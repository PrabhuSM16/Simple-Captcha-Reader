from glob import glob
import os
import cv2

def build_db(src, dst, charSize=5, yPad=2, xPad=1):
  # function to extract all characters in the image set and store in a new folder
  # User to manually filter out 1 sample for each unique character (0-9, A-Z)
  assert os.path.exists(src), f'Source folder "{src}" does not exist!'
  
  if not os.path.exists(dst):
    os.makedirs(dst) # create folder to store all unique characters

    imgs = glob(f'{src}/*.jpg')
    i = 0

    # loop through all images
    for img in imgs:
      im = cv2.imread(img) # read image

      # extract character ROI
      captcha = cv2.cvtColor(im, cv2.COLOR_BGR2GRAY) # convert from RGB to grayscale
      _, bin = cv2.threshold(captcha, 50, 255, cv2.THRESH_BINARY_INV) # inverse binarize image (search from darker regions)
      rois, _ = cv2.findContours(bin, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE) # extract ROI (external connected group of points)

      # for each ROI, cut out a padded area and save
      for roi in rois[::-1]:
        if cv2.contourArea(roi) > charSize: # threshold on ROI size to filter out noise, if any
          x, y, w, h = cv2.boundingRect(roi) # get bounding box properties of ROI for cropping
          
          cv2.imwrite(f'{dst}/{i:03d}.jpg', im.copy()[y-yPad:y+h+yPad, x-xPad:x+w+xPad]) # write to image
          i+=1

if __name__ == '__main__':
  # define folders
  char_src = "./chars"      # location of database of characters
  captcha_src = "./input"   # location of input captchas to be inferred (.jpg images)
  
  # creates a folder of char images to use as ground truth templates for recognition (early exit if dst exists)
  build_db(captcha_src, char_src, charSize=5, yPad=2, xPad=1)

  # User to manually select and rename 1 sample of each possible character (0-9, A-Z)