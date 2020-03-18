import praw
import image_scraper
import os
import urllib
import pytesseract
import cv2
import imageio
from PIL import Image
from os import listdir
from os.path import isfile, join
import natsort
import enchant
import re

def filterText(raw_recipe_text):
    '''
    Function that takes in the raw text from running the Tesseract software on
    the image and filters out any empty or nonsensical text. This function will
    also account for any redundancies in the text.
    '''
    #recipe to return
    recipe = []

    print("RAW:",raw_recipe_text)

    #ingredients Dict
    ing_dict = {}

    #set check to english words
    d = enchant.Dict("en_US")

    for line in raw_recipe_text:
        if line != "":
            split_line = line.split()

            #validate every "word" in line
            valid_line = ""
            for word in split_line:
                if d.check(word):
                    valid_line += word + " "


            #strip of any non alphanumeric characters
            regex = re.compile('([^\s\w]|_)+')
            #First parameter is the replacement, second parameter is your input string
            valid_line = regex.sub('', valid_line)


            #have not seen before and is a valid direction/ingredient
            if valid_line != "" and valid_line not in ing_dict:
                #double check for no redundancies
                recipe.append(valid_line)
                ing_dict[valid_line] = True



    return recipe


#TODO: implement function that uses cv2 to increase constrast in images through
#      the histogram thing

def contrastImages(image_list, path):
    '''
    Function that uses the cv equalizeHist function to increase the contrast
    wtihin the images. The point of this is to hopefully increase the difference
    between the text and the gif, which should make it easier to extract the
    text form the image.
    '''

    contrasted_imgs = []

    #create clahe object
    clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8,8))

    for image in image_list:
        i = cv2.imread(path + image)
        #convert image to greyscale so that clahe works
        grayimg = cv2.cvtColor(i, cv2.COLOR_BGR2GRAY)

        contrast = clahe.apply(grayimg)
        print(type(contrast), "contrast type")

        contrasted_imgs.append(contrast)


    return contrasted_imgs

def main():

    ##############CLEAR THESE SO THEY ARE NOT PUBLIC
    r = praw.Reddit(client_id='PoRv0-pH0Uc3Ag',
                         client_secret="jbdOyC6HuNd0_WwHKRBZutqPtnE", password='superswag',
                         user_agent='PyEng Bot 1.0', username='LaxestBro')


    top_GIF_recipe = r.subreddit("GifRecipes").hot(limit=5)

    #account for pinned posts
    gif_url_list = []
    for item in top_GIF_recipe:
        if not item.stickied:
            gif_url_list.append(item.url)


    #only want the top one
    target_gif_url = gif_url_list[0]


    #Handle redirected urls
    res = urllib.request.urlopen(target_gif_url)
    redirected_target_gif_url = res.geturl()

    #scrape for the gif and save the image to a folder called mygifs
    os.system('image-scraper -s mygifs ' +  redirected_target_gif_url +' --formats gif')


    #where the images are stored
    image_path = '/Users/ScottEberle/Desktop/Projects/GifDecoder/mygifs'

    #extract image name from mygifs folder
    #TODO: make it so it can find the image name without hard coding
    gif_recipe = os.listdir(image_path)[2]


    #get entire path to image
    total_image_path = image_path + "/" + gif_recipe



    #total_image_path = '/Users/ScottEberle/Desktop/Projects/GifDecoder/mygifs/Doggo.gif'



    #This divides image into numpy arrays:
    gif = imageio.mimread(total_image_path)

    imgs = [cv2.cvtColor(img, cv2.COLOR_RGB2BGR) for img in gif] #stored as numpy arrays

    #save each frame of the gif as a jpeg image
    image_count = 0
    for frame in imgs:
        im = Image.fromarray(frame)
        image_count = str(image_count)
        image_name = "img" + image_count + ".jpeg"
        im.save('/Users/ScottEberle/Desktop/Projects/GifDecoder/mygifs/convertedImages/'+image_name)
        image_count = int(image_count)
        image_count += 1

    #CHANGE PATH VARIABLE
    #get list of all files in convertedImages directory
    mypath = '/Users/ScottEberle/Desktop/Projects/GifDecoder/mygifs/convertedImages/'
    frames_of_gif = [f for f in listdir(mypath)]


    #sort the frames in the order of the gif so ingredients are seqential
    sorted_frames = natsort.natsorted(frames_of_gif)

    #this list holds what the gif's text says
    recipe_list = []


    #TODO:sent images through histogram equalization
    sorted_frames = contrastImages(sorted_frames, mypath)


    for image in sorted_frames:
        recipe_list.append(pytesseract.image_to_string(image))



    filtered_recipe = filterText(recipe_list)
    print()
    print("Break")
    print()
    print()
    print("Filtered Recipe:", filtered_recipe)


if __name__ == "__main__":
    main()

    #THEN POST IN COMMENT THE RECIPE
