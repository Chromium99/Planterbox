 HOW TO RUN THE CODE
 You should have these four Python files in the src folder:

clean_images.py

exp_mbv3.py

predict_annotate.py

train_mobilenet_v3.py

You should also have a data folder and a models folder at the root of the project.

SETUP ON YOUR COMPUTER
=========================

Make sure you have Python 3 installed.

Open a terminal (PowerShell on Windows, Terminal on Mac/Linux).

Go to the project folder, for example:

cd C:\Users<your_name>\Documents\Planterbox

Create a virtual environment:

On Windows:
python -m venv venv
.\venv\Scripts\activate

On Mac/Linux:
python3 -m venv venv
source venv/bin/activate

Install the required Python packages:
pip install -r requirements.txt

After this, you are ready to run the scripts.

FOLDER STRUCTURE YOU SHOULD HAVE
====================================

Your project should roughly look like this:

Planterbox/
data/
species/ (raw images, one subfolder per plant species)
splits/ (will be created automatically by the training/experiment code)
models/
species/
experiments/ (will be created and filled by training/experiments)
release/ (final model for deployment)
meta/ (class_names.json etc., depending on how the scripts are set up)
predictions_out/ (will be created by predict_annotate.py)
src/
clean_images.py
exp_mbv3.py
predict_annotate.py
train_mobilenet_v3.py
README or other files

Important:

data/species must contain one folder per plant species, with images inside each.

data/splits will be created automatically if it doesn’t exist.

WHAT EACH PYTHON FILE DOES
=============================

clean_images.py

Purpose:

This script goes through your image folders and makes sure all images are in a consistent format (for example, converts RGBA PNGs with transparency to normal RGB JPGs, and may skip or clean corrupted images).

What it is used for:

It prevents training crashes caused by weird image formats (like images with 4 channels or grayscale).

It is usually run once after you download or move a new dataset into data/species.

How to run it:

Make sure your virtual environment is active.

Make sure your raw images are inside data/species/<species_name>.

From the root project folder run:
python src/clean_images.py

What happens:

It will scan through the target folders defined inside the script (commonly data/species and sometimes data/splits).

It will convert or fix images so that all of them are safe to feed into the model.

If something breaks:

Check the console output to see which file caused the issue.

Remove or replace any truly corrupted images.

exp_mbv3.py

Purpose:

This is the “experiment” script for training multiple versions of MobileNetV3.

It lets you easily run different configurations (baseline, fine-tuned, with class weights, with different image sizes, etc.) and saves metrics for comparison.

What it is used for:

Running comparisons between:

baseline224

ft224

ft224_cw

ft256_cw

Producing summary files (like JSON and CSV/Excel) you can use in your presentation to show accuracy and macro F1 scores.

How to run a basic experiment:

Activate your virtual environment.

Go to the project root.

Run something like:
python src/exp_mbv3.py --tag baseline224

Common flags (depending on how it was set up in your version):

--img 224 or 256 (input image size)

--finetune (turn on fine-tuning of top layers)

--class_weight (use class weights for imbalanced classes)

--freeze_bn (freeze batch normalization layers when fine-tuning)

--tag NAME (name the run, used as folder name in models/species/experiments)

Example runs:

Baseline:
python src/exp_mbv3.py --tag baseline224

Fine-tuned:
python src/exp_mbv3.py --finetune --freeze_bn --tag ft224

Fine-tuned + class weights:
python src/exp_mbv3.py --finetune --freeze_bn --class_weight --tag ft224_cw

What happens:

The script loads images from data/splits/train, /val, and /test.

If splits do not exist yet, usually you should run train_mobilenet_v3.py once to create them.

It trains a model using the chosen options.

It saves:

best.keras (the best Keras model)

model.tflite (a TFLite version for mobile)

summary and report files (accuracy, macro F1, per-class metrics)
under models/species/experiments/<tag>.

train_mobilenet_v3.py

Purpose:

This is the main training pipeline script for your project, often focused on the final chosen configuration (for example, ft224_cw).

It handles:

Creating the train/val/test splits (if they don’t exist)

Building the MobileNetV3 model

Training it

Saving the main model and TFLite export

Typical usage:

Run this once to set up and train your main model:
python src/train_mobilenet_v3.py

What it does step by step:

Checks data/species for all species folders and images.

If data/splits does not exist, it randomly splits the data into:

train (80%)

val (10%)

test (10%)

Builds a MobileNetV3-based classifier with the correct input size (usually 224x224) and number of classes.

Applies data augmentation and proper preprocessing (such as scaling pixels to [-1, 1]).

Trains the model for a certain number of epochs.

Sometimes (depending on the code) it does a second phase of training where it unfreezes part of the backbone (fine-tuning).

Saves:

The best Keras model (best.keras)

A TFLite model (model.tflite), often in models/species/release/

Optional summary/metrics files (JSON or CSV) used for reporting.

Use this script when:

You or a teammate wants to retrain the main model from scratch.

You change the dataset and want an updated model.

You want a simple, default way to reproduce the final model without messing with experimental flags.

predict_annotate.py

Purpose:

This script is used to test the trained model on real images.

It loads the trained model and labels, runs prediction on one image or a folder of images, and saves new copies with the predicted plant name written on top.

How to run it:

Make sure you have already trained a model (for example ft224_cw) and it is saved in models/species/experiments/<variant>/best.keras.

Make sure you have labels.txt generated (or the script loads class names from meta/class_names.json).

Activate the virtual environment.

From the project root, run:
python src/predict_annotate.py "PATH_TO_IMAGE_OR_FOLDER"

Examples:

Single image:
python src/predict_annotate.py "C:\Users\you\Pictures\plant.jpg"

Folder of images:
python src/predict_annotate.py "C:\Users\you\Pictures\plants_to_test"

What happens:

The script loads the Keras model (best.keras) for the chosen variant (e.g., ft224_cw).

It reads the labels in the same order as the model’s outputs.

For each image:

It resizes it to the correct input size (e.g., 224x224).

It applies the same preprocessing as training (e.g., MobileNetV3’s preprocess_input).

It runs the model to get probabilities for all species.

It finds the top-k predictions (usually top 3).

It opens the original image, draws a black rectangle at the top, and writes:
SpeciesName1 (probability)
SpeciesName2 (probability)
SpeciesName3 (probability)

It saves the annotated image into the predictions_out folder with a new filename like originalname_pred.jpg.

This is what you use when you want to:

Show that the model works on real photos.

Create example images for your presentation.

Let teammates quickly test the model on their own plant photos.

TYPICAL WORKFLOW FOR A TEAMMATE
==================================

Here is a simple step-by-step list your groupmates can follow on their own machine:

Clone the repository and go into the Planterbox folder.

Create and activate a virtual environment.

Install dependencies using:
pip install -r requirements.txt

Make sure the dataset is in the correct place:

All species folders are in data/species.

Run the cleaning script:
python src/clean_images.py

Train the main model:

Either run the standard training script:
python src/train_mobilenet_v3.py

Or run the experiment script with desired options, for example:
python src/exp_mbv3.py --finetune --freeze_bn --class_weight --tag ft224_cw

Once training finishes, test the model on some images:
python src/predict_annotate.py "path_to_image_or_folder"

Open the predictions_out folder and look at the annotated images to see what the model predicted.
