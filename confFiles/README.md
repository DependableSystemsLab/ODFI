# ODFI Fault Injection YAML Format

ODFI enables five types of annotation faults to be injected (one fault type at a time).
ODFI performs fault injection according to the fault type defined in a YAML file.
This folder contains many predefined YAML files, which you may use directly **without further modification**.


## Organization of YAML files in this folder

The YAML files in this folder are divided into two modes: fault injection per image or fault injection over objects.

Here, we illustrate an example of how to interpret the name of the YAML file.

1. Fault injection per image (`-1.yaml` suffix at the end of the file): injects exactly one annotation fault (randomly selected annotation box) per randomly selected image.
E.g. If there are 10 images, the fault type is `mislabel_cat` and the fault amount is 10%, then only one annotation fault will be injected into 1 randomly selected image.
[mislabel_cat-10-1.yaml](mislabel_cat-10-1.yaml)

2. Fault injection over objects: injects annotation faults over randomly selected annotation boxes.
E.g. If there are 10 images containing 2 annotations each, the fault type is `mislabel_cat` and the fault amount is 10%, then 2 annotation faults will be injected across the 10 images.
Examples of possible outcomes:
* Image #1 and Image #5 both have one faulty annotation each. Rest of the images are untouched.
* Image #1 has two faulty annotations. Rest of the images are untouched.
[mislabel_cat-10.yaml](mislabel_cat-10.yaml) 


## How to define your own custom YAML file (Optional)

1. For all fault types except `incorrect_bb`, define it in the following format:
```yaml
Type: <fault_type>
Amount: <fault_amount>
Injections_Per_Image: 1 # Only add this line if you want to inject per image
```

2. For `incorrect_bb` only, define it in the following format:
```yaml
Type: <fault_type>
Amount: <fault_amount>
Size: <size_diff_percentage>
Position: <position_offset_percentage>
Injections_Per_Image: 1 # Only add this line if you want to inject per image
```

## Acceptable Values / Ranges for YAML fields

1. Fault Type - Must use abbreviated form in parentheses:
* Mislabelled Class (`mislabel_cat`)
* Mislabelled Superclass (`mislabel_super`)
* Incorrect Bounding Box (`incorrect_bb`)
* Missing Annotation (`remove_ann`)
* Redundant Annotation (`redundant_ann`)

2. Fault Amount: 0 to 100

3. Injections Per Image: Any positive integer value

4. Size Diff Percentage: -100 to 100

5. Position Offset Percentage: -100 to 100

> **_NOTES:_** For Injections Per Image, ODFI will never inject more than the number of total annotations in a single image. For size and position parameters, ODFI will automatically reject scenarios where the injected annotation box is outside the bounds of the original image dimensions.

