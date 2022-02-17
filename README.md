# What the f is this?
Well, it's just an id3 editor that change metadata based on part of a song.

Powered by [Shazam](https://www.shazam.com)
> Note that it doesn't always identify the right song or can't identify at all

# How to use?
> Before running any of the following, make sure you have ffmpeg in your PATH
```
git clone https://github.com/FoxeiZ/autoID3
pip install -r requirements.txt
cd autoID3
python main.py <moozic folder goes here>
```
Some setting:
  - Change `test` to `True` for a test run

# Dependencies
  - [mutagen](https://github.com/quodlibet/mutagen) - for ID3 edit
  - [ShazamAPI](https://github.com/Numenorean/ShazamAPI) - for you know, send and receive data from Shazam
