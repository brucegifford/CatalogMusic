def sort_song_list(song_list):
    index = 0
    for song in song_list:
        index += 1
        index_str = str(index).zfill(4)
        disc_num = song.get("discnumber", "1")
        if disc_num:
            parts = disc_num.split('/')
            disc_num = parts[0]
        disc_num = str(disc_num).zfill(4)
        tracknumber = song.get("tracknumber", "1")
        if tracknumber:
            parts = tracknumber.split('/')
            tracknumber = parts[0]
        tracknumber = str(tracknumber).zfill(4)
        song_sort_key = "%s:%s:%s"%(disc_num, tracknumber, index_str)
        song["__sort_key__"] = song_sort_key
    song_list.sort(key=lambda k: k["__sort_key__"])
    for song in song_list:
        del song["__sort_key__"]

def make_albums_list(media_files):
    albums_dict = {}
    for media_file in media_files:
        album_name = media_file.get("album", "__UNKNOWN__")
        if not album_name in albums_dict:
            albums_dict[album_name] = {"album": album_name, "songs":[]}
        album_dict = albums_dict[album_name]
        album_dict["songs"].append(media_file)
    albums = []
    for album_name in sorted(albums_dict.keys()):
        album_dict = albums_dict[album_name]
        sort_song_list(album_dict["songs"])
        albums.append(album_dict)
    return albums

def make_artists_list(media_files):
    artists_dict = {}
    for media_file in media_files:
        artist_name = media_file.get("artist", "__UNKNOWN__")
        if not artist_name in artists_dict:
            artists_dict[artist_name] = {"artist": artist_name, "albums": {}}
        artist_dict = artists_dict[artist_name]
        albums_dict = artist_dict["albums"]

        album_name = media_file.get("album", "__UNKNOWN__")
        if not album_name in albums_dict:
            albums_dict[album_name] = {"album": album_name, "songs": []}
        album_dict = albums_dict[album_name]
        album_dict["songs"].append(media_file)
    artists = []
    for artist_name in sorted(artists_dict.keys()):
        artist_dict_orig = artists_dict[artist_name]
        artist_dict = {
            "artist": artist_dict_orig["artist"],
            "albums": []
        }
        for album_name in sorted(artist_dict_orig["albums"].keys()):
            album_dict = artist_dict_orig["albums"][album_name]
            sort_song_list(album_dict["songs"])
            artist_dict["albums"].append(album_dict)
        artists.append(artist_dict)
    return artists

