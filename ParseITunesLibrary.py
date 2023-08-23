import xml.etree.ElementTree as ET
from datetime import datetime
import IReadiTunes as irit



def parse_itunes_library_file(itunes_library_file):
    """
    Parse iTunes Library.xml file and extract data for each entry.

    Args:
        xml_file_path (str): The path to the iTunes Library.xml file.

    Returns:
        list: A list of dictionaries, where each dictionary represents an entry in the iTunes Library.
    """

    # First of all, init the library
    my_lib = irit.lib_init()

    # Read iTunes XML file
    my_lib.parse(itunes_library_file)

    song_list = []
    for song in my_lib.get_song_list():
        song_list.append(song.get_as_dict())

    movie_list = []
    for movie in my_lib.get_movie_list():
        movie_list.append(movie.get_as_dict())

    podcast_list = []
    for podcast in my_lib.get_podcast_list():
        podcast_list.append(podcast.get_as_dict())

    tvshow_list = []
    for tvshow in my_lib.get_tvshow_list():
        tvshow_list.append(tvshow.get_as_dict())

    audiobook_list = []
    for audiobook in my_lib.get_audiobook_list():
        audiobook_list.append(audiobook.get_as_dict())


    playlists = []
    for playlist in my_lib.get_playlists():
        playlists.append(playlist.get_as_dict(add_distingished_kind_label=True))

    return song_list, movie_list, podcast_list, tvshow_list, audiobook_list, playlists
