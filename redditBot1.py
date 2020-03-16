import praw
import image_scraper
import os
import urllib



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
print(target_gif_url)

#Handle redirected urls
res = urllib.request.urlopen(target_gif_url)
redirected_target_gif_url = res.geturl()

#scrape for the gif and save the image to a folder called mygifs


os.system('image-scraper -s mygifs ' +  redirected_target_gif_url +' --formats gif')


#take image and use it in tesseract to get out the recipe.
#THEN POST IN COMMENT THE RECIPE
