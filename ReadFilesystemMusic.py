import os
import json
import traceback
from mutagen.easyid3 import EasyID3
from mutagen.flac import FLAC
from mutagen.mp3 import MP3
from mutagen.mp4 import MP4
from mutagen.oggvorbis import OggVorbis

def extract_metadata(media_files, root_dir, base_path = None):
    root_dir = os.path.abspath(root_dir)
    root_dir = root_dir.replace('\\', '/')
    if not root_dir.endswith('/'):
        root_dir += '/'
    if base_path == None:
        base_path = root_dir
    base_path_len = len(base_path)
    print("Processing " + root_dir)

    for entry in os.scandir(root_dir):
        entry_path = entry.path.replace('\\', '/')
        relative_path = entry_path[base_path_len:]
        if entry.is_file():
            base, ext = os.path.splitext(entry.name)
            ext = ext.lower()
            if ext == '.mp3':
                audio = MP3(entry.path, ID3=EasyID3)
            elif ext == '.mp4':
                audio = MP4(entry.path)
            elif ext == '.flac':
                audio = FLAC(entry.path)
            elif ext == '.ogg':
                audio = OggVorbis(entry.path)
            else:
                continue
            data = {
                'full_path': entry_path,
                'rel_path': relative_path
            }
            for key, value in audio.items():
                data[key] = value[0]
            media_files.append(data)
        elif entry.is_dir():
            # recurse into the folder
            extract_metadata(media_files, entry_path, base_path)


def Main():
    app_name = "ReadFilesystemMusic"

    try:
        files = extract_metadata(r"C:\Users\bruce\Music\iTunes\iTunes Media\Music")
        print(files)

        with open('iTunesFiles.json', "w", encoding='utf-8') as data_file:
            data_file.write(json.dumps(files, sort_keys=True, indent=4, separators=(',', ': '), ensure_ascii=False))

    except Exception as ex:
        print('Got an exception in '+app_name)
        print(str(ex))
        print(traceback.format_exc())

if __name__ == '__main__':
    Main()