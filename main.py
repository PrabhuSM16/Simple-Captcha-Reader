from glob import glob
import os
import cv2

class Captcha(object):
  def __init__(self, db, charSize=5, yPad=2, xPad=1):
    """
    input:
      db       -> database (folder) of images of all known chars and their labels (ground truth templates)
      charSize -> minimum size of character
    output:
      Write predicted chars to file
    """
    assert os.path.exists(db), f'Database of characters "{db}" does not exist!'
    
    self.charSize = charSize # store the minimum size of each character
    self.yPad = yPad
    self.xPad = xPad

    # load database of characters to buffers
    _refs = glob(f'{char_src}/*.jpg')
    self.refs = []          # list to hold all char buffers
    self.labs = []          # list to hold all char labels
    for ref in _refs:
      self.refs.append(cv2.imread(ref))
      self.labs.append(os.path.basename(ref).split(".jpg")[0])

  def __call__(self, im_path, save_path, preview=False):
    # main call to captcha reader
    assert os.path.exists(im_path), f'Path to Captcha "{im_path}" does not exist!'

    im = cv2.imread(im_path) # read captcha to numpy array
    ans = "" # placeholder for predicted chars

    rois = self.extract_char_ROIs(im) # extract ROIs for each letter

    # extract each ROI and apply template matching
    for roi in rois[::-1]:
      if cv2.contourArea(roi) > self.charSize: # threshold on ROI size to filter out noise, if any
        x, y, w, h = cv2.boundingRect(roi) # get bounding box properties of ROI for cropping
        ans += self.recognize_char(im[y-self.yPad : y+h+self.yPad, x-self.xPad : x+w+self.xPad]) # crop ROI bounding box and pass to template matching
    
    # display captcha and print predicted label
    if preview:
      print(ans)
      cv2.imshow('input', im)
      if cv2.waitKey() & 0xFF == ord('q'):
        exit()
      cv2.destroyAllWindows()

    # save output to file
    with open(save_path, 'w') as f:
      f.write(f'{ans}\n')

  def extract_char_ROIs(self, img):
    # extract ROIs for each character in each captcha
    captcha = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY) # convert from RGB to grayscale
    _, bin = cv2.threshold(captcha, 50, 255, cv2.THRESH_BINARY_INV) # inverse binarize image (search from darker regions)
    rois, _ = cv2.findContours(bin, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE) # extract ROI (external connected group of points)
    return rois
      
  def recognize_char(self, char): 
    # apply template matching between cropped char and all reference chars in DB
    res = [cv2.matchTemplate(char, ref, cv2.TM_CCORR_NORMED)[0][0] for ref in self.refs]
    
    # identity of char corresponds to char whose match template score is highest
    id = res.index(max(res))

    return self.labs[id]
    
if __name__ == '__main__':
  # define folders
  char_src = "./chars"      # location of database of characters
  captcha_src = "./input"   # location of input captchas to be inferred (.jpg images)
  captcha_dst = "./output"  # location where output will be stored (.txt files)
  
  # create output directory
  os.makedirs(captcha_dst, exist_ok=True)

  # instantiate Captcha reader
  captchaInf = Captcha(char_src, charSize=5)

  # load captchas for inference
  captchas = glob(f'{captcha_src}/*.jpg')
  
  # loop
  for cap in captchas:
    dst = f'{captcha_dst}/{os.path.basename(cap).replace(".jpg", ".txt")}' # generate save path
    captchaInf(cap, dst) # inference
