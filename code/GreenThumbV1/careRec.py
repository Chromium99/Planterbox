from google import genai
from google.genai import types
import json
import re
from PIL import Image
import matplotlib.pyplot as plt
import pandas as pd
from tensorflow import keras
from tensorflow.keras.applications.mobilenet_v3 import preprocess_input
import numpy as np
from pathlib import Path

MODEL_PATH = "/content/models/species/experiments/ft224_cw/best.keras"
LABELS_PATH = "/content/models/species/release/labels.txt"

species_model = keras.models.load_model(
    MODEL_PATH,
    custom_objects={"preprocess_input": preprocess_input},
    compile=False
)

labels = [l.strip() for l in open(LABELS_PATH).read().splitlines()]
H, W = species_model.input_shape[1:3]

def detect_species(img_path):
    img = keras.utils.load_img(img_path, target_size=(H, W))
    x = keras.utils.img_to_array(img)
    x = preprocess_input(x)[None, ...].astype("float32")
    probs = species_model.predict(x, verbose=0)[0]

    idx = int(np.argmax(probs))
    return labels[idx], float(probs[idx])

client = genai.Client(api_key="")

# Load CSV keywords & care data
df = pd.read_csv("/content/plants.csv", encoding="latin1")

def load_keywords_for_species(species_name):
    row = df[df["Plant Name"].str.lower() == species_name.lower()]
    if row.empty:
        return set()

    row = row.iloc[0]
    keywords = set()

    for col in df.columns:
        if col == "Plant Name":
            continue
        val = row[col]
        if pd.isna(val):
            continue

        text = str(val).lower().replace("-", " ").replace("/", " ")
        for word in text.split():
            keywords.add(word.strip())

    return keywords

def get_care_data(species_name):
    row = df[df["Plant Name"].str.lower() == species_name.lower()]
    if row.empty:
        return None
    return row.iloc[0].to_dict()

# Model prompt
def model_prompt(species_name, image_path):

    care_info = get_care_data(species_name)
    if care_info is None:
        print(f"Species '{species_name}' not found in CSV.")
        return

    # Load image
    img = Image.open(image_path)
    plt.imshow(img)
    plt.axis("off")
    plt.show()

    # Prompt combining both tasks
    prompt = f"""
    You are a plant diagnosis and care assistant.

    The user provides:
    1. An image of a plant
    2. The species name: "{species_name}"

    Your job is to produce ONE FINAL JSON OUTPUT with:

    {{
      "validated_species": "",
      "visible_symptoms": [],
      "likely_causes": [],
      "care_recommendations": "",
      "urgency_level": "low | medium | high"
    }}

    CARE RECOMMENDATIONS MUST INCLUDE:

    1. Growth rate (slow, moderate, fast)
    2. Soil type (well-drained, sandy, loamy, acidic)
    3. Sunlight requirement (full sunlight, indirect sunlight, partial sunlight)
    4. Watering frequency (water weekly, keep soil evenly moist, let soil dry between watering, keep soil slightly moist,
    keep soil consistently moist, water when soil is dry, water when topsoil is dry, water when soil feels dry)
    5. Fertilization type (balanced, acidic, low-nitrogen, organic, no)

    Additional instructions:
    - Analyze the plant image to identify symptoms.
    - Tailor recommendations to both species and symptoms.
    - Make all recommendations accurate, and concise.
    - Keep the information short (a couple of sentences).
    - Output ONLY the JSON. No markdown or commentary.
    """

    # Model call
    response = client.models.generate_content(
        model="gemini-2.5-flash",
        contents=[img, prompt]
    )

    raw = response.text.strip()

    # Clean JSON
    raw = re.sub(r"```json|```", "", raw).strip()

    try:
        diagnostic = json.loads(raw)
    except:
        diagnostic = {"error": "Invalid JSON returned.", "raw_output": raw}
        
    return diagnostic

def process_plant(image_path, species_name=None):

    # Auto-detect species if missing
    if species_name is None:
        species_name, confidence = detect_species(image_path)
        print(f"[Auto-detected species] {species_name} ({confidence:.2f})")

    # Get Gemini diagnosis + care
    diagnostic = model_prompt(species_name, image_path)

    if diagnostic is None:
        return None

    # Keyword match evaluation
    keywords = load_keywords_for_species(species_name)

    if "care_recommendations" in diagnostic:
        care_text = diagnostic["care_recommendations"].lower()
        matched = [kw for kw in keywords if kw in care_text]
        total = len(keywords)
        found = len(matched)
        percentage = (found / total * 100) if total > 0 else 0
    else:
        matched = []
        percentage = 0

    result = {
        "species_detected": species_name,
        "gemini_result": diagnostic,
        "keyword_match_score": round(percentage, 2),
        "keywords_matched": matched,
    }

    return result