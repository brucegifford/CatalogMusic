import os
import json
import traceback

import mutagen
from mutagen.easyid3 import EasyID3
from mutagen.flac import FLAC
from mutagen.mp3 import MP3
from mutagen.mp4 import MP4
from mutagen.oggvorbis import OggVorbis
from mutagen.aiff import AIFF
from mutagen.wave import WAVE

def extract_metadata(media_files, root_dir, logger, base_path = None):
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
            elif ext == '.mp4' or ext == '.m4a':
                audio = MP4(entry.path)
            elif ext == '.flac':
                audio = FLAC(entry.path)
            elif ext == '.aif':
                audio = AIFF(entry.path)
            elif ext == '.wav':
                audio = WAVE(entry.path)
            elif ext == '.ogg':
                audio = OggVorbis(entry.path)
            else:
                continue
            data = {
                'full_path': entry_path,
                'rel_path': relative_path
            }
            for key, value in audio.items():
                """
                if type(value) not in [list, bool, mutagen.id3.TPE2, mutagen.id3.TALB]:
                    print("check this out")
                if key not in ['covr', 'trkn', 'disk'] and type(value) is list:
                    for index, item in enumerate(value):
                        if type(item) not in [str,int,tuple]:
                            print("check this out, key %s, index %d type %s"%(key, index, str(type(item))))
                """
                if type(value) is list and len(value) == 1 and type(value[0]) is mutagen.mp4.MP4FreeForm:
                    logger.error("skipping tag '%s' in file '%s' for now which contains MP4FreeForm key"%(key, entry.path))
                    continue
                elif key == 'covr':
                    logger.error("skipping tag 'covr' in file %s for now"%(entry.path))
                    continue
                elif type(value) is list and len(value) == 1:
                    data[key] = value[0]
                elif type(value) in [mutagen.id3.TPE2, mutagen.id3.TALB] and type(value[0]) is str:
                    data[key] = value[0]
                elif type(value) is list and len(value) > 1:
                    if key == 'genre':
                        data[key] = ','.join(value)
                    else:
                        assert False, "What should we do with this kind of data, type is "+str(type(value))
                elif type(value) is bool:
                    data[key] = value
                else:
                    assert False, "What should we do with this kind of data, type is "+str(type(value))
            media_files.append(data)
        elif entry.is_dir():
            # recurse into the folder
            extract_metadata(media_files, entry_path, logger, base_path)


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