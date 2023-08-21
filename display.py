import argparse
from pycocotools.coco import COCO

from cocoextra import COCOExtra

import json

parser = argparse.ArgumentParser()

parser.add_argument('-a', '--ann_json', dest='train_ann_json', required = True,
                    help='Path to training annotations JSON file')

parser.add_argument('-i', '--images_path', dest='train_images_path', required = True,
                    help='Path to training images directory')

parser.add_argument('-o', '--output', dest='injected_ann_json', required = True,
                    help='Path to post-injection annotation JSON file')

parser.add_argument('-c', '--change_file', dest='change_file', required = True,
                    help='Path to file listing changed images and annotations')


def load_coco(annotation_file, train_images_path):
    coco_annotation = COCO(annotation_file=annotation_file)
    cocoextra = COCOExtra(coco_ann=coco_annotation, train_images_path=train_images_path)
    return coco_annotation, cocoextra

def main():
    args = parser.parse_args()

    coco_annotation_orig, cocoextra_orig = load_coco(args.train_ann_json, args.train_images_path)
    coco_annotation_injected, cocoextra_injected = load_coco(args.injected_ann_json, args.train_images_path)

    with open(args.change_file, "r") as outfile:
        selected_img_ann_ids = json.load(outfile)

    for image_id in selected_img_ann_ids:
        image_id_int = int(image_id)
        cocoextra_injected.ann_on_image_sidebyside(image_id_int, coco_annotation_orig, modified_ann_ids=selected_img_ann_ids[image_id], window_title="Before-After on: " + image_id)

    return

if __name__ == "__main__":
    main()

