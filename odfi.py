#!/usr/bin/python

import tensorflow as tf

import numpy as np
import random, math

import yaml, sys
import copy

def config(confFile):
    try:
        fiConfs = open(confFile, "r")
    except:
        print("Unable to find/open the config file in:", confFile)
        print("Make sure the correct path is passed to the inject call.")
        sys.exit()
    if(confFile.endswith(".yaml")):
        fiConf = yaml.safe_load(fiConfs)
    else:
        print("Unsupported file format:", confFile)
        sys.exit()
    fiConfs.close()
    return fiConf

def inject(confFile="confFiles/sample.yaml", **kwargs):
    fiConf = config(confFile)
    fiFunc = globals()[fiConf["Type"]]
    return fiFunc(fiConf, **kwargs)

def redundant_ann(fiConf, **kwargs):
    return inject_images(fiConf["Type"], fiConf, **kwargs)

def remove_ann(fiConf, **kwargs):
    return inject_images(fiConf["Type"], fiConf, **kwargs)

def mislabel_cat(fiConf, **kwargs):
    return inject_images(fiConf["Type"], fiConf, **kwargs)

def mislabel_super(fiConf, **kwargs):
    return inject_images(fiConf["Type"], fiConf, **kwargs)

def incorrect_bb(fiConf, **kwargs):
    return inject_images(fiConf["Type"], fiConf, **kwargs)

def inject_images(fault_type, fiConf, **kwargs):

    coco_ann = kwargs["coco_ann"]
    anns = coco_ann.anns
    ann_ids = coco_ann.getAnnIds()
    img_ids = coco_ann.getImgIds()

    doInjectionByImg = True if "Injections_Per_Image" in fiConf else False

    if doInjectionByImg:
        injections_per_image = fiConf["Injections_Per_Image"]
        num = len(img_ids)
    else:
        num = len(ann_ids)

    err_sz = fiConf["Amount"]
    err_sz = (err_sz * num) / 100
    err_sz = math.floor(err_sz)
    ind = random.sample(range(num), err_sz)


    if doInjectionByImg:
        img_ids = np.array(img_ids)
        selected_img_ids = img_ids[ind]
        ann_ids = coco_ann.getAnnIds(imgIds=selected_img_ids)
        ann_imgs = coco_ann.loadAnns(ann_ids)
    else:
        ann_ids = np.array(ann_ids)
        selected_ann_ids = ann_ids[ind]
        ann_imgs = coco_ann.loadAnns(selected_ann_ids)
        img_ann_dict = get_img_ann_dict(ann_imgs)
        selected_img_ids = list(img_ann_dict.keys())

    ann_id_counter = len(anns) + 1000 # Set counter to arbitrary high value to aid creation of new ann id

    all_cat = coco_ann.getCatIds()
    num_cat = len(all_cat)

    # Keep track of which images and annotations have been modified
    modified_img_ann_ids = {}


    # Inject into all randomly selected images
    for img_id in selected_img_ids:

        modified_img_ann_ids[img_id] = []
        ann_ids = coco_ann.getAnnIds(imgIds=[img_id])

        if doInjectionByImg:
            if not ann_ids:
                continue

            num_ann_imgs = len(ann_ids)
            inst_on_images = num_ann_imgs if (injections_per_image > num_ann_imgs) else injections_per_image

            # Randomly choose annotations for injection
            r = list(range(num_ann_imgs))
            random_ann_ids = random.sample(r, k=inst_on_images)
            selected_ann_ids_per_image = [ann_ids[i] for i in random_ann_ids]

            selected_ann_imgs_per_image = coco_ann.loadAnns(selected_ann_ids_per_image)

        else:
            selected_ann_imgs_per_image = img_ann_dict[img_id]

        # Get size of image for positioning faults onky
        if fault_type == "incorrect_bb" or fault_type == "redundant_ann":
            img_info = coco_ann.loadImgs([img_id])[0]
            img_width = img_info['width']
            img_height = img_info['height']

            err_pos = fiConf["Position"] if "Position" in fiConf else 20
            err_step = err_pos / 100
            err_x_step = img_width * err_step
            err_y_step = img_height * err_step

        # Inject into all randomly selected annotations (only 1 by default if doInjectionByImg)
        for ann_img in selected_ann_imgs_per_image:
            ann_id = ann_img['id']
            orig_cat_id = ann_img['category_id']

            if orig_cat_id not in all_cat:
                continue

            if fault_type == "mislabel_cat":
                # Mutate the category
                orig_ind = all_cat.index(orig_cat_id)
                r = list(range(0, orig_ind)) + list(range(orig_ind + 1, num_cat))
                new_cat_ind = random.choice(r)
                ann_img['category_id'] = all_cat[new_cat_ind]

            elif fault_type == "mislabel_super":
                # Mutate category to another supercategory
                all_cat_ids = coco_ann.getCatIds()
                query_annotation = coco_ann.loadCats([orig_cat_id])[0]
                query_supercategory = query_annotation['supercategory']
                related_cat_ids = coco_ann.getCatIds(supNms=[query_supercategory])
                r = list(set(all_cat_ids) - set(related_cat_ids))
                new_cat_id = random.choice(r)
                ann_img['category_id'] = new_cat_id

            elif fault_type == "incorrect_bb":
                orig_bbox = ann_img['bbox']
                orig_x = orig_bbox[0]
                orig_y = orig_bbox[1]
                orig_width = orig_bbox[2]
                orig_height = orig_bbox[3]

                if fiConf["Size"] != 0:
                    # Mutate bounding box size
                    (orig_width, orig_height) = mutate_bb_size(ann_img, orig_x, orig_y, orig_width,
                                                                orig_height, img_width, img_height, fiConf["Size"])

                if fiConf["Position"] != 0:
                    # Mutate bounding box position
                    mutate_bb_position(ann_img, orig_x, orig_y, orig_width, orig_height,
                                        img_width, img_height, err_x_step, err_y_step)

            elif fault_type == "remove_ann":
                #Remove annotation from image
                del anns[ann_id]

            elif fault_type == "redundant_ann":
                ann_id_counter = ann_id_counter + 1
                redundant_ann = copy.deepcopy(ann_img)
                redundant_ann['id'] = ann_id_counter
                anns[ann_id_counter] = redundant_ann

                orig_bbox = ann_img['bbox']
                orig_x = orig_bbox[0]
                orig_y = orig_bbox[1]
                orig_width = orig_bbox[2]
                orig_height = orig_bbox[3]

                # Mutate redundant bounding box size
                (orig_width, orig_height) = mutate_bb_size(redundant_ann, orig_x, orig_y, orig_width,
                                                            orig_height, img_width, img_height)

                # Mutate redundant bounding box position
                mutate_bb_position(redundant_ann, orig_x, orig_y, orig_width, orig_height,
                                    img_width, img_height, err_x_step, err_y_step)

                modified_img_ann_ids[img_id].append(ann_id_counter)

            # Track this annotation as modified
            if fault_type != "remove_ann" and fault_type != "redundant_ann":
                modified_img_ann_ids[img_id].append(ann_id)

    if fault_type == "remove_ann" or fault_type == "redundant_ann":
        coco_ann.dataset["annotations"] = list(anns.values())

    return modified_img_ann_ids

