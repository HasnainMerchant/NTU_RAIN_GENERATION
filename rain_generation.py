import matplotlib.pyplot as plt
import glob
import cv2 as cv2
import argparse
import numpy as np
import os
import time
# from PIL import Image, ImageEnhance

# Converts components instead of the RGB representation to HLS
# The HSV model describes colors similarly to how the human eye tends to perceive color.
######################## HLS (Hue, Lightness, Saturation) #########################################
def hls(image,src='RGB'):
    verify_image(image)
    if(is_list(image)):
        image_HLS = []
        image_list = image
        for img in image_list:
            eval('image_HLS.append(cv2.cvtColor(img,cv2.COLOR_' + src.upper() + '2HLS))')
    else:
        image_HLS = eval('cv2.cvtColor(image,cv2.COLOR_' + src.upper() + '2HLS)')
    return image_HLS

# Allows us to assign channels in the data to R, G and B (Red, Green, Blue) 
######################## RGB #########################################
def rgb(image, src='BGR'):
    verify_image(image)
    if(is_list(image)):
        image_RGB = []
        image_list = image
        for img in image_list:
            eval('image_RGB.append(cv2.cvtColor(img,cv2.COLOR_' + src.upper() + '2RGB))')
    else:
        image_RGB = eval('cv2.cvtColor(image,cv2.COLOR_' + src.upper() + '2RGB)')
    return image_RGB

######################## GENERATE RANDOM LINES #########################################
def generate_random_lines(imshape, slant, drop_length, rain_intensity):
    drops = []
    area = imshape[0] * imshape[1]
    no_of_drops = area//600

    if rain_intensity.lower() == '10mm':
        no_of_drops = area//700
        drop_length = 12
    elif rain_intensity.lower() == '20mm':
        no_of_drops = area//600
        drop_length = 15
    elif rain_intensity.lower() == '30mm':
        no_of_drops = area//700
        drop_length = 20
    elif rain_intensity.lower() == '40mm':
        no_of_drops = area//800
        drop_length = 25
    elif rain_intensity.lower() == '50mm':
        no_of_drops = area//600
        drop_length = 30
    elif rain_intensity.lower() == '100mm':
        no_of_drops = area//770
        drop_length = 40
    elif rain_intensity.lower() == '200mm':
        no_of_drops = area//770
        drop_length = 50

    for i in range(no_of_drops):
        if slant < 0:
            x = np.random.randint(slant, imshape[1])
        else:
            x = np.random.randint(0, imshape[1] - slant)
        y = np.random.randint(0, imshape[0] - drop_length)
        drops.append((x,y))
    return drops, drop_length

######################## PROCESSING RAIN IMAGES #########################################
def rain_process(image, slant, drop_length, drop_color, drop_width, rain_drops, brightness):
    imshape = image.shape  
    image_t = image.copy()
    for rain_drop in rain_drops:
        cv2.line(image_t, (rain_drop[0], rain_drop[1]), (rain_drop[0] + slant,rain_drop[1] + drop_length), drop_color, drop_width)
    image = cv2.blur(image_t, (4, 4)) ## rainy view are blurry
    # image_2 = Image
    # enhancer = ImageEnhance.Brightness(image)
    # image_output = enhancer.enhance(brightness)
    image_HLS = hls(image) ## Conversion to HLS
    image_RGB = rgb(image_HLS, 'hls') ## Conversion to RGB
    return image_RGB

