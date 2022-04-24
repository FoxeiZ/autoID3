from ShazamAPI import Shazam
import os
import sys
import subprocess as sp
from pathlib import Path
from mutagen.mp3 import MP3
from mutagen.easyid3 import EasyID3
import mutagen.id3


def main(item, test=False):
    audiofile = MP3(item, ID3=EasyID3)

    if audiofile.info.length > 35.0:
        pipe = sp.run(['ffmpeg', '-y', '-i', item, '-vn', '-ss', '00:00:35', '-to', '00:00:55', '-f', 'mp3', 'pipe:1', '-hide_banner', '-loglevel', 'warning'], stdout=sp.PIPE)
        mp3_file = pipe.stdout
    else:
        mp3_file = open(item, 'rb').read()

    try:
        audiofile.add_tags(ID3=EasyID3)
    except mutagen.id3.error:
        pass

    shazam = Shazam(mp3_file, lang='us').recognizeSong()
    data = next(shazam)

    if not data[1]['matches']:
        print(item, ': cant find metadata for this song\n')
        error += 1
        return

    try:
        print(f"{item} -> {data[1]['track']['subtitle']} - {data[1]['track']['title']}.mp3\n")

        if test:
            return

        # check for existing metadata
        if not audiofile['title']:
            print('start writing tag...')
            audiofile['artist'] = data[1]['track']['subtitle']
            audiofile['title']  = data[1]['track']['title']
            audiofile['album']  = data[1]['track']['sections'][0]['metadata'][0]['text']
            audiofile['genre']  = data[1]['track']['genres']['primary']
            # close eyeD3 editor
            audiofile.save()
            print('done!\n')

        # change filename
        os.rename(item, os.path.join(sys.argv[1], f"{data[1]['track']['subtitle']} - {data[1]['track']['title']}.mp3"))

    except KeyError:
        print('missing data, skipping!\n')
        error += 1
        return


if __name__ == '__main__':
    error = 0
    path = Path(sys.argv[1])

    if path.is_dir():
        for item in path.glob('*.mp3'):
            main(item)
    else:
        main(path)

    print('total error: ', error)
