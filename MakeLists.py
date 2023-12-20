from iTunesHelper import get_itunes_album_artist, make_album_key, get_itunes_album_name

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

unknown_value = "__UNKNOWN__"
def get_key_Value(dict_inp, key):
    value = dict_inp.get(key, unknown_value)
    if value is None:
        return unknown_value
    else:
        return value

def make_albums_list(media_files):
    albums_dict = {}
    for media_file in media_files:
        album_artist = get_itunes_album_artist(media_file, unknown_value)
        album_name = get_itunes_album_name(media_file, unknown_value)
        album_key = make_album_key(album_name, album_artist)
        if not album_key in albums_dict:
            albums_dict[album_key] = {"album": album_name, "album_artist":album_artist, "songs":[]}
        album_dict = albums_dict[album_key]
        album_dict["songs"].append(media_file)
    albums = []
    #print(albums_dict.keys())
    for album_name in sorted(albums_dict.keys()):
        album_dict = albums_dict[album_name]
        sort_song_list(album_dict["songs"])
        albums.append(album_dict)
    return albums

def make_artists_list(media_files):
    artists_dict = {}
    for media_file in media_files:
        album_artist = get_itunes_album_artist(media_file, unknown_value)
        if not album_artist in artists_dict:
            artists_dict[album_artist] = {"artist": album_artist, "albums": {}}
        artist_dict = artists_dict[album_artist]
        albums_dict = artist_dict["albums"]

        album_name = get_itunes_album_name(media_file, unknown_value)
        if not album_name in albums_dict:
            albums_dict[album_name] = {"album": album_name, "songs": []}
        album_dict = albums_dict[album_name]
        album_dict["songs"].append(media_file)
    artists = []
    #print(artists_dict.keys())
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

def sort_episode_list(episode_list, sort_reversed):
    index = 0
    for episode in episode_list:
        index += 1
        index_str = str(index).zfill(4)
        if "release_date" in episode:
            sort_date = episode["release_date"]
        elif "date_added" in episode:
            sort_date = episode["date_added"]
        elif "date_modified" in episode:
            sort_date = episode["date_modified"]
        else:
            sort_date = "YYYY-MM-DDTHH:MM:SS"
        track_id = str(episode.get("track_id", "9999"))
        episode_sort_key = "%s:%s:%s"%(sort_date, track_id, index_str)
        episode["__sort_key__"] = episode_sort_key
    episode_list.sort(key=lambda k: k["__sort_key__"], reverse=sort_reversed)
    for episode in episode_list:
        del episode["__sort_key__"]

def make_podcast_list(media_files, podcast_sort_episodes_reversed_list):
    # create a map of podcast names for quick lookup
    sort_reversed_map = {}
    for podcast_name in podcast_sort_episodes_reversed_list:
        sort_reversed_map[podcast_name.lower()] = True

    #print("sort map", str(sort_reversed_map))

    podcast_dict = {}
    for media_file in media_files:
        album_name = get_itunes_album_name(media_file, unknown_value)
        if not album_name in podcast_dict:
            podcast_dict[album_name] = {"album": album_name, "episodes":[]}
        album_dict = podcast_dict[album_name]
        album_dict["episodes"].append(media_file)
    podcasts = []
    #print(albums_dict.keys())
    for album_key in sorted(podcast_dict.keys()):
        album_dict = podcast_dict[album_key]
        podcast_name = album_dict["album"]
        #print("'%s' '%s', %s" %(podcast_name, podcast_name.lower(), str(sort_reversed_map.get(podcast_name.lower(),False)) ))
        sort_episode_list(album_dict["episodes"], sort_reversed_map.get(podcast_name.lower(),False))
        podcasts.append(album_dict)
    return podcasts

