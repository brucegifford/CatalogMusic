import json
import os
from MakeLists import make_albums_list, make_artists_list

def make_legal_filename(filename):
    for char in "/\\:*?\"'<>|[]":
        filename = filename.replace(char, '_')
    filename = filename.strip(', _.')
    return filename


def write_flat_songs_list(media_files, flat_songs_path):
    with open(flat_songs_path, "w", encoding='utf-8') as data_file:
        data_file.write(json.dumps(media_files, sort_keys=True, indent=4, separators=(',', ': '), ensure_ascii=False))

def write_flat_albums_list(media_files, flat_albums_path):
    albums_list_flat = make_albums_list(media_files)
    with open(flat_albums_path, "w", encoding='utf-8') as data_file:
        data_file.write(json.dumps(albums_list_flat, sort_keys=True, indent=4, separators=(',', ': '), ensure_ascii=False))

def write_flat_artists_list(media_files, flat_artists_path):
    artists_list_flat = make_artists_list(media_files)
    with open(flat_artists_path, "w", encoding='utf-8') as data_file:
        data_file.write(json.dumps(artists_list_flat, sort_keys=True, indent=4, separators=(',', ': '), ensure_ascii=False))

def write_flat_albums_artists_folder(media_files, flat_albums_artists_folder_path):
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
            with open(filepath, "w", encoding='utf-8') as data_file:
                data_file.write(json.dumps(album, sort_keys=True, indent=4, separators=(',', ': '), ensure_ascii=False))

def write_flat_artists_albums_folder(media_files, flat_artists_albums_folder_path):
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
            with open(filepath, "w", encoding='utf-8') as data_file:
                data_file.write(json.dumps(album, sort_keys=True, indent=4, separators=(',', ': '), ensure_ascii=False))

def write_nested_albums_folders(media_files, nested_albums_folder_path):
    os.makedirs(nested_albums_folder_path, exist_ok=True)
    artists_list = make_artists_list(media_files)
    for artist in artists_list:
        artist_name = artist["artist"]
        artist_name = make_legal_filename(artist_name)
        for album in artist["albums"]:
            album_name = album["album"]
            album_name = make_legal_filename(album_name)
            album_path = os.path.join(nested_albums_folder_path, album_name)
            os.makedirs(album_path, exist_ok=True)
            filename = "%s^%s.json" % (album_name, artist_name)
            filepath = os.path.join(album_path, filename)
            with open(filepath, "w", encoding='utf-8') as data_file:
                data_file.write(json.dumps(album, sort_keys=True, indent=4, separators=(',', ': '), ensure_ascii=False))

def write_nested_artists_folders(media_files, nested_artists_folder_path):
    os.makedirs(nested_artists_folder_path, exist_ok=True)
    artists_list = make_artists_list(media_files)
    for artist in artists_list:
        artist_name = artist["artist"]
        artist_name = make_legal_filename(artist_name)
        artist_path = os.path.join(nested_artists_folder_path, artist_name)
        os.makedirs(artist_path, exist_ok=True)
        for album in artist["albums"]:
            album_name = album["album"]
            album_name = make_legal_filename(album_name)
            filename = "%s^%s.json" % (artist_name, album_name)
            filepath = os.path.join(artist_path, filename)
            with open(filepath, "w", encoding='utf-8') as data_file:
                data_file.write(json.dumps(album, sort_keys=True, indent=4, separators=(',', ': '), ensure_ascii=False))
