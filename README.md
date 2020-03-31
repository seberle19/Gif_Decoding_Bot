# Gif_Decoding_Bot

This program makes use of the reddit PRAW python library. The idea behind the program is to use PRAW to find the most popular GIF on the subreddit GIFRecipes. Once the top post is found, the GIF itself is scraped from the internet. Using the OpenCV library, the GIF is then converted to a series of images and these images are manipulated to make the text in the image more concrete. The tesseract OCR engine is then used on the images and the resulting textualization of the GIF is printed to the terminal. 
