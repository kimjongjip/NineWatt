# -*- coding: utf-8 -*-
"""fine-tune-sam-2.1.ipynb

Automatically generated by Colab.

Original file is located at
    https://colab.research.google.com/github/roboflow-ai/notebooks/blob/add-fine-tune-sam-2.1/notebooks/fine-tune-sam-2.1.ipynb

[![Roboflow Notebooks](https://media.roboflow.com/notebooks/template/bannertest2-2.png?ik-sdk-version=javascript-1.4.3&updatedAt=1672932710194)](https://github.com/roboflow/notebooks)

# Fine-Tune Segment Anything 2.1 (SAM-2.1)

---

[![GitHub](https://badges.aleen42.com/src/github.svg)](https://github.com/facebookresearch/sam2)

Segment Anything Model is a computer vision from Meta AI that can "cut out" any object, in any image, with a single click.

In September 2024, Meta Research released SAM-2.1 SAM-2.1 is the latest model in the Segment Anything model series. When evaluated against the Segment Anything V test set, the MOSE validation set, and the LVOSv2 dataset, all SAM-2.1 model sizes perform better than SAM-2.

SAM-2.1 was released with training instructions that you can use to fine-tune SAM-2.1 for a specific use case. This is ideal if you want to train SAM-2.1 to segment objects in a specific domain at which the base model struggles.

Here is an example of results from SAM-2, sourced from the Meta SAM-2 GitHub repository:

![segment anything model](https://github.com/facebookresearch/sam2/raw/main/assets/sa_v_dataset.jpg?raw=true)

We recommend that you follow along in this notebook while reading the blog post on [SAM-2.1 fine-tuning](https://blog.roboflow.com/sam-2-1-fine-tuning).

## Pro Tip: Use GPU Acceleration

If you are running this notebook in Google Colab, navigate to `Edit` -> `Notebook settings` -> `Hardware accelerator`, set it to `GPU`, and then click `Save`. This will ensure your notebook uses a GPU, which will significantly speed up model training times.

Meta recommends training SAM-2.1 on an A100. Thus, if possible, select an A100 GPU in Google Colab for use in training the model.

## Steps in this Tutorial

In this tutorial, we are going to cover:

- **Before you start** - Make sure you have access to the GPU
- Download SAM-2.1
- Download Example Data
- Load Model
- Automated Mask Generation

Without further ado, let's get started!

## Download SAM-2.1 and Data

Below, we download SAM-2.1 from GitHub, then download a dataset for use in training. You will need a dataset structured in the correct format for SAM-2.1.

Roboflow supports exporting segmentation datasets to the SAM-2.1 format, ideal for use in this guide. You can upload segmentation datasets in the COCO JSON Segmentation format then convert them to SAM-2.1 for use in this guide.

[Learn how to label a dataset in Roboflow](https://blog.roboflow.com/getting-started-with-roboflow/)

[Learn how to export data from Roboflow for training](https://docs.roboflow.com/datasets/exporting-data).

![Export as SAM-2 data](https://media.roboflow.com/sam2export.png)

We then download a SAM-2.1 training YAML file which we will use to configure our model training job.

Finally, we install SAM-2.1 and download the model checkpoints.

Replace the below code with the code to export your dataset. You can also use the same code above to fine-tune our car parts dataset. _Note: If you use the car parts dataset pre-filled below, you will still need to add a [Roboflow API key](https://docs.roboflow.com/api-reference/authentication#retrieve-an-api-key)._

**Important ⚠️: You must generate a dataset with images stretched to 1024x1024 for training. This is because our training configuration is set to use images of this resolution.**
"""

!pip install roboflow

from roboflow import Roboflow
import os

rf = Roboflow(api_key="W8Wh3vwPre13GJ9ArQue")
project = rf.workspace("brad-dwyer").project("car-parts-pgo19")
version = project.version(6)
dataset = version.download("sam2")

# rename dataset.location to "data"
os.rename(dataset.location, "/content/data")

!git clone https://github.com/facebookresearch/sam2.git

!wget -O /content/sam2/sam2/configs/train.yaml 'https://drive.usercontent.google.com/download?id=11cmbxPPsYqFyWq87tmLgBAQ6OZgEhPG3'

# Commented out IPython magic to ensure Python compatibility.
# %cd ./sam2/

"""Next, we are going to install SAM-2.

The SAM-2 installation process may take several minutes.
"""

!pip install -e .[dev] -q

!cd ./checkpoints && ./download_ckpts.sh

"""## Modify Dataset File Names

SAM-2.1 requires dataset file names to be in a particular format. Run the code snippet below to format your dataset file names as required.
"""

# Script to rename roboflow filenames to something SAM 2.1 compatible.
# Maybe it is possible to remove this step tweaking sam2/sam2/configs/train.yaml.
import os
import re

FOLDER = "/content/data/train"

