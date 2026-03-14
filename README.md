# Simple Captcha Reader

A small python class using template matching to read simple captchas with the following properties:
- All characters share the same font and spacing
- Background and foreground colors and textures are largely consistent between samples
- No skewing of the character structures

### Requirements
- Python 3
- OpenCV

### Approach
Given the above requirements for the captcha, the following assumptions can be made:
- Shape/Size/Color of characters would remain roughly the same, regardless of position
- No overlapping of characters (Consistent spacing between characters)

To infer the sequence of characters, a simple pipeline is used:
- Convert captcha image to grayscale
- Binarize (segment) the image (search for dark areas -> characters)
- Extract regions of interest (ROIs) by leveraging on the connectedness of segmented points (No overlapping between characters)
- Apply a small padding along the width and height to capture the external structure of each character
- Compare the normalized cross-correlation score between the padded ROI and each template in the DB
- The **identity** of the padded ROI is taken to be the **label** of the template with the **highest corresponding normalized cross-correlation score**
- Output is saved to a .txt file in "./output" with the same name as the input image

## Installation

Clone this repo:
```bash
git clone 
cd SimpleCaptchaReader
```  

Create virtual enviornment:
```bash
python -m venv .env
```  

Activate the virtual environment:
```bash
.env/Scripts/activate    # For Windows environment
source .env/bin/activate # For Linux environment
```  

Install requirements via Pip:
```bash
python -m pip install -r requirements.txt
```  

## Create a database of templates
**An example of the completed DB is attached in this repo**</br></br>
To recognize the captcha characters with template matching, we must first build a small database of all known characters:
- Upper-case Characters (A - Z)
- Numerals (0 - 9)

Extract all characters from available data:
```bash
python create_db.py # images will be stored in ./chars
```

In "./chars" folder,
- Manually select 1 sample for each unique character
- Rename the sample to the character's name
- Delete all other copies

## Inference
To infer the text in a Captcha, in a Python 3 console:
- Set the paths to the database of templates, and source folder of Captcha images:
```python
char_src = "./chars"      # location of database of characters
captcha_src = "./input"   # location of input captchas to be inferred (.jpg images)
```

- Create the destination folder to store the output txt files:
```python
captcha_dst = "./output"  # location where output will be stored (.txt files)
os.makedirs(captcha_dst, exist_ok=True)
```

- Create an instance of the Captcha reader class:
```python
captchaInf = Captcha(char_src, charSize=5)
```

- Load all captcha images in source folder:
```python
captchas = glob(f'{captcha_src}/*.jpg')
```

- Looping over all captchas, create the destination folder name, and pass the captcha to the reader:
```python
for cap in captchas:
    dst = f'{captcha_dst}/{os.path.basename(cap).replace(".jpg", ".txt")}' # generate save path
    captchaInf(cap, dst, preview=False) # inference (To display output, set preview flag to True)
```

Alternatively, you can run the main file with default values (in bash):
```bash
python main.py
```


