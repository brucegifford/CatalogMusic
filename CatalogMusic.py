import os
import sys
import json
import argparse
import logging
from log_util import setup_logger2
import traceback
from ReadFilesystemMusic import extract_metadata
from WriteLists import write_flat_songs_list, write_flat_albums_list, write_flat_artists_list, \
    write_flat_albums_artists_folder, write_flat_artists_albums_folder, \
    write_nested_albums_folders, write_nested_artists_folders

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
def make_output_file_path(output_dir, filename):
    if len(output_dir) > 0:
        output_path = os.path.join(output_dir, filename)
    else:
        output_path = filename
    return output_path

def Main():
    app_name = "CatalogMusic"

    try:
        good_args = []
        for arg in sys.argv[1:]:
            if (not arg.startswith('#')) and (not arg.startswith('--#')) and (not arg.startswith('-#')):
                good_args.append(arg)

        parser = argparse.ArgumentParser(description='Catalog Music', fromfile_prefix_chars='@')
        parser.add_argument('--media_files_dirs', nargs='*')
        parser.add_argument('--media_files_input', default=None, help="json file wtih media files in it", required=False)
        parser.add_argument('--song_list_flat', default=None, help="file path for writing a file with all files in it", required=False)
        parser.add_argument('--albums_list_flat', default=None, help="file path for writing a file with all files in it organized by album", required=False)
        parser.add_argument('--artists_list_flat', default=None, help="file path for writing a file with all files in it organized by album", required=False)
        parser.add_argument('--albums_artists_folder_flat', default=None, help="file path for writing a file with all files in it organized by album", required=False)
        parser.add_argument('--artists_albums_folder_flat', default=None, help="file path for writing a file with all files in it organized by album", required=False)
        parser.add_argument('--albums_nested', default=None, help="file path for writing a file with all files in it organized by album", required=False)
        parser.add_argument('--artists_nested', default=None, help="file path for writing a file with all files in it organized by album", required=False)
        parser.add_argument('--outputdir', help="directory where output files get written")


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

        media_files = []
        if args.media_files_input:
            if os.path.exists(args.media_files_input):
                media_files_input = args.media_files_input
            else:
                media_files_input = os.path.join(output_dir, args.media_files_input)
            with open(media_files_input, encoding='utf-8') as data_file:
                media_files = json.load(data_file)
        elif args.media_files_dirs:
            for media_dir in args.media_files_dirs:
                print(media_dir)
                extract_metadata(media_files, media_dir)

        if media_files:
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



    except Exception as ex:
        log_func = logger.error if logger else print
        log_func('Got an exception in '+app_name)
        log_func(str(ex))
        log_func(traceback.format_exc())


if __name__ == '__main__':
    Main()