def get_new_pos_within_bounds(orig_pos, orig_size, err_step, img_bound, new_pos_list):
    new_pos = orig_pos + err_step
    if new_pos + orig_size <= img_bound:
        new_pos_list.append(new_pos)

    new_pos = orig_pos - err_step
    if new_pos >= 0:
        new_pos_list.append(new_pos)

def mutate_bb_size(ann_img, orig_x, orig_y, orig_width, orig_height, img_width, img_height, err_size=-50):
    err_sign = (err_size > 0)
    err_size = abs(err_size / 100)

    err_scale = math.sqrt(1 + err_size) if err_sign else math.sqrt(1 - err_size)
    new_width = round(orig_width * err_scale, 2)
    new_height = round(orig_height * err_scale, 2)

    if orig_x + new_width > img_width:
        new_width = img_width - orig_x

    if orig_y + new_height > img_height:
        new_height = img_height - orig_y

    ann_img['bbox'][2] = new_width
    ann_img['bbox'][3] = new_height

    return (new_width, new_height)

def mutate_bb_position(ann_img, orig_x, orig_y, orig_width, orig_height, img_width, img_height, err_x_step, err_y_step):
    new_x_list = [orig_x]
    get_new_pos_within_bounds(orig_x, orig_width, err_x_step, img_width, new_x_list)
    new_y_list = [orig_y]
    get_new_pos_within_bounds(orig_y, orig_height, err_y_step, img_height, new_y_list)

    if len(new_y_list)==1 and len(new_x_list)>1:
        new_x = random.choice(new_x_list[1:])
    else:
        new_x = random.choice(new_x_list)

    if new_x == orig_x and len(new_y_list)>1:
        new_y = random.choice(new_y_list[1:])
    else:
        new_y = random.choice(new_y_list)

    ann_img['bbox'][0] = new_x
    ann_img['bbox'][1] = new_y

# Get dict: {imgId: [anns]}
def get_img_ann_dict(anns):
    img_ann_dict = {}
    for ann in anns:
        ann_img_id = ann["image_id"]
        if ann_img_id not in img_ann_dict:
            img_ann_dict[ann_img_id] = []
        img_ann_dict[ann_img_id].append(ann)
    return img_ann_dict

