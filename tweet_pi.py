#!/usr/bin/python
# -*- coding:utf-8 -*-
import sys
import os
import shutil

picdir = os.path.join(os.path.dirname(os.path.realpath(__file__)), 'imgs')
libdir = os.path.join(os.path.dirname(os.path.realpath(__file__)), 'utils')

if os.path.exists(libdir):
    sys.path.append(libdir)

from waveshare_epd import epd2in7
from dotenv import load_dotenv
import urllib.parse
import tweepy
import requests
import textwrap

from PIL import Image,ImageDraw,ImageFont

import RPi.GPIO as GPIO
import time

epd = epd2in7.EPD()
font24 = ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf', 24)
font12 = ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf', 12)
font35 = ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf', 35)
NEW_TWEET = 5
STOP=6

# Load Twitter API Environment Variables
load_dotenv()
bearer = os.getenv('BEARER')

tweetinfo = []
def get_tweets():
    auth = tweepy.OAuth2BearerHandler(bearer)
    api = tweepy.API(auth)  
    search_term = urllib.parse.quote(input('Search term: '))
    public_tweets = api.search_tweets(q=search_term, lang='en', count=30)

    for tweet in public_tweets:
        profile_picture = get_profile_image(tweet)
        formatted_tweet = textwrap.fill(tweet.text, width=26)
        tweetinfo.append([formatted_tweet, tweet.user.screen_name , profile_picture])

# Grab twitter profile image and convert to bmp
def get_profile_image(info):
    image_urls = info.user.profile_image_url
    file_name = info.user.screen_name
    download_image = requests.get(image_urls)

    if download_image.status_code == 200:
        pass
    else:
        download_image = requests.get('https://abs.twimg.com/sticky/default_profile_images/default_profile_normal.png')

    if '.png' in download_image.url:
        downloaded = open(os.path.join(picdir, f'{file_name}.png'), 'wb+')
    else:
        downloaded = open(os.path.join(picdir, f'{file_name}.jpg'), 'wb+')
    downloaded.write(download_image.content)
    downloaded.close()
    if '.png' in download_image.url:
        bmp = Image.open(os.path.join(picdir, f'{file_name}.png')).convert('RGB')
    else:
        bmp = Image.open(os.path.join(picdir, f'{file_name}.jpg')).convert('RGB')
    bmp.save(os.path.join(picdir, f'{file_name}.bmp'))
    bmp.close()
    return f'{file_name}.bmp'
        

# Display current_tweet based on counter
def display_tweet(ctweet):
    Himage = Image.new('L', (epd.height, epd.width), 255)  # 255: clear the frame
    if 'default_profile_normal.bmp' in ctweet[2]:
        img = Image.open(os.path.join(picdir, f'/default/{ctweet[2]}'))
    else:
        img = Image.open(os.path.join(picdir, ctweet[2]))
    Himage.paste(img, (10, 10, 10 + img.size[0], 10 + img.size[1]))
    draw = ImageDraw.Draw( Himage)
    draw.multiline_text((70, 10), ctweet[0], font = font12, fill = epd.GRAY4)
    textbox_size = draw.textbbox((75,10),ctweet[0], font = font12)
    draw.text((70, textbox_size[3]+10), f'@{ctweet[1]}', font = font12, fill = epd.GRAY4)
    epd.display_4Gray(epd.getbuffer_4Gray(Himage))

# Get waveshare screen functional
def init_screen():
    try:
        epd.init()
        epd.Clear(0xFF)
        epd.Init_4Gray()
            
    except IOError as e:
        print(e)
        
    except KeyboardInterrupt:    
        epd2in7.epdconfig.module_exit()
        exit()

# Cleanly end program on button press
def stop_program():
    epd.Clear(0xFF)
    epd2in7.epdconfig.module_exit()

    # Delete all the image files for clean slate on next startup
    for file in os.listdir(picdir):
        if file.endswith(".bmp") or file.endswith(".jpg") or file.endswith(".png"):
            os.remove(os.path.join(picdir, file))
    GPIO.cleanup()
    exit()

# pin numbers are interpreted as BCM pin numbers.
GPIO.setmode(GPIO.BCM)
# Sets the pin as input and sets Pull-up mode for the pin.
GPIO.setup(NEW_TWEET,GPIO.IN,GPIO.PUD_UP)
GPIO.setup(STOP,GPIO.IN,GPIO.PUD_UP)

# Start tweet retrieval
get_tweets()

# Initiate waveshare screen
init_screen()

# Set tweet cycle counter to 0
current_tweet = 0
while True:
    time.sleep(0.05)
    # Returns the value read at the given pin. It will be HIGH or LOW (0 or 1).
    if GPIO.input(NEW_TWEET) == 0:
        try:
            print(tweetinfo[current_tweet])
            display_tweet(tweetinfo[current_tweet])
        except:
            print('No tweets found')
        # Increment tweet counter if less than total count of tweets
        if current_tweet < len(tweetinfo)-1:
            current_tweet += 1
        else:
            current_tweet = 0
        while GPIO.input(NEW_TWEET) == 0:
            time.sleep(0.01)
    # Exit Program on Button Click
    if GPIO.input(STOP) == 0:
        stop_program()