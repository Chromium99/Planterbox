1. Install Requirements
Clone the repo
git clone <your_repo_url>
cd Planterbox

Create a virtual environment

Windows:

python -m venv venv
.\venv\Scripts\activate


Mac/Linux:

python3 -m venv venv
source venv/bin/activate

Install dependencies
pip install -r requirements.txt

2. Project Folder Structure

Your directory must look like this:

Planterbox/
│
├── data/
│   ├── species/
│   │     ├── Aloe Vera/
│   │     ├── Orchid/
│   │     ├── Peace Lily/
│   │     └── ... (47 total species)
│   │
│   └── splits/
│         ├── train/
│         ├── val/
│         └── test/
│
├── models/
│   └── species/
│         ├── experiments/
│         │      ├── baseline224/
│         │      ├── ft224/
│         │      ├── ft224_cw/
│         │      ├── ft256_cw/
│         │
│         ├── release/
│         │      ├── model.tflite
│         │      ├── labels.txt
│         │
│         └── meta/
│                └── class_names.json
│
├── predictions_out/
│
├── src/
│   ├── train_mobilenet_v3.py
│   ├── predict_annotate.py
│   └── clean_images.py
│
└── README.md

3. Preparing the Dataset
3.1 Add raw species images

Download the Kaggle houseplant dataset and place all species folders into:

Planterbox/data/species/

3.2 Clean corrupted/alpha-channel images

This converts everything to RGB JPG:

python .\src\clean_images.py

3.3 Rebuild train/val/test splits (optional)

If you want a fresh split:

Remove-Item .\data\splits -Recurse -Force


The training script will recreate splits automatically if missing.

4. Training the Model

Run:

python .\src\train_mobilenet_v3.py


This script:

Loads ~14,700 plant images

Creates an 80/10/10 train/val/test split

Trains several MobileNetV3 variants

Saves best model weights to:

models/species/experiments/<variant>/best.keras


Exports a TFLite model to:

models/species/release/model.tflite

Best-performing model
ft224_cw


(“Fine-tuned at 224px with class weights”)

5. Running Predictions

Run inference on an image or entire folder:

python .\src\predict_annotate.py "<path_to_image_or_folder>"


This script:

Loads your trained model

Performs species prediction

Writes annotated images to:

Planterbox/predictions_out/


Example annotation:

Aloe Vera (1.00)
Orchid (0.00)
Snake Plant (0.00)

6. Model Variants
Variant	Description
baseline224	224px, no fine-tuning
ft224	fine-tuned layers
ft224_cw	fine-tuned + class weights (BEST)
ft256_cw	256px resolution, slightly better but slower

Selected model for deployment:

ft224_cw

7. Deploying to Mobile (Planterbox App)

Use these files:

models/species/release/model.tflite
models/species/release/labels.txt


Make sure the mobile app applies the same preprocessing:

Resize to 224×224

Scale pixels to [-1, 1]

8. Team Summary

Each team member can:

Train new model variants

Run inference locally

Generate annotated prediction examples

Analyze model performance

Integrate the .tflite model into the app

Modify and extend the training pipeline
