import os
import numpy as np
import matplotlib.pyplot as plt
from PIL import Image
import skimage.io as io
from pycocotools.coco import COCO
import json

# Extra utility COCO functions, not included in the default API
class COCOExtra:
    def __init__(self, coco_ann, train_images_path):
        self.coco_ann = coco_ann
        self.train_images_path = train_images_path

    # Overlay annotated category text directly on images
    def ann_on_image(self, img_id, modified_ann_ids=None, save_fig=False, window_title=""):
        coco_ann = self.coco_ann
        img_info = coco_ann.loadImgs([img_id])[0]
        img_file_name = img_info["file_name"]
        image_path = os.path.join(self.train_images_path, img_file_name)
        im = io.imread(image_path)

        fig, ax = plt.subplots()
        fig.canvas.set_window_title(window_title)
        ax.axis("off")
        ax.imshow(np.asarray(im))

        ann_ids = coco_ann.getAnnIds(imgIds=[img_id], iscrowd=None)
        anns = coco_ann.loadAnns(ann_ids)

        coco_ann.showAnns(anns, draw_bbox=True)

        cat_ids = coco_ann.getCatIds()

        for i, ann in enumerate(anns):
            entity_id = anns[i]["category_id"]

            if entity_id not in cat_ids:
                continue

            entity = coco_ann.loadCats(entity_id)[0]["name"]

            if modified_ann_ids and anns[i]["id"] in modified_ann_ids:
                facecolor = 'red'
            else:
                facecolor = 'white'

            ax.text(anns[i]['bbox'][0], anns[i]['bbox'][1], entity, style='italic',
                    bbox={'facecolor': facecolor, 'alpha': 0.7, 'pad': 5})

        if save_fig:
            if modified_ann_ids:
                plt.savefig(f"{img_id}_annotated_injected.jpg", bbox_inches="tight", pad_inches=0)
            else:
                plt.savefig(f"{img_id}_annotated.jpg", bbox_inches="tight", pad_inches=0)
        else:
            plt.show()


    # Display image by image id
    def show_img(self, img_id, save_fig=False):
        coco_ann = self.coco_ann
        img_info = coco_ann.loadImgs([img_id])[0]
        img_file_name = img_info["file_name"]
        image_path = os.path.join(self.train_images_path, img_file_name)
        im = io.imread(image_path)

        plt.axis("off")
        plt.imshow(np.asarray(im))

        if save_fig:
            plt.savefig(f"{img_id}.jpg", bbox_inches="tight", pad_inches=0)
        else:
            plt.show()


    # Save modified annotation file
    def save_ann(self, filename):
        with open(filename, "w") as outfile:
            json.dump(self.coco_ann.dataset, outfile, indent=4)


    # Get dict: {supercategory: [category_ids]}
    def get_supercat_dict(self):
        coco_ann = self.coco_ann
        allcats = coco_ann.cats
        result = {}

        for catId, cat in allcats.items():
            supercat = cat["supercategory"]
            if not supercat:
                raise ValueError("Dataset has no supercategories!")
            if supercat not in result:
                result[supercat] = []

            result[supercat].append(catId)
        return result