for filename in os.listdir(FOLDER):
    # Replace all except last dot with underscore
    new_filename = filename.replace(".", "_", filename.count(".") - 1)
    if not re.search(r"_\d+\.\w+$", new_filename):
        # Add an int to the end of base name
        new_filename = new_filename.replace(".", "_1.")
    os.rename(os.path.join(FOLDER, filename), os.path.join(FOLDER, new_filename))

"""## Start Training

You can now start training a SAM-2.1 model. The amount of time it will take to train the model will vary depending on the GPU you are using and the number of images in your dataset.

For the car part dataset of 38 images, training on an A100 GPU takes ~15 minutes.
"""

!python training/train.py -c 'configs/train.yaml' --use-cluster 0 --num-gpus 1

"""You can visualize the model training graphs with Tensorboard:"""

# Commented out IPython magic to ensure Python compatibility.
# %load_ext tensorboard
# %tensorboard --bind_all --logdir ./sam2_logs/

"""## Visualize Model Results

With a trained model ready, we can test the model on an image from our test set.

To assist with visualizing model predictions, we are going to use Roboflow supervision, an open source computer vision Python package with utilities for working with vision model outputs

"""

!pip install supervision -q

"""### Load SAM-2.1"""

import torch
from sam2.build_sam import build_sam2
from sam2.automatic_mask_generator import SAM2AutomaticMaskGenerator
import supervision as sv
import os
import random
from PIL import Image
import numpy as np

# use bfloat16 for the entire notebook
# from Meta notebook
torch.autocast("cuda", dtype=torch.bfloat16).__enter__()
if torch.cuda.get_device_properties(0).major >= 8:
    torch.backends.cuda.matmul.allow_tf32 = True
    torch.backends.cudnn.allow_tf32 = True

checkpoint = "/content/sam2/sam2_logs/configs/train.yaml/checkpoints/checkpoint.pt"
model_cfg = "configs/sam2.1/sam2.1_hiera_b+.yaml"
sam2 = build_sam2(model_cfg, checkpoint, device="cuda")
mask_generator = SAM2AutomaticMaskGenerator(sam2)

checkpoint_base = "/content/sam2/checkpoints/sam2.1_hiera_base_plus.pt"
model_cfg_base = "configs/sam2.1/sam2.1_hiera_b+.yaml"
sam2_base = build_sam2(model_cfg_base, checkpoint_base, device="cuda")
mask_generator_base = SAM2AutomaticMaskGenerator(sam2_base)

"""### Run Inference on an Image in Automatic Mask Generation Mode"""

validation_set = os.listdir("/content/data/valid")

# choose random with .json extension
image = random.choice([img for img in validation_set if img.endswith(".jpg")])
image = os.path.join("/content/data/valid", image)
opened_image = np.array(Image.open(image).convert("RGB"))
result = mask_generator.generate(opened_image)

detections = sv.Detections.from_sam(sam_result=result)

mask_annotator = sv.MaskAnnotator(color_lookup = sv.ColorLookup.INDEX)
annotated_image = opened_image.copy()
annotated_image = mask_annotator.annotate(annotated_image, detections=detections)

base_annotator = sv.MaskAnnotator(color_lookup = sv.ColorLookup.INDEX)

base_result = mask_generator_base.generate(opened_image)
base_detections = sv.Detections.from_sam(sam_result=base_result)
base_annotated_image = opened_image.copy()
base_annotated_image = base_annotator.annotate(base_annotated_image, detections=base_detections)

sv.plot_images_grid(images=[annotated_image, base_annotated_image], titles=["Fine-Tuned SAM-2.1", "Base SAM-2.1"], grid_size=(1, 2))

"""## 🏆 Congratulations

### Learning Resources

Roboflow has produced many resources that you may find interesting as you advance your knowledge of computer vision:

- [Roboflow Notebooks](https://github.com/roboflow/notebooks): A repository of over 20 notebooks that walk through how to train custom models with a range of model types, from YOLOv7 to SegFormer.
- [Roboflow YouTube](https://www.youtube.com/c/Roboflow): Our library of videos featuring deep dives into the latest in computer vision, detailed tutorials that accompany our notebooks, and more.
- [Roboflow Discuss](https://discuss.roboflow.com/): Have a question about how to do something on Roboflow? Ask your question on our discussion forum.
- [Roboflow Models](https://roboflow.com): Learn about state-of-the-art models and their performance. Find links and tutorials to guide your learning.

### Convert data formats

Roboflow provides free utilities to convert data between dozens of popular computer vision formats. Check out [Roboflow Formats](https://roboflow.com/formats) to find tutorials on how to convert data between formats in a few clicks.

### Connect computer vision to your project logic

[Roboflow Templates](https://roboflow.com/templates) is a public gallery of code snippets that you can use to connect computer vision to your project logic. Code snippets range from sending emails after inference to measuring object distance between detections.
"""