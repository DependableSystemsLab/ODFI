import os
import numpy as np
import matplotlib.pyplot as plt
from PIL import Image
import skimage.io as io
import requests
from pycocotools.coco import COCO
import random
import json

import sys
sys.path.insert(0, "..")

import odfi
from cocoextra import COCOExtra


TRAIN_IMAGES_DIRECTORY = "" # Point this to your training image directory
TRAIN_ANNOTATIONS_PATH = "" # Point this to your annotation JSON file


def load_coco(annotation_file, train_images_path=TRAIN_IMAGES_DIRECTORY):
    coco_annotation = COCO(annotation_file=annotation_file)
    cocoextra = COCOExtra(coco_ann=coco_annotation, train_images_path=train_images_path)
    return coco_annotation, cocoextra

def main():
    coco_annotation, cocoextra = load_coco(TRAIN_ANNOTATIONS_PATH)

    final_fault = "mislabel_cat-10"
    #final_fault = "remove_ann-10"
    #final_fault = "mislabel_super-10"
    #final_fault = "incorrect_bb-10"
    #final_fault = "redundant_ann-10"

    conf_file = "./confFiles/" + final_fault + ".yaml"

    selected_img_ann_ids = odfi.inject(coco_ann=coco_annotation, confFile=conf_file)
    keys = list(selected_img_ann_ids.keys())

    #Modified annotation filename
    modified_json_fname = "coco-" + final_fault + ".json"

    # Reload COCO with injected dataset
    cocoextra.save_ann(modified_json_fname)
    coco_annotation, cocoextra = load_coco(modified_json_fname)

    random_key = random.choice(keys)
    print(f"Random Key: {random_key}")
    cocoextra.ann_on_image(random_key, modified_ann_ids=selected_img_ann_ids[random_key])

    return


if __name__ == "__main__":
    main()

