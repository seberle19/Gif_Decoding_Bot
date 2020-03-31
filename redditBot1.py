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


def removeNonAlphanumeric(line):
    '''
    Function that takes in a line of text from the filterText function. This
    function will then remove any characters that would likely not appear in
    a recipe.
    Returns: string without weird characters
    '''

    remove_list = [':','<', '>', ';', '(', ')', '|', "'"]

    cleaned_line = ""
    for character in line:
        if character not in remove_list:
            cleaned_line += character
    return cleaned_line


def filterText(raw_recipe_text):
    '''
    Function that takes in the raw text from running the Tesseract software on
    the image and filters out any empty or nonsensical text. This function will
    also account for any redundancies in the text.
    Returns: a list of the different lines of recipe
    '''
    #recipe to return
    recipe = []

    #print(raw_recipe_text)

    #ingredients Dict
    ing_dict = {}

    #set check to english words
    d = enchant.Dict("en_US")


    for line in raw_recipe_text:
        if line != "":
            line = removeNonAlphanumeric(line)
            split_line = line.split()

            #validate every "word" in line
            valid_line = ""
            for word in split_line:
                if d.check(word):
                    valid_line += word + " "

            #have not seen before and is a valid direction/ingredient
            if valid_line != "" and valid_line not in ing_dict:
                recipe.append(valid_line)
                ing_dict[valid_line] = True

    final_recipe = []
    for note in recipe:
        note = note.upper()
        final_recipe.append(note.strip())

    return final_recipe



def increaseContrast(image_list, path):
    '''
    Function that uses the cv equalizeHist function to increase the contrast
    wtihin the images. The point of this is to hopefully increase the difference
    between the text and the gif, which should make it easier to extract the
    text form the image.
    Returns: a list of images that have had their contrast increased
    '''

    contrasted_imgs = []
    #create clahe object
    clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8,8))

    for image in image_list:
        i = cv2.imread(path + image)
        #convert image to greyscale so that clahe works
        grayimg = cv2.cvtColor(i, cv2.COLOR_BGR2GRAY)
        contrast = clahe.apply(grayimg)
        contrasted_imgs.append(contrast)

    return contrasted_imgs


def remove_converted_images(path):

    for filename in os.listdir(path):
        file_path = os.path.join(path, filename)
        try:
            if os.path.isfile(file_path) or os.path.islink(file_path):
                os.unlink(file_path)
            elif os.path.isdir(file_path):
                shutil.rmtree(file_path)
        except Exception as e:
            print('Failed to delete %s. Reason: %s' % (file_path, e))


def main():

    r = praw.Reddit(client_id='***TOP SECRET***',
                         client_secret="***TOP SECRET***", password='***TOP SECRET***',
                         user_agent='PyEng Bot 1.0', username='***TOP SECRET***')


    top_GIF_recipe = r.subreddit("GifRecipes").hot(limit=5)


    #flag
    first_post = False
    #account for pinned posts
    gif_url_list = []
    for item in top_GIF_recipe:
        if not item.stickied:
            if first_post == False:
                top_submission = item #stores the submmission
                first_post = True
            gif_url_list.append(item.url)


    #only want the top one
    target_gif_url = gif_url_list[0]


    #Handle redirected urls
    res = urllib.request.urlopen(target_gif_url)
    redirected_target_gif_url = res.geturl()

    #scrape for the gif and save the image to a folder called mygifs
    os.system('image-scraper -s mygifs/downloaded ' +  redirected_target_gif_url +' --formats gif')


    #where the images are stored
    image_path = '/Users/ScottEberle/Desktop/Projects/GifDecoder/mygifs/downloaded'


    #extract image name from mygifs folder
    gif_recipe = os.listdir(image_path)[0]

    #get entire path to image
    total_image_path = image_path + "/" + gif_recipe


    #This divides image into numpy arrays:
    gif = imageio.mimread(total_image_path)

    imgs = [cv2.cvtColor(img, cv2.COLOR_RGB2BGR) for img in gif] #stored as numpy arrays

    mypath = '/Users/ScottEberle/Desktop/Projects/GifDecoder/mygifs/convertedImages/'

    #save each frame of the gif as a png image
    image_count = 0
    for frame in imgs:
        im = Image.fromarray(frame)
        image_count = str(image_count)
        image_name = "img" + image_count + ".png"
        im.save(mypath+image_name)
        image_count = int(image_count)
        image_count += 1


    #get list of all frames in convertedImages directory
    frames_of_gif = [f for f in listdir(mypath)]


    #sort the frames in the order of the gif so ingredients are seqential
    sorted_frames = natsort.natsorted(frames_of_gif)


    sorted_frames = increaseContrast(sorted_frames, mypath)

    #this list holds what the gif's text says
    recipe_list = []

    for image in sorted_frames:
        recipe_list.append(pytesseract.image_to_string(image))


    #Filter the text from the image
    filtered_recipe = filterText(recipe_list)

    #delete gif after done analyzing
    os.remove(total_image_path)

    #delete converted images
    remove_converted_images(mypath)


    print("Recipe:", *filtered_recipe,sep='\n')



if __name__ == "__main__":
    main()

