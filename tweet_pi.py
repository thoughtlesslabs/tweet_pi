#!/usr/bin/python
# -*- coding:utf-8 -*-
import sys
import os
import shutil

picdir = os.path.join(os.path.dirname(os.path.realpath(__file__)), 'imgs')
libdir = os.path.join(os.path.dirname(os.path.realpath(__file__)), 'utils')

if os.path.exists(libdir):
    sys.path.append(libdir)

import logging
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
font14 = ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf', 14)
font35 = ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf', 35)
NEW_TWEET = 5
STOP=6

load_dotenv()

bearer = os.getenv('BEARER')

tweetinfo = []
def get_tweets():
    auth = tweepy.OAuth2BearerHandler(bearer)
    api = tweepy.API(auth)  
    print(api)
    search_term = urllib.parse.quote(input('Search term: '))
    public_tweets = api.search_tweets(q=search_term, count=20)

    for tweet in public_tweets:
        profile_picture = get_profile_image(tweet)
        formatted_tweet = textwrap.fill(tweet.text, width=20)
        tweetinfo.append([formatted_tweet, tweet.user.screen_name , profile_picture])

def get_profile_image(info):
    image_urls = info.user.profile_image_url
    file_name = info.user.screen_name
    download_image = requests.get(image_urls)
    downloaded = open(f'imgs/{file_name}.jpg', 'wb+')
    downloaded.write(download_image.content)
    downloaded.close()
    bmp = Image.open(f'imgs/{file_name}.jpg')
    bmp.convert('RGB')
    bmp.save(f'imgs/{file_name}.bmp')
    bmp.close()
    return f'{file_name}.bmp'


def display_tweet(ctweet):
    print(ctweet)
    print(len(tweetinfo))
    Himage = Image.new('L', (epd.height, epd.width), 255)  # 255: clear the frame
    img = Image.open(os.path.join(picdir, ctweet[2]))
    Himage.paste(img, (10, 10, 10 + img.size[0], 10 + img.size[1]))
    draw = ImageDraw.Draw( Himage)
    draw.multiline_text((75, 10), ctweet[0], font = font14, fill = epd.GRAY4)
    textbox_size = draw.textbbox((75,10),ctweet[0], font = font14)
    draw.text((75, textbox_size[3]+10), f'{ctweet[1]}', font = font14, fill = epd.GRAY4)
    epd.display_4Gray(epd.getbuffer_4Gray(Himage))

def init_screen():
    try:

        logging.info("epd2in7 Demo")   
        
        '''2Gray(Black and white) display'''
        logging.info("init and Clear")
        epd.init()
        epd.Clear(0xFF)

        '''4Gray display'''
        logging.info("4Gray display--------------------------------")
        epd.Init_4Gray()
            
    except IOError as e:
        logging.info(e)
        
    except KeyboardInterrupt:    
        logging.info("ctrl + c:")
        epd2in7.epdconfig.module_exit()
        exit()

def stop_program():
    epd.Clear(0xFF)
    epd2in7.epdconfig.module_exit()
    folder = 'imgs'
    for filename in os.listdir(folder):
        file_path = os.path.join(folder, filename)
        try:
            if os.path.isfile(file_path) or os.path.islink(file_path):
                os.unlink(file_path)
            elif os.path.isdir(file_path):
                shutil.rmtree(file_path)
        except Exception as e:
            print('Failed to delete %s. Reason: %s' % (file_path, e))
    GPIO.cleanup()
    exit()

# pin numbers are interpreted as BCM pin numbers.
GPIO.setmode(GPIO.BCM)
# Sets the pin as input and sets Pull-up mode for the pin.
GPIO.setup(NEW_TWEET,GPIO.IN,GPIO.PUD_UP)
GPIO.setup(STOP,GPIO.IN,GPIO.PUD_UP)
get_tweets()
init_screen()
current_tweet = 0
while True:
    time.sleep(0.05)
    # Returns the value read at the given pin. It will be HIGH or LOW (0 or 1).
    if GPIO.input(NEW_TWEET) == 0:
        display_tweet(tweetinfo[current_tweet])
        if current_tweet < len(tweetinfo)-1:
            current_tweet += 1
        else:
            current_tweet = 0
        while GPIO.input(NEW_TWEET) == 0:
            time.sleep(0.01)
    if GPIO.input(STOP) == 0:
        stop_program()