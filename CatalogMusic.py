import os
import sys
import json
import argparse
import logging
from log_util import setup_logger2
import traceback
import shutil
from ReadFilesystemMusic import extract_metadata
from ParseITunesLibrary import parse_itunes_library_file
from WriteLists import write_flat_songs_list, write_flat_albums_list, write_flat_artists_list, \
    write_flat_albums_artists_folder, write_flat_artists_albums_folder, \
    write_nested_albums_folders, write_nested_artists_folders, write_flat_podcast_list, write_podcasts_folder

"""
--song_list_flat
    songs_list.json
    [ 
        {song},
        {song2} 
    ]

--albums_list_flat
    albums_list.json
    [
        {
            album1 [ 
                {song1}, 
                {song2} 
            ]
        }, 
        {
            album2 [ 
                {song1}, 
                {song2} 
            ]
        }
    ]

--artists_list_flat
    artists_list.json
    [
        {
            artist1 [
                {
                    album1 [ 
                        {song1}, 
                        {song2} 
                    ]
                }, 
                {
                    album2 [ 
                        {song1}, 
                        {song2} 
                    ]
                }
            ]
        },
        {
            artist2 [
                {
                    album1 [ 
                        {song1}, 
                        {song2} 
                    ]
                }, 
                {
                    album2 [ 
                        {song1}, 
                        {song2} 
                    ]
                }
            ]
        }
    ]


"""

def strip_quotes_if_needed(input_arg):
    input_arg = input_arg.strip()
    if input_arg[0] == '"' and input_arg[-1] == '"':
        # strip open and closing double quotes
        input_arg = input_arg[1:-1]
    if input_arg[0] == "'" and input_arg[-1] == "'":
        # strip open and closing single quotes
        input_arg = input_arg[1:-1]
    return input_arg


def make_output_file_path(output_dir, filename):
    if len(output_dir) > 0:
        output_path = os.path.join(output_dir, filename)
    else:
        output_path = filename
    return output_path

def ensure_parent_folder_exists(file_path):
    ## since the filename may include pathing information, make sure the final parent directory exists
    output_path = os.path.dirname(file_path)
    if output_path != '' and (not os.path.exists(output_path)):
        os.makedirs(output_path)

def write_output_files(media_files, output_dir, args, logger):
    if args.song_list_flat:
        flat_file_path = make_output_file_path(output_dir, args.song_list_flat)
        write_flat_songs_list(media_files, flat_file_path)

    if args.albums_list_flat:
        flat_albums_path = make_output_file_path(output_dir, args.albums_list_flat)
        write_flat_albums_list(media_files, flat_albums_path)

    if args.artists_list_flat:
        flat_artists_path = make_output_file_path(output_dir, args.artists_list_flat)
        write_flat_artists_list(media_files, flat_artists_path)

    if args.albums_artists_folder_flat:
        flat_albums_artists_folder_path = make_output_file_path(output_dir, args.albums_artists_folder_flat)
        write_flat_albums_artists_folder(media_files, flat_albums_artists_folder_path)

    if args.artists_albums_folder_flat:
        flat_artists_albums_folder_path = make_output_file_path(output_dir, args.artists_albums_folder_flat)
        write_flat_artists_albums_folder(media_files, flat_artists_albums_folder_path)

    if args.albums_nested:
        nested_albums_folder_path = make_output_file_path(output_dir, args.albums_nested)
        write_nested_albums_folders(media_files, nested_albums_folder_path)

    if args.artists_nested:
        nested_artists_folder_path = make_output_file_path(output_dir, args.artists_nested)
        write_nested_artists_folders(media_files, nested_artists_folder_path)


def output_podcast_list(podcast_files, output_dir, args, logger):
    if args.podcast_list_full:
        flat_file_path = make_output_file_path(output_dir, args.podcast_list_full)
        write_flat_songs_list(podcast_files, flat_file_path)

    if args.podcast_list_flat:
        flat_podcast_path = make_output_file_path(output_dir, args.podcast_list_flat)
        write_flat_podcast_list(podcast_files, flat_podcast_path, args.podcast_sort_episodes_reversed)

    if args.podcast_folder:
        podcasts_folder_path = make_output_file_path(output_dir, args.podcast_folder)
        write_podcasts_folder(podcast_files, podcasts_folder_path, args.podcast_folder_csvs, args.podcast_sort_episodes_reversed)



def write_playlist_files(playlists, output_dir, args, logger):
    if args.playlist_flat:
        flat_file_path = make_output_file_path(output_dir, args.playlist_flat)
        write_flat_songs_list(playlists, flat_file_path)

    for index, playlist in enumerate(playlists):
        outpath = playlist["display_path"]
        if outpath[0] == '/':
            outpath = outpath[1:]
        flat_file_path = make_output_file_path(output_dir, outpath+".json")
        ensure_parent_folder_exists(flat_file_path)
        write_flat_songs_list(playlist, flat_file_path)



