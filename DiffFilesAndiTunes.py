import sys
import argparse
import os
import logging
import json
import shutil
import traceback
from log_util import setup_logger2

logger = None
output_dir = None


def load_file_system_songs(file_system_songs):
    with open(file_system_songs, encoding='utf-8') as data_file:
        file_system_songs = json.load(data_file)
    file_system_map = {}
    for track in file_system_songs:
        track_path_lower = track["full_path"].lower()
        if track_path_lower in file_system_map:
            logger.error("this file exists twice in the file system somehow???")
            logger.error("entry1")
            logger.error(str(file_system_map[track_path_lower]))
            logger.error('entry2')
            logger.error(str(track))
            continue
        file_system_map[track_path_lower] = track
    track_names_sorted = sorted(file_system_map.keys())
    return file_system_songs, file_system_map, track_names_sorted


def load_itunes_library_songs(iTunes_Library_songs):
    with open(iTunes_Library_songs, encoding='utf-8') as data_file:
        itunes_libary_songs = json.load(data_file)
    itunes_libary_map = {}
    for track in itunes_libary_songs:
        if not "location" in track:
            logger.error("This track does not contain a location entry")
            logger.error(str(track))
            continue
        path = track["location"].lower()
        if path.find('file://localhost/') < 0:
            logger.error("This track is not on the local computer")
            logger.error(str(track))
            continue
        path = path.replace("file://localhost/","")
        if path in itunes_libary_map:
            logger.error("this file exists twice in the itunes library")
            logger.error("entry1")
            logger.error(str(itunes_libary_map[path]))
            logger.error('entry2')
            logger.error(str(track))
            continue
        itunes_libary_map[path] = track
    track_names_sorted = sorted(itunes_libary_map.keys())
    return itunes_libary_songs, itunes_libary_map, track_names_sorted


def find_missing(songs_sorted, other_song_map, label):
    logger.info("")
    num_missing = 0
    for song_name in songs_sorted:
        if not song_name in other_song_map:
            logger.info("%s missing in %s" %(song_name, label))
            num_missing += 1
    return num_missing

def make_output_file_path(output_dir, filename):
    if len(output_dir) > 0:
        output_path = os.path.join(output_dir, filename)
    else:
        output_path = filename
    return output_path

def Main():
    global logger, output_dir
    app_name = "DiffFilesAndiTunes"

    try:
        good_args = []
        for arg in sys.argv[1:]:
            if (not arg.startswith('#')) and (not arg.startswith('--#')) and (not arg.startswith('-#')):
                good_args.append(arg)

        parser = argparse.ArgumentParser(description=app_name, fromfile_prefix_chars='@')
        parser.add_argument('--file_system_songs', default=None, help="iTunes files on disk", required=True)
        parser.add_argument('--iTunes_Library_songs', default=None, help="iTunes Library songs", required=True)
        parser.add_argument('--outputdir', help="directory where output files get written")
        parser.add_argument('--dump_song_keys', default=False, action="store_true", help="when set, dump keys to files")

        args = parser.parse_args(good_args)

        if args.outputdir:
            output_dir = args.outputdir
        else:
            output_dir = ""
        if len(output_dir) > 0 and not os.path.exists(output_dir):
            os.makedirs(output_dir)
        log_dir = os.path.join(output_dir, "logs")
        if len(log_dir) > 0 and not os.path.exists(log_dir):
            os.makedirs(log_dir)

        logger = setup_logger2(app_name, os.path.join(log_dir, app_name+'.log'), level=logging.DEBUG,
                               console_logging_level=logging.DEBUG,
                               error_log_file=os.path.join(log_dir, app_name + '.excp.log'))

        file_system_songs, file_system_map, file_system_songs_sorted = load_file_system_songs(args.file_system_songs)
        logger.info("Found %d file systems songs on disk" %(len(file_system_songs_sorted)))
        # dump the filenames  if requested
        if args.dump_song_keys:
            file_system_songs_sorted_keys = make_output_file_path(output_dir, "file_system_songs.txt")
            with open(file_system_songs_sorted_keys, "w", encoding='utf-8') as data_file:
                for fname in file_system_songs_sorted:
                    data_file.write(fname+'\n')

        itunes_libary_songs, itunes_libary_map, itunes_libary_songs_sorted = load_itunes_library_songs(args.iTunes_Library_songs)
        logger.info("Found %d itunes songs with %d on disk" %(len(itunes_libary_songs), len(itunes_libary_songs_sorted)))
        # dump the filenames  if requested
        if args.dump_song_keys:
            itunes_libary_songs_sorted_keys = make_output_file_path(output_dir, "iTunes_songs.txt")
            with open(itunes_libary_songs_sorted_keys, "w", encoding='utf-8') as data_file:
                for fname in itunes_libary_songs_sorted:
                    data_file.write(fname+'\n')


        itunes_missing = find_missing(file_system_songs_sorted, itunes_libary_map, "iTunes")
        file_system_missing = find_missing(itunes_libary_songs_sorted, file_system_map, "Disk")
        logger.info("%d missing iTunes entries" %(itunes_missing))
        logger.info("%d missing file system entries" %(file_system_missing))




    except Exception as ex:
        log_func = logger.error if logger else print
        log_func('Got an exception in '+app_name)
        log_func(str(ex))
        log_func(traceback.format_exc())


if __name__ == '__main__':
    Main()