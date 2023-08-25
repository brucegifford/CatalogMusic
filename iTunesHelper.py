def get_itunes_album_artist(song_dict, missing_value = None):
    if song_dict.get("compilation", False) == True:
        album_artist = "Compilations"
    else:
        album_artist = song_dict.get("album_artist",None)
        if album_artist is None:
            album_artist = song_dict.get("artist", missing_value)
    return album_artist

def make_album_key(album_name, album_artist):
    return album_name +'|'+ album_artist