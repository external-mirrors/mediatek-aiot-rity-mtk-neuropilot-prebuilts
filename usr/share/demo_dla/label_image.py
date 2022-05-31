import os
import re
import subprocess as sp
import numpy as np
from PIL import Image



img_file = "grace_hopper.jpg"
img_bin = "grace_hopper.bin"
tflite_model = "mobilenet_v1_1.0_224_quant.tflite"
dla_model = "mobilenet_v1_1.0_224_quant.dla"
label_file = "imagenet_slim_labels.txt"

def img_to_bin():
    img = Image.open(img_file).convert("RGB")
    newsize = (224, 224)
    img = img.resize(newsize)
    img_raw = np.asarray(img)
    img_data = np.reshape(img_raw, (1, 224, 224, 3))
    img_data.tofile(img_bin);

def tflite_to_dla():
    sp.getoutput("ncc-tflite -arch mdla2.0 %s -o %s" % (tflite_model, dla_model) )

def inference_dla():
    pwd = os. getcwd()
    
    dla_model_path = pwd + '/' + dla_model;
    img_bin_path = pwd + '/' + img_bin;
    print(dla_model_path)
    print(img_bin_path)
    out = sp.getoutput("cd /usr/lib64/;./runtime_api_sample %s %s" % (dla_model_path, img_bin_path))
    print("stdout::: ", out)
    
    # parse output, find top index
    temp = re.findall(r'\d+', out)
    res = list(map(int, temp))
    top_index = res[-1]
    
    # read labels to find image classification result
    f = open(label_file, 'r')
    lines = f.readlines()
    result = lines[top_index]
    print("The image:", result)
    f.close()
    

if __name__ == "__main__":
    img_to_bin()
    tflite_to_dla()
    inference_dla()
    