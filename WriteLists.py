import json
import os
import shutil
from datetime import date, datetime
import csv

from MakeLists import make_albums_list, make_artists_list, make_podcast_list
from iTunesHelper import make_legal_filename, get_artist_folder_truncated_if_needed, get_album_folder_truncated_if_needed

def json_serial(obj):
    """JSON serializer for objects not serializable by default json code"""

    if isinstance(obj, (datetime, date)):
        return obj.isoformat()
    raise TypeError ("Type %s not serializable" % type(obj))

def write_json_file(json_data, file_path, encoding='utf-8'):
    with open(file_path, "w", encoding=encoding) as data_file:
        data_file.write(json.dumps(json_data, sort_keys=True, indent=4, separators=(',', ': '), ensure_ascii=False, default=json_serial))

def write_flat_songs_list(media_files, flat_songs_path):
    write_json_file(media_files, flat_songs_path)

def write_flat_albums_list(media_files, flat_albums_path):
    albums_list_flat = make_albums_list(media_files)
    write_json_file(albums_list_flat, flat_albums_path)

def write_flat_artists_list(media_files, flat_artists_path):
    artists_list_flat = make_artists_list(media_files)
    write_json_file(artists_list_flat, flat_artists_path)

def write_flat_albums_artists_folder(media_files, flat_albums_artists_folder_path):
    if os.path.exists(flat_albums_artists_folder_path):
        shutil.rmtree(flat_albums_artists_folder_path)
    os.makedirs(flat_albums_artists_folder_path, exist_ok=True)
    artists_list = make_artists_list(media_files)
    for artist in artists_list:
        artist_name = artist["artist"]
        artist_name = make_legal_filename(artist_name)
        for album in artist["albums"]:
            album_name = album["album"]
            album_name = make_legal_filename(album_name)
            filename = "%s^%s.json" % (album_name, artist_name)
            filepath = os.path.join(flat_albums_artists_folder_path, filename)
            write_json_file(album, filepath)

def write_flat_artists_albums_folder(media_files, flat_artists_albums_folder_path):
    if os.path.exists(flat_artists_albums_folder_path):
        shutil.rmtree(flat_artists_albums_folder_path)
    os.makedirs(flat_artists_albums_folder_path, exist_ok=True)
    artists_list = make_artists_list(media_files)
    for artist in artists_list:
        artist_name = artist["artist"]
        artist_name = make_legal_filename(artist_name)
        for album in artist["albums"]:
            album_name = album["album"]
            album_name = make_legal_filename(album_name)
            filename = "%s^%s.json" % (artist_name, album_name)
            filepath = os.path.join(flat_artists_albums_folder_path, filename)
            write_json_file(album, filepath)

def write_nested_albums_folders(media_files, nested_albums_folder_path):
    if os.path.exists(nested_albums_folder_path):
        shutil.rmtree(nested_albums_folder_path)
    os.makedirs(nested_albums_folder_path, exist_ok=True)
    artists_list = make_artists_list(media_files)
    for artist in artists_list:
        artist_name = artist["artist"]
        artist_name = get_artist_folder_truncated_if_needed(artist_name)
        artist_name = make_legal_filename(artist_name)
        for album in artist["albums"]:
            album_name = album["album"]
            album_name = get_album_folder_truncated_if_needed(album_name)
            album_name = make_legal_filename(album_name)
            album_path = os.path.join(nested_albums_folder_path, album_name)
            os.makedirs(album_path, exist_ok=True)
            filename = "%s^%s.json" % (album_name, artist_name)
            filepath = os.path.join(album_path, filename)
            write_json_file(album, filepath)

def write_nested_artists_folders(media_files, nested_artists_folder_path):
    if os.path.exists(nested_artists_folder_path):
        shutil.rmtree(nested_artists_folder_path)
    os.makedirs(nested_artists_folder_path, exist_ok=True)
    artists_list = make_artists_list(media_files)
    for artist in artists_list:
        artist_name = artist["artist"]
        artist_name = get_artist_folder_truncated_if_needed(artist_name)
        artist_name = make_legal_filename(artist_name)
        artist_path = os.path.join(nested_artists_folder_path, artist_name)
        os.makedirs(artist_path, exist_ok=True)
        for album in artist["albums"]:
            album_name = album["album"]
            album_name = get_album_folder_truncated_if_needed(album_name)
            album_name = make_legal_filename(album_name)
            """
            album_path = os.path.join( artist_path, album_name )
            os.makedirs(album_path, exist_ok=True)
            """
            filename = "%s.json" % (album_name)
            """
            filepath = os.path.join(album_path, filename)
            """
            filepath = os.path.join(artist_path, filename)
            write_json_file(album, filepath)

def write_flat_podcast_list(media_files, flat_podcasts_path, podcast_sort_episodes_reversed):
    podcasts_list_flat = make_podcast_list(media_files, podcast_sort_episodes_reversed)
    write_json_file(podcasts_list_flat, flat_podcasts_path)

def write_podcasts_folder(media_files, nested_podcasts_folder_path, write_podcast_folder_csvs, podcast_sort_episodes_reversed):
    if os.path.exists(nested_podcasts_folder_path):
        shutil.rmtree(nested_podcasts_folder_path)
    os.makedirs(nested_podcasts_folder_path, exist_ok=True)
    podcasts_list = make_podcast_list(media_files, podcast_sort_episodes_reversed)
    for podcast_dict in podcasts_list:
        album_name = podcast_dict["album"]
        album_name = get_album_folder_truncated_if_needed(album_name)
        album_name = make_legal_filename(album_name)
        filename = "%s.json" % (album_name)
        podcast_path = os.path.join(nested_podcasts_folder_path, filename)
        write_json_file(podcast_dict, podcast_path)

        # now write a csv versoin of the file
        csv_filename = "%s.csv" % (album_name)
        csv_podcast_path = os.path.join(nested_podcasts_folder_path, csv_filename)

        if write_podcast_folder_csvs:
            keys = set().union(*(d.keys() for d in podcast_dict["episodes"]))
            with open(csv_podcast_path, 'w', encoding='utf8', newline='') as output_file:
                fc = csv.DictWriter(output_file, fieldnames=keys,)
                fc.writeheader()
                fc.writerows(podcast_dict["episodes"])

