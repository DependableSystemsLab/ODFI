# ODFI - Object Detection Fault Injector

## 1. Artifact Description

This repository contains the source code for ODFI, an annotation fault injection tool for object detection datasets in [COCO-Format](https://cocodataset.org/#format-data).

We support five types of annotation faults. Each annotation fault is listed, along with its in-tool abbreviation.
You may read more about the description of each fault type in the [paper](https://blogs.ubc.ca/dependablesystemslab/2023/08/07/evaluating-the-effect-of-common-annotation-faults-on-object-detection-techniques-per/).
* Mislabelled Class (`mislabel_cat`)
* Mislabelled Superclass (`mislabel_super`)
* Incorrect Bounding Box (`incorrect_bb`)
* Missing Annotation (`remove_ann`)
* Redundant Annotation (`redundant_ann`)


### Directory Layout

```
.
├── cocoextra.py
├── coco_patch
│   └── coco_py.patch
├── confFiles
├── data
│   └── cocotraffic-sample
│       ├── injected (create this folder)
│       ├── train_annotations.json
│       └── train_images
├── display.py
├── examples
│   └── explore_coco.py
├── inject.py
├── odfi.py
├── README.md
├── test
│   ├── confFiles
    ├── InjectionOverObjectsTest.py
    └── InjectionPerImageTest.py
```


## 2. Environment Setup

### Dependencies

1. Ensure you that you have Python 3+, and have the following dependencies installed.
```bash
pip install matplotlib numpy pillow scikit-image
```

2. Clone the [COCO API repository](https://github.com/cocodataset/cocoapi.git).
```bash
git clone https://github.com/cocodataset/cocoapi.git
```

3. Copy the folder, `coco_patch` into the newly cloned COCO API repository.
```bash
cp -r coco_patch ./cocoapi/
cd cocoapi
```

4. Apply the coco_py_patch on the repository.
```bash
git apply coco_patch/coco_py.patch
```

5. Install the COCO API in editable mode.
```bash
pip install -e .
```

6. COCO API should now be installed. You can confirm this by runing `pip freeze`.


## 3. Getting Started

### Instructions on Running ODFI Test (Demo) Scripts

This is the easiest way to start visualizing the annotation boxes injected / perturbed by ODFI on a COCO-Formatted dataset.
For your convenience, we have included a small sample of 10 images from COCO-Traffic dataset under the [data](./data/) folder.

> **_NOTE:_**  You will need GUI access (or X11 forwarding enabled if connected to a remote server) to visualize the before and after images containing injected annotations.

1. Navigate to the test folder.
```bash
cd test
```

2. Run ODFI in fault injection per image mode. This will inject exactly one fault per image. For each fault type, the before (original golden) image will appear first.
After closing the before image, another window will shortly pop up. This is the after image. In the image window, you will see "After " and the name of the abbreviated fault type injected.
For example, `mislabel_cat-100-1` means that the mislabelled class fault has been injected once per image, on 100% of the training dataset. Close the popup image windows to proceed to the next fault injection. All tests should pass in the end.
```bash
python InjectionPerImageTest.py
```

3. Run ODFI in fault injection over objects mode. This will inject into every object annotation over every single image in the dataset. For each fault type, the before (original golden) image will appear first.
After closing the before image, another window will shortly pop up. This is the after image. In the image window, you will see "After " and the name of the abbreviated fault type injected.
For example, `mislabel_cat-100` means that the mislabelled class fault has been injected into every object annotation in the training dataset.  Close the popup image windows to proceed to the next fault injection. All tests should pass in the end.
```bash
python InjectionOverObjectsTest.py
```

### Instructions on Running ODFI on Entire Datasets

Please follow these instructions if you want to run ODFI on an entire dataset.
For your convenience, we have included a small sample of 10 images from COCO-Traffic dataset under the [data](./data/) folder, as well as, predefined YAML files under [confFiles](./confFiles/).
While you do not need to create additional YAML files for this demo, you may read more about how to setup your custom YAML file [here](./confFiles/README.md).

1. Create a folder to store the injected annotation JSON files.
```bash
mkdir data/cocotraffic-sample/injected
```

2. Inject annotation faults of your choice into any COCO-Formatted dataset by creating a new JSON file containing the faulty injected annotations
The original golden JSON file (supplied under the `ann_json` argument) is not modified.
The `.changed` file will contain a dictionary of `{image_id: [ann_ids]}` in JSON format, where a list of all the impacted images and annotation ids are shown.

Example injecting Mislabelled Class
Change the relative paths below as appropriate.

* Using long options:
```bash
python inject.py --ann_json ~/ODFI/data/cocotraffic-sample/train_annotations.json --images_path ~/ODFI/data/cocotraffic-sample/train_images --odfi_yaml ~/ODFI/confFiles/mislabel_cat-10.yaml --output ~/ODFI/data/cocotraffic-sample/injected/mislabel_cat-10.json --change_file ~/ODFI/data/cocotraffic-sample/injected/mislabel_cat-10.changed
```

* Using short options:
```bash
python inject.py -a ~/ODFI/data/cocotraffic-sample/train_annotations.json -i ~/ODFI/data/cocotraffic-sample/train_images -y ~/ODFI/confFiles/mislabel_cat-10.yaml -o ~/ODFI/data/cocotraffic-sample/injected/mislabel_cat-10.json -c ~/ODFI/data/cocotraffic-sample/injected/mislabel_cat-10.changed
```

3. Display the before and after images with annotations overlayed, side-by-side.
You should see the injected annotations marked in red on the After (right) side plot.
`display.py` will cycle through every image, affected by fault injection.
```bash
python display.py -a ~/ODFI/data/cocotraffic-sample/train_annotations.json -i ~/ODFI/data/cocotraffic-sample/train_images -o ~/ODFI/data/cocotraffic-sample/injected/mislabel_cat-10.json -c ~/ODFI/data/cocotraffic-sample/injected/mislabel_cat-10.changed
```

4. Try running this for other fault types.
* Redundant Annotation
```bash
python inject.py -a ~/ODFI/data/cocotraffic-sample/train_annotations.json -i ~/ODFI/data/cocotraffic-sample/train_images -y ~/ODFI/confFiles/redundant_ann-10.yaml -o ~/ODFI/data/cocotraffic-sample/injected/redundant_ann-10.json -c ~/ODFI/data/cocotraffic-sample/injected/redundant_ann-10.changed
python display.py -a ~/ODFI/data/cocotraffic-sample/train_annotations.json -i ~/ODFI/data/cocotraffic-sample/train_images -o ~/ODFI/data/cocotraffic-sample/injected/redundant_ann-10.json -c ~/ODFI/data/cocotraffic-sample/injected/redundant_ann-10.changed
```

* Missing Annotation
```bash
python inject.py -a ~/ODFI/data/cocotraffic-sample/train_annotations.json -i ~/ODFI/data/cocotraffic-sample/train_images -y ~/ODFI/confFiles/remove_ann-10.yaml -o ~/ODFI/data/cocotraffic-sample/injected/remove_ann-10.json -c ~/ODFI/data/cocotraffic-sample/injected/remove_ann-10.changed
python display.py -a ~/ODFI/data/cocotraffic-sample/train_annotations.json -i ~/ODFI/data/cocotraffic-sample/train_images -o ~/ODFI/data/cocotraffic-sample/injected/remove_ann-10.json -c ~/ODFI/data/cocotraffic-sample/injected/remove_ann-10.changed
```

* Incorrect Bounding Box
```bash
python inject.py -a ~/ODFI/data/cocotraffic-sample/train_annotations.json -i ~/ODFI/data/cocotraffic-sample/train_images -y ~/ODFI/confFiles/incorrect_bb-10.yaml -o ~/ODFI/data/cocotraffic-sample/injected/incorrect_bb-10.json -c ~/ODFI/data/cocotraffic-sample/injected/incorrect_bb-10.changed
python display.py -a ~/ODFI/data/cocotraffic-sample/train_annotations.json -i ~/ODFI/data/cocotraffic-sample/train_images -o ~/ODFI/data/cocotraffic-sample/injected/incorrect_bb-10.json -c ~/ODFI/data/cocotraffic-sample/injected/incorrect_bb-10.changed
```

* Mislabelled Superclass
```bash
python inject.py -a ~/ODFI/data/cocotraffic-sample/train_annotations.json -i ~/ODFI/data/cocotraffic-sample/train_images -y ~/ODFI/confFiles/mislabel_super-10.yaml -o ~/ODFI/data/cocotraffic-sample/injected/mislabel_super-10.json -c ~/ODFI/data/cocotraffic-sample/injected/mislabel_super-10.changed
python display.py -a ~/ODFI/data/cocotraffic-sample/train_annotations.json -i ~/ODFI/data/cocotraffic-sample/train_images -o ~/ODFI/data/cocotraffic-sample/injected/mislabel_super-10.json -c ~/ODFI/data/cocotraffic-sample/injected/mislabel_super-10.changed
```

## Citation

Please cite the following paper if you use our tool.

```
@inproceedings{Chan2023_ODFI,
  author    = {Chan, Abraham and Gujarati, Arpan and Pattabiraman, Karthik and Gopalakrishnan, Sathish},
  title     = {{Evaluating the Effect of Common Annotation Faults on Object Detection Techniques}},
  booktitle = {2023 IEEE 34th International Symposium on Software Reliability Engineering (ISSRE)},
  year      = {2023}
}
```