######################## ADD OOD RAIN TO IMAGES #########################################
def add_rain(image, slant=-1, rain_intensity='None', brightness=0, drop_length=20, drop_width=1, drop_color=(200,200,200)): ## (200,200,200) a shade of gray
    verify_image(image)
    slant_extreme = slant

    #Error Checking of values
    if not(is_numeric(slant_extreme) and (slant_extreme >= -20 and slant_extreme <= 20) or slant_extreme == -1):
        raise Exception(err_rain_slant)
    if not(is_numeric(drop_width) and drop_width >= 1 and drop_width <= 5):
        raise Exception(err_rain_width)
    if not(is_numeric(drop_length) and drop_length >= 0 and drop_length <= 100):
        raise Exception(err_rain_length)

    if(is_list(image)):
        image_RGB = []
        image_list = image
        imshape = image[0].shape
        if slant_extreme == -1:
            slant = np.random.randint(-10, 10) ##generate random slant if no slant value is given
        for img in image_list:
            rain_drops, drop_length = generate_random_lines(imshape, slant, drop_length, rain_intensity)
            output = rain_process(img, slant_extreme, drop_length, drop_color, drop_width, rain_drops, brightness)
            image_RGB.append(output)
    else:
        imshape = image.shape
        if slant_extreme == -1:
            slant = np.random.randint(-10, 10) ##generate random slant if no slant value is given
        rain_drops, drop_length = generate_random_lines(imshape, slant, drop_length, rain_intensity)
        output = rain_process(image, slant_extreme, drop_length, drop_color, drop_width, rain_drops)
        image_RGB=output

    return image_RGB

######################## LOAD IMAGES FROM PATH #########################################
def load_images(path):
    image_list = []
    images = glob.glob(path)
    for index in range(len(images)):
        image= cv2.cvtColor(cv2.imread(images[index]),cv2.COLOR_BGR2RGB)
        image_list.append(cv2.resize(image,(1280,720)))
     
    return image_list

######################## GENERATE RAIN IMAGES #########################################
def generate_rain(args):
    # path = './images/*.png'
    images = load_images(args.input + "/*.png")

    rainy_images = add_rain(images, args.slant, args.rain_intensity, args.brightness_level)
    # print("Rain Images generated")

    save_images(rainy_images)

######################## SAVE IMAGES #########################################
def save_images(images):
    new_dir_name = f"rain{args.rain_intensity}"
    current_dir = os.getcwd()
    new_dir = os.path.join(current_dir, new_dir_name)
    os.mkdir(new_dir)
    i=0
    for img in images:
        # plt.imsave(f"{new_dir}/img{i}.png", img)
        cv2.imwrite(f"{new_dir}/img{i}.png", img)
        i += 1

######################## ERROR CHECKING #########################################
def is_numpy_array(x):
    return isinstance(x, np.ndarray)
def is_tuple(x):
    return type(x) is tuple
def is_list(x):
    return type(x) is list
def is_numeric(x):
    return type(x) is int
def is_numeric_list_or_tuple(x):
    for i in x:
        if not is_numeric(i):
            return False
    return True
def verify_image(image):
    if is_numpy_array(image):
        pass
    elif(is_list(image)):
        image_list = image
        for img in image_list:
            if not is_numpy_array(img):
                raise Exception("not a numpy array or list of numpy array")
    else:
        raise Exception("not a numpy array or list of numpy array")
err_rain_slant = "Numeric value between -20 and 20 is allowed"
err_rain_width = "Width value between 1 and 5 is allowed"
err_rain_length = "Length value between 0 and 100 is allowed"

######################## MAIN #########################################
if __name__ == '__main__':
    parser = argparse.ArgumentParser('Add OOD Rain to Images')
    parser.add_argument(
        '--input',
        help='Input Folder Of Files')
    parser.add_argument(
        '--rain_intensity',
        default='10mm',
        help='Add Rain Intensity')
    parser.add_argument(
        '--slant',
        default=-5,
        type=int,
        help='Enter Slant For Droplets Of Rains')
    parser.add_argument(
        '--brightness_level',
        default=0.0,
        type=float,
        help='Enter Brightness Level')
    # parser.add_argument(
    #     '--save',
    #     default='./',
    #     help='Enter The Path Where To Save')
    args = parser.parse_args()
    st = time.time()
    generate_rain(args)
    et = time.time()
    print(f"ELAPSED TIME - {et-st}")