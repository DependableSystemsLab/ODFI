import os
import shutil
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

import unittest

TRAIN_IMAGES_DIRECTORY = "/home/abraham/ODFI/data/cocotraffic-sample/train_images" # Point this to your training image directory (absolute path required)
TRAIN_ANNOTATIONS_PATH = "/home/abraham/ODFI/data/cocotraffic-sample/train_annotations.json" # Point this to your annotation JSON file (absolute path required)

INTERACTIVE = True # Set True to see interactive demo


def load_coco(annotation_file, train_images_path=TRAIN_IMAGES_DIRECTORY):
    coco_annotation = COCO(annotation_file=annotation_file)
    cocoextra = COCOExtra(coco_ann=coco_annotation, train_images_path=train_images_path)
    return coco_annotation, cocoextra

class InjectionPerImageTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.orig_coco_ann, cls.orig_cocoextra = load_coco(TRAIN_ANNOTATIONS_PATH)
        img_ids = cls.orig_coco_ann.getImgIds()

        cls.test_image_id1 = 268342 # Image with two annotations: two traffic lights
        cls.test_image_id2 = 221190 # Image with three annotations: train, two traffic lights

        cls.before_ann_ids1 = cls.orig_coco_ann.getAnnIds(imgIds=[cls.test_image_id1])
        cls.before_anns1 = cls.orig_coco_ann.loadAnns(cls.before_ann_ids1)

        cls.interactive = INTERACTIVE
        cls.__createTestFolder()

    def setUp(self):
        self.coco_ann, self.cocoextra = load_coco(TRAIN_ANNOTATIONS_PATH)
        self.anns = self.coco_ann.anns

    def test_mislabel_cat(self):
        self.final_fault = "mislabel_cat-100-1"
        self.__inject()
        injected_ann_ids1 = self.selected_img_ann_ids[self.test_image_id1]

        after_ann_ids1 = self.coco_ann.getAnnIds(imgIds=[self.test_image_id1])
        after_anns1 = self.coco_ann.loadAnns(after_ann_ids1)

        self.assertEqual(len(self.before_ann_ids1), len(after_ann_ids1))
        self.assertEqual(len(injected_ann_ids1), 1)

        before_anns1 = self.orig_coco_ann.loadAnns(injected_ann_ids1)
        injected_anns1 = self.coco_ann.loadAnns(injected_ann_ids1)
        self.assertNotEqual(before_anns1[0]['category_id'], injected_anns1[0]['category_id'])

    def test_mislabel_super(self):
        self.final_fault = "mislabel_super-100-1"
        self.__inject()
        injected_ann_ids1 = self.selected_img_ann_ids[self.test_image_id1]

        after_ann_ids1 = self.coco_ann.getAnnIds(imgIds=[self.test_image_id1])
        after_anns1 = self.coco_ann.loadAnns(after_ann_ids1)

        self.assertEqual(len(self.before_ann_ids1), len(after_ann_ids1))
        self.assertEqual(len(injected_ann_ids1), 1)

        before_anns1 = self.orig_coco_ann.loadAnns(injected_ann_ids1)
        injected_anns1 = self.coco_ann.loadAnns(injected_ann_ids1)

        orig_cat_id1 = before_anns1[0]['category_id']
        query_annotation = self.coco_ann.loadCats([orig_cat_id1])[0]
        query_supercategory = query_annotation['supercategory']
        related_cat_ids1 = self.coco_ann.getCatIds(supNms=[query_supercategory])

        self.assertNotIn(injected_anns1[0]['category_id'], related_cat_ids1)

    def test_incorrect_bb(self):
        self.final_fault = "incorrect_bb-100-1"
        self.__inject()
        injected_ann_ids1 = self.selected_img_ann_ids[self.test_image_id1]

        after_ann_ids1 = self.coco_ann.getAnnIds(imgIds=[self.test_image_id1])
        after_anns1 = self.coco_ann.loadAnns(after_ann_ids1)

        self.assertEqual(len(self.before_ann_ids1), len(after_ann_ids1))
        self.assertEqual(len(injected_ann_ids1), 1)

        before_anns1 = self.orig_coco_ann.loadAnns(injected_ann_ids1)
        injected_anns1 = self.coco_ann.loadAnns(injected_ann_ids1)
        self.assertNotEqual(before_anns1[0]['bbox'], injected_anns1[0]['bbox'])

    def test_redundant_ann(self):
        self.final_fault = "redundant_ann-100-1"
        self.__inject()

        # Modified annotation filename
        modified_json_fname = "./injected/coco-" + self.final_fault + ".json"

        self.cocoextra.save_ann(modified_json_fname)
        coco_ann, self.cocoextra = load_coco(modified_json_fname)

        after_ann_ids1 = coco_ann.getAnnIds(imgIds=[self.test_image_id1])
        after_anns1 = coco_ann.loadAnns(after_ann_ids1)

        self.assertEqual(len(self.before_ann_ids1) + 1, len(after_ann_ids1))

    def test_remove_ann(self):
        self.final_fault = "remove_ann-100-1"
        self.__inject()

        # Modified annotation filename
        modified_json_fname = "./injected/coco-" + self.final_fault + ".json"

        self.cocoextra.save_ann(modified_json_fname)
        coco_ann, self.cocoextra = load_coco(modified_json_fname)

        after_ann_ids1 = coco_ann.getAnnIds(imgIds=[self.test_image_id1])
        after_anns1 = coco_ann.loadAnns(after_ann_ids1)

        self.assertEqual(len(self.before_ann_ids1) - 1, len(after_ann_ids1))

    def tearDown(self):
        if self.interactive:
            print(f"Image Key: {self.test_image_id1}")
            self.orig_cocoextra.ann_on_image(self.test_image_id1, window_title="Before")
            self.cocoextra.ann_on_image(self.test_image_id1, modified_ann_ids=self.selected_img_ann_ids[self.test_image_id1], window_title="After " + self.final_fault)

    def __inject(self):
        conf_file = "./confFiles/" + self.final_fault + ".yaml"
        self.selected_img_ann_ids = odfi.inject(coco_ann=self.coco_ann, confFile=conf_file)

    @classmethod
    def tearDownClass(cls):
        cls.__deleteTestFolder()

    @classmethod
    def __createTestFolder(cls):
        testfolder = "./injected"
        if not os.path.exists(testfolder):
            os.makedirs(testfolder)

    @classmethod
    def __deleteTestFolder(cls):
        testfolder = "./injected"
        if os.path.exists(testfolder):
            shutil.rmtree(testfolder)

if __name__ == "__main__":
    unittest.main()

