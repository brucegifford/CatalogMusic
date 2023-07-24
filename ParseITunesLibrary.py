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
    for track in my_lib.get_track_list():
        song_list.append(track.get_as_dict())

    playlists = []
    for playlist in my_lib.get_playlists():
        playlists.append(playlist.get_as_dict())

    return song_list, playlists
