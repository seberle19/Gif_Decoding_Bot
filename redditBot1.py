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
print(target_gif_url, "target")

#Handle redirected urls
res = urllib.request.urlopen(target_gif_url)
redirected_target_gif_url = res.geturl()

#scrape for the gif and save the image to a folder called mygifs
os.system('image-scraper -s mygifs ' +  redirected_target_gif_url +' --formats gif')


#where the images are stored
image_path = '/Users/ScottEberle/Desktop/Projects/GifDecoder/mygifs'

#extract image name from mygifs folder
gif_recipe = os.listdir(image_path)[0]

'''
#get entire path to image
total_image_path = image_path + "/" + gif_recipe
print(total_image_path)
'''

total_image_path = '/Users/ScottEberle/Desktop/Projects/GifDecoder/mygifs/Doggo.gif'



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

#TODO: sort names of images so that it is in order when we go through it in
#      pytesseract
print(frames_of_gif)



'''
for image in frames_of_gif:
    print(pytesseract.image_to_string(image))


print(pytesseract.image_to_string(frame))
print()
'''


#take image and use it in tesseract to get out the recipe.



#THEN POST IN COMMENT THE RECIPE
