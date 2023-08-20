import argparse
from pycocotools.coco import COCO

import odfi
from cocoextra import COCOExtra


parser = argparse.ArgumentParser()

parser.add_argument('-a', '--ann_json', dest='train_ann_json', required = True,
                    help='Path to training annotations JSON file')

parser.add_argument('-i', '--images_path', dest='train_images_path', required = True,
                    help='Path to training images directory')

parser.add_argument('-y', '--odfi_yaml', dest='odfi_yaml', required = True,
                    help='Path to ODFI YAML file')

parser.add_argument('-o', '--output', dest='injected_ann_json',
                    help='Path to post-injection annotation JSON file')


def load_coco(annotation_file, train_images_path):
    coco_annotation = COCO(annotation_file=annotation_file)
    cocoextra = COCOExtra(coco_ann=coco_annotation, train_images_path=train_images_path)
    return coco_annotation, cocoextra

def main():
    args = parser.parse_args()

    if not args.injected_ann_json:
        args.injected_ann_json = args.odfi_yaml.split("/")[-1].split(".yaml")[0] + ".json"

    coco_annotation, cocoextra = load_coco(args.train_ann_json, args.train_images_path)

    selected_img_ann_ids = odfi.inject(coco_ann=coco_annotation, confFile=args.odfi_yaml)
    cocoextra.save_ann(args.injected_ann_json)
    return

if __name__ == "__main__":
    main()

