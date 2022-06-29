# Tweet Pi

## Search keywords on twitter and display them on a 2.7" waveshare e-paper screen

### Requirements

* Raspberry Pi Zero W (or similar)

* Waveshare 2.7 inch e-Paper Hat

* Power Supply

To get started make sure you follow the guide on [Waveshare](https://www.waveshare.com/wiki/2.7inch_e-Paper_HAT) to ensure you have all the required drivers. Waveshare demos all require sudo so this was built with that in mind.

You will also need Twitter API access to get a bearer token.

1. Use the requirements.txt as sudo to pip install needed packages
2. Create a .env file and add your Twitter API bearer token as BEARER=<your_token>
3. Launch the program with sudo python3 tweet_pi.py from the tweet_pi folder
4. Type in a Search Term
5. Press Key 1 on the HAT once it has initilized to display tweet.
6. Tweets will cycle through until the limit (or total amount of tweets found) and the restart at the beginning
7. Press Key 2 on the HAT to clear the screen and exit.

Enjoy!

### Example

<https://user-images.githubusercontent.com/5252508/176463872-f2edc484-3e24-4c57-ad45-67d60f5e5b8a.mp4>
