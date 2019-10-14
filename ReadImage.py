import struct,os.path
from scipy import ndimage
import matplotlib.pyplot as plt
#from pylab import *
import numpy as np
from PIL import Image

def read_fuji(inf_file):
    """
    Read in a Fuji ISAC style file using the .inf extension
    the corresponding .img file must be in the same path
    """
 
    inf_data = dict()
    #read inf file and store all fields 
    inf_handle = open(inf_file, 'r')
    filetxt = inf_handle.readlines()
    inf_handle.close()
    # read in all inf data (not much is useful)
    for index,line in enumerate(filetxt):
        if index == 1: inf_data["image_file"] = line.strip()
        if index == 3: inf_data["pix_sx"] = line.strip()
        if index == 4: inf_data["pix_sy"] = line.strip()
        if index == 5: inf_data["pix_bitdepth"] = line.strip()
        if index == 6: inf_data["image_sx"] = line.strip()
        if index == 7: inf_data["image_sy"] = line.strip()
        if index == 8: inf_data["sensitivity"] = line.strip()
        if index == 9: inf_data["lattitude"] = line.strip()
        if index == 10: inf_data["date"] = line.strip()
        if index == 13: inf_data["scanner"] = line.strip()
        if index == 17: 
            str = line.strip()
            inf_data["range_low"] = str.split("=")[1]
        if index == 18: 
            str = line.strip()
            inf_data["range_high"] = str.split("=")[1]
        if index == 19: 
            str = line.strip()
            inf_data["scale_type"] = str.split("=")[1]
        if index == 20: 
            str = line.strip()
            inf_data["method"] = str.split("=")[1]
        if index == 21: 
            str = line.strip()
            inf_data["laser_name"] = str.split("=")[1]
        if index == 22: 
            str = line.strip()
            inf_data["filter_name"] = str.split("=")[1]
        if index == 23: 
            str = line.strip()
            inf_data["laser_power"] = str.split("=")[1]
        if index == 24: 
            str = line.strip()
            inf_data["nd_filter"] = str.split("=")[1]
        if index == 25: 
            str = line.strip()
            inf_data["compression_rate"] = str.split("=")[1]
        if index == 26: 
            str = line.strip()
            inf_data["shading_data"] = str.split("=")[1]
        if index == 27: 
            str = line.strip()
            inf_data["hot_cold_pix"] = str.split("=")[1]
        if index == 28: 
            str = line.strip()
            inf_data["smoothing"] = str.split("=")[1]
        if index == 29: 
            str = line.strip()
            inf_data["poly_face_corr"] = str.split("=")[1]
        if index == 30: 
            str = line.strip()
            inf_data["chidori"] = str.split("=")[1]
        else:
            pass  
        # for fuji images, use psl transformation for counts
        inf_data["use_psl"] = True
    dirname = os.path.dirname(inf_file)
    filename = '.'.join((inf_data["image_file"],'img'))
    image_filename = '/'.join((dirname,filename))
    #note, mode must be 'rb' - read binary for windows
    image_file_handle = open(image_filename,'rb')
    num_pix = int(inf_data["image_sx"])*int(inf_data["image_sy"])
    #read image data as string
    image_string = image_file_handle.read()
    image_file_handle.close()
    #read as default 16bit unsigned big-endian (use byte swap function if no good)
    format_string =">%sH" % num_pix
    #axes are swapped somehow
    image_dim = (int(inf_data["image_sy"]),int(inf_data["image_sx"]))
    #unpack string as binary data
    raw_data = struct.unpack(format_string,image_string)
    #convert to np.array image matrix format 1D
    image = np.array(raw_data,dtype="uint16")
    #convert the 1D array to a standard 2D image
    image.shape = (image_dim)
    #store information and image as object and return
    image_object = {'info':inf_data,'image':image}
    return image_object



def read_image(filename):
    """
    Read in an image using the Image PIL module (supports most formats)"""
    inf_data = dict()
    raw_image = Image.open(filename)
    raw_image.getdata()
    mode=raw_image.mode
    if (mode == "I;16"):
        (sx,sy)=raw_image.size
        inf_data["image_sx"] = int(sx)
        inf_data["image_sy"] = int(sy)
        inf_data["use_psl"] = False
        image = np.array(raw_image.getdata(),dtype='uint16')
        image = image.reshape((sy,sx))
    if (mode == "RGB"):
    ###image has three color channels, so sum for pixel counting?
        r,g,b = raw_image.split()
        ra,ga,ba = np.array(r,dtype='uint16'),np.array(g,dtype='uint16'),np.array(b,dtype='uint16')
        image = ra + ga + ba
        print image.shape
        inf_data["image_sx"] = image.shape[0]
        inf_data["image_sy"] = image.shape[1]
        inf_data["use_psl"] = False
        print inf_data
    image_object = {'info':inf_data,'image':image}
    return image_object








