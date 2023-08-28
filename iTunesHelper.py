
# these are the various keys used by mp3, mp4 and itunes
complilation_keys = ["compilation", "cpil"]
album_artist_keys = ["album_artist", "albumartist", "aART"]
artist_keys = ["artist", "©ART"]

def get_itunes_album_artist(song_dict, missing_value = None):
    # first check if this is a compilation, if so it goes in the Compilations folder/artist
    for compilation_key in complilation_keys:
        if song_dict.get(compilation_key,False) in [True, "True", "true", "1", 1]:
            return "Compilations"

    # otherwise, see if the song lists an explicit album artist
    for album_artist_key in album_artist_keys:
        album_artist = song_dict.get(album_artist_key, None)
        if album_artist:
            return album_artist

    # otherwise, look for an explicit artist key
    for artist_key in artist_keys:
        artist_name = song_dict.get(artist_key, None)
        if artist_name:
            return artist_name

    # otherwise, look at the artist
    return missing_value


album_name_keys = ["album", "©alb"]
def get_itunes_album_name(song_dict, missing_value = None):
    # otherwise, see if the song lists an explicit album artist
    for album_name_key in album_name_keys:
        album_name = song_dict.get(album_name_key, None)
        if album_name:
            return album_name
    return missing_value

def make_album_key(album_name, album_artist):
    return album_name +'|'+ album_artist

def make_legal_filename(filename):
    for char in "/\\:*?\"<>|’":
        filename = filename.replace(char, '_')
    filename = filename.strip(', ')
    if filename[-1] == '.':
        filename = filename[:-1] + '_'
    return filename