def Main():
    app_name = "CatalogMusic"

    try:
        good_args = []
        for arg in sys.argv[1:]:
            if (not arg.startswith('#')) and (not arg.startswith('--#')) and (not arg.startswith('-#')):
                good_args.append(arg)

        parser = argparse.ArgumentParser(description='Catalog Music', fromfile_prefix_chars='@')
        parser.add_argument('--itunes_library', default=None, help="itunes library xml file", required=False)
        parser.add_argument('--media_files_dirs', nargs='*')
        parser.add_argument('--media_files_input', default=None, help="json file wtih media files in it", required=False)
        parser.add_argument('--song_list_flat', default="iTunesSongs.json", help="file path for writing a file with all files in it", required=False)
        parser.add_argument('--albums_list_flat', default="Albums_list.json", help="file path for writing a file with all files in it organized by album", required=False)
        parser.add_argument('--artists_list_flat', default="Artists_list.json", help="file path for writing a file with all files in it organized by album", required=False)
        parser.add_argument('--albums_artists_folder_flat', default="Albums_Artists_flat", help="file path for writing a file with all files in it organized by album", required=False)
        parser.add_argument('--artists_albums_folder_flat', default="Artists_Albums_flat", help="file path for writing a file with all files in it organized by album", required=False)
        parser.add_argument('--albums_nested', default="Albums", help="file path for writing a file with all files in it organized by album", required=False)
        parser.add_argument('--artists_nested', default="Artists", help="file path for writing a file with all files in it organized by album", required=False)
        parser.add_argument('--playlist_flat', default="iTunesPlaylists.json", help="file path for writing a file with all playlists in it", required=False)
        parser.add_argument('--podcast_list_full', default="iTunesPodcasts.json", help="file path for writing a file with all files in it", required=False)
        parser.add_argument('--podcast_list_flat', default="podcasts_list.json", help="file path for writing a file with all files in it", required=False)
        parser.add_argument('--podcast_folder', default="Podcasts", help="file path for writing a file with all files in it organized by podcast", required=False)
        parser.add_argument('--podcast_folder_csvs', default=False, action="store_true", help="when set, dump csv files in the podcasts folder")
        parser.add_argument('--podcast_sort_episodes_reversed', nargs='*')
        parser.add_argument('--outputdir', help="directory where output files get written")


        args = parser.parse_args(good_args)

        if args.outputdir:
            output_dir = args.outputdir
        else:
            output_dir = ""

        # do some directory cleanup if needed
        if len(output_dir) > 0 and args.media_files_dirs and not args.media_files_input and os.path.exists(output_dir):
            shutil.rmtree(output_dir)

        # create the output_dir if needed
        if len(output_dir) > 0 and not os.path.exists(output_dir):
            os.makedirs(output_dir)


        log_dir = os.path.join(output_dir, "logs")
        if len(log_dir) > 0 and not os.path.exists(log_dir):
            os.makedirs(log_dir)

        logger = setup_logger2(app_name, os.path.join(log_dir, app_name+'.log'), level=logging.DEBUG,
                               console_logging_level=logging.DEBUG,
                               error_log_file=os.path.join(log_dir, app_name + '.excp.log'))

        media_files = []
        song_list = []
        playlists = []
        movie_list = []
        podcast_list = []
        tvshow_list = []
        audiobook_list = []

        if args.media_files_input:
            media_files_input = strip_quotes_if_needed(args.media_files_input)
            if not os.path.exists(args.media_files_input):
                media_files_input = os.path.join(output_dir, media_files_input)
            with open(media_files_input, encoding='utf-8') as data_file:
                media_files = json.load(data_file)
        elif args.media_files_dirs:
            if not os.path.exists(output_dir):
                os.makedirs(output_dir)
            for media_dir in args.media_files_dirs:
                media_dir = strip_quotes_if_needed(media_dir)
                print(media_dir)
                extract_metadata(media_files, media_dir, logger)
        elif args.itunes_library:
            itunes_library = strip_quotes_if_needed(args.itunes_library)
            song_list, movie_list, podcast_list, tvshow_list, audiobook_list, playlists = parse_itunes_library_file(itunes_library)


        if media_files:
            write_output_files(media_files, output_dir, args, logger)

        def make_output_folder(folder_name):
            item_output_dir = os.path.join(output_dir, folder_name)
            if os.path.exists(item_output_dir):
                shutil.rmtree(item_output_dir)
            os.makedirs(item_output_dir)
            return item_output_dir

        def output_items_list(item_list, folder_name):
            item_output_dir = make_output_folder(folder_name)
            write_output_files(item_list, item_output_dir, args, logger)

        if song_list:
            output_items_list(song_list, "songs")

        if movie_list:
            output_items_list(movie_list, "movies")

        if podcast_list:
            item_output_dir = make_output_folder("podcasts")
            output_podcast_list(podcast_list, item_output_dir, args, logger)
            #output_items_list(podcast_list, "podcasts")

        if tvshow_list:
            output_items_list(tvshow_list, "tvshows")

        if audiobook_list:
            output_items_list(audiobook_list, "audiobooks")

        if playlists:
            playlists_output_dir = make_output_folder("playlists")
            write_playlist_files(playlists, playlists_output_dir, args, logger)

    except Exception as ex:
        log_func = logger.error if logger else print
        log_func('Got an exception in '+app_name)
        log_func(str(ex))
        log_func(traceback.format_exc())


if __name__ == '__main__':
    Main()