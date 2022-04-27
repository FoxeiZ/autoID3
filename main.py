import argparse
import os
from pathlib import Path

from mutagen.mp3 import MP3
from mutagen.easyid3 import EasyID3
import mutagen.id3

from ShazamAPI import Shazam


class MissingData(Exception):
    pass


class NoData(Exception):
    pass


def confirmation(switch):
    if not switch:
        return True

    if input("Do you want to save change [y/n] ").lower() == "y":
        return True
    else:
        return False


def main(item, dry_run=False, confirm=False):
    audiofile = MP3(item, ID3=EasyID3)

    if audiofile.info.length > 35.0:
        with open(item, "rb") as temp:
            temp.seek(580685)  # 35secs ? | just estimate
            mp3_file = temp.read(420685)  # 25secs ?
    else:
        mp3_file = open(item, "rb").read()

    try:
        audiofile.add_tags(ID3=EasyID3)
    except mutagen.id3.error:
        pass

    shazam = Shazam(mp3_file, lang="us").recognizeSong()
    data = next(shazam)
    data = data[1]

    if not data["matches"]:
        raise NoData(f"{item}: cant find metadata for this song")

    try:
        print(f"\n{item} -> {data['track']['subtitle']} - {data['track']['title']}.mp3")

        if dry_run:
            return

        # check for existing metadata
        if confirmation(confirm):
            print("start writing tag...")
            audiofile["artist"] = data["track"]["subtitle"]
            audiofile["title"] = data["track"]["title"]
            audiofile["album"] = data["track"]["sections"][0]["metadata"][0].get("text", None)
            audiofile["genre"] = data["track"]["genres"]["primary"]
            # close eyeD3 editor
            audiofile.save()

            # change filename
            os.rename(
                item,
                item.with_name(
                    f"{data['track']['subtitle']} - {data['track']['title']}.mp3",
                ),
            )

    except KeyError:
        raise MissingData("missing data, skipping!")


if __name__ == "__main__":

    parser = argparse.ArgumentParser(
        description="An ID3 editor that change metadata based on part of a song.",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
    )

    parser.add_argument(
        "path",
        metavar="PATH",
        type=Path,
        nargs="+",
        help='It can be either a path to a folder or a file.',
    )

    parser.add_argument(
        "--dry-run",
        action="store_true",
        help='Do a trial run with no permanent changes',
    )

    parser.add_argument(
        "--wait-for-confirmation",
        action="store_true",
        dest="confirm",
        help='Show the confirmation before making any changes',
    )

    error = 0
    args = parser.parse_args()

    for path in args.path:
        if path.is_dir():
            for item in path.glob("*.mp3"):
                try:
                    main(item, args.dry_run, args.confirm)
                except (NoData, MissingData) as err:
                    print(f"{err.__class__.__name__} | {err}")
                    error += 1
        else:
            try:
                main(path, args.dry_run, args.confirm)
            except (NoData, MissingData) as err:
                print(f"{err.__class__.__name__} | {err}")
                error += 1

    print("total error: ", error)
