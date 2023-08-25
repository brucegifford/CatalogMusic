import sys
import argparse
import os
import logging
import json
import shutil
import traceback
from log_util import setup_logger2
from iTunesHelper import get_itunes_album_artist, make_album_key

logger = None
output_dir = None
ignores_data = {}

def load_ignores(ignores_file):
    global ignores_data
    with open(ignores_file, encoding='utf-8') as data_file:
        ignores_data = json.load(data_file)


def update_locations(song_list):
    for song in song_list:
        if not "location" in song:
            return False
        path = song["location"].lower()
        path = path.replace("file://localhost/", "")
        song["location"] = path
    return True


def load_itunes_albums(itunes_albums_file):
    with open(itunes_albums_file, encoding='utf-8') as data_file:
        itunes_albums = json.load(data_file)
    album_map = {}
    album_names_sorted = []
    for album in itunes_albums:
        album_name = album["album"]
        album_artist = album["album_artist"]
        album_key = make_album_key(album_name, album_artist)
        if album_key in album_map:
            logger.error("this album exists twice in iTunes somehow???")
            logger.error("entry1")
            logger.error(str(album_map[album_key]))
            logger.error('entry2')
            logger.error(str(album))
            continue

        if not update_locations(album["songs"]):
            continue

        album_map[album_key] = album
        album_names_sorted.append(album_name)
    album_names_sorted.sort()
    return itunes_albums, album_map, album_names_sorted


def load_itunes_playlists(itunes_playlists_file):
    with open(itunes_playlists_file, encoding='utf-8') as data_file:
        itunes_playlists_raw = json.load(data_file)
    itunes_playlists = []
    playlist_names_sorted = []
    for playlist in itunes_playlists_raw:
        # don't look at the master list
        if playlist.get("master",False):
            continue
        # don't look at Downloaded lists
        if playlist["name"] in [ "Downloaded", "Genius", "Music", "Podcasts", "Purchased", "Voice Memos" ]:
            continue
        # don't look at tv_shows
        if playlist.get("tv_shows",False):
            continue
        # don't look at movies
        if playlist.get("movies",False):
            continue
        # don't look at audiobooks
        if playlist.get("audiobooks",False):
            continue
        # don't look at folders
        if playlist.get("folder",False):
            continue
        update_locations(playlist["tracks"])
        itunes_playlists.append(playlist)
        playlist_name = playlist["name"]
        playlist_names_sorted.append(playlist_name)
        """
        if playlist_name in itunes_playlists_map:
            logger.error("this playlist exists twice in iTunes somehow???")
            logger.error("entry1")
            logger.error(str(itunes_playlists_map[playlist_name]))
            logger.error('entry2')
            logger.error(str(playlist))
            continue
        itunes_playlists_map[playlist_name] = playlist
        """
    playlist_names_sorted.sort()
    return itunes_playlists, playlist_names_sorted

def add_playlist_checklist_for_album(album, playlist, checklist):
    # if they have not created one yet, create one
    if not "playlist_checklists" in album:
        album["playlist_checklists"] = {}
    playlist_checklists = album["playlist_checklists"]
    playlist_checklists[playlist["name"]] = checklist

class AlbumChecklist(object):
    def __init__(self, album_name, album_artist, album_map, playlist):
        self.playlist = playlist
        self.album_name = album_name
        self.album_artist = album_artist
        self.album_key = make_album_key(self.album_name, self.album_artist)
        self.album = album_map[self.album_key]
        add_playlist_checklist_for_album(self.album, playlist, self)
        self.num_songs = len(self.album["songs"])
        self.songs_checked = 0
        self.checks = {}
        for song in self.album["songs"]:
            self.checks[song["location"]] = False
    def mark_song(self, song_location):
        assert song_location in self.checks
        assert self.checks[song_location] == False
        self.checks[song_location] = True
        self.songs_checked += 1

    def fully_covered(self):
        return self.songs_checked == self.num_songs

def get_album_checklist_for_playlist(playlist, album_name, album_artist, album_map):
    # if they have not created one yet, create one
    if not "album_checklists" in playlist:
        playlist["album_checklists"] = {}
    # now we are guarenteed to have our map to grab it
    album_checklists = playlist["album_checklists"]
    album_key = make_album_key(album_name, album_artist)
    if not album_key in album_checklists:
        album_checklists[album_key] = AlbumChecklist(album_name, album_artist, album_map, playlist)
    return album_checklists[album_key]


def match_playlist_to_albums(playlist, album_map):
    for track in playlist["tracks"]:
        album_name = track["album"]
        album_artist = get_itunes_album_artist(track)
        album_checklist = get_album_checklist_for_playlist(playlist, album_name, album_artist, album_map)
        album_checklist.mark_song(track["location"])

def match_playlists_to_albums(itunes_playlists, album_map):
    ignore_partial_albums_in_playlists = ignores_data.get("ignore_partial_albums_in_playlists",{})
    for playlist in itunes_playlists:
        playlist_name = playlist["name"]

        # check for empty playlists
        if not "tracks" in playlist or len(playlist["tracks"]) == 0:
            logger.info("Playlist '%s' contains NO tracks"%(playlist_name))
            continue

        playlist_album_ignore_list = ignore_partial_albums_in_playlists.get(playlist_name,[])
        match_playlist_to_albums(playlist, album_map)
        album_checklists = playlist["album_checklists"]
        for album_name, checkList in album_checklists.items():
            # if the album is in the ignore list, don't log about it
            if album_name in playlist_album_ignore_list:
                continue
            if not checkList.fully_covered():
                logger.info("Playlist '%s' is missing %s songs from album '%s'"%(playlist["name"],checkList.num_songs-checkList.songs_checked, album_name))
                for key in sorted(checkList.checks.keys()):
                    if not checkList.checks[key]:
                        logger.info("\t%s"%(key))


def find_albums_with_no_playlists(args, album_map):
    albums_not_needing_playlists = ignores_data.get("albums_not_needing_playlists",{})
    num_ignored = 0
    num_with_no_playlists = 0
    num_with_partial_playlists = 0
    num_with_multiple_playlists = 0
    num_with_complete_playlists = 0
    for album_key, album in album_map.items():
        if album_key in albums_not_needing_playlists:
            logger.info("Ignoring album '%s' which does not need a playlist"%(album_key))
            num_ignored += 1
            continue
        playlist_checklists = album.get("playlist_checklists", {})
        if len(playlist_checklists) == 0:
            logger.info("There are no playlists for Album '%s'"%(album_key))
            num_with_no_playlists += 1
            continue

        # peak and see if this album is covered or not
        if args.dont_show_fully_covered:
            is_fully_covered_by_any = False
            is_any_partial = False
            for playlist_name, checkList in playlist_checklists.items():
                if checkList.fully_covered():
                    is_fully_covered_by_any = True
                else:
                    is_any_partial = True
            # if this album is fully covered and we are not prinitng about it, update and move on
            if is_fully_covered_by_any:
                num_with_complete_playlists += 1
                if is_any_partial:
                    num_with_partial_playlists += 1
                if len(playlist_checklists) > 1:
                    num_with_multiple_playlists += 1
                continue

        if len(playlist_checklists) == 1:
            #loop to get the first and only element
            for playlist_name, checkList in playlist_checklists.items():
                pass
            if checkList.fully_covered():
                if not args.dont_show_fully_covered:
                    logger.info("Album '%s' is fully covered by playlist '%s'"%(album_key,playlist_name))
                num_with_complete_playlists += 1
            else:
                logger.info("Album '%s' is only partially covered by playlist '%s', missing songs are:"%(album_key,playlist_name))
                num_with_partial_playlists += 1
                for key in sorted(checkList.checks.keys()):
                    if not checkList.checks[key]:
                        logger.info("\t%s"%(key))
            continue
        logger.info("Album '%s' is reference by multiple playlists "%(album_key))
        num_with_multiple_playlists += 1
        got_complete_coverage = False
        got_partial_coverage = False
        for playlist_name, checkList in playlist_checklists.items():
            if checkList.fully_covered():
                logger.info("\tAlbum '%s' is fully covered by playlist '%s'"%(album_key,playlist_name))
                got_complete_coverage = True
            else:
                logger.info("\tAlbum '%s' is only partially covered by playlist '%s', included songs are:"%(album_key,playlist_name))
                got_partial_coverage = True
                for key in sorted(checkList.checks.keys()):
                    if checkList.checks[key]:
                        logger.info("\t\t%s"%(key))
        if got_complete_coverage:
            num_with_complete_playlists += 1
        if got_partial_coverage:
            num_with_partial_playlists += 1

    # print summary
    logger.info("Found %d albums with no playlists" %(num_with_no_playlists))
    logger.info("Found %d albums with partial playlists" %(num_with_partial_playlists))
    logger.info("Found %d albums with multiple playlists" %(num_with_multiple_playlists))
    logger.info("Found %d albums with complete playlists" %(num_with_complete_playlists))
    logger.info("Found %s albums which we are ignoring for playlists" %(num_ignored))




def make_output_file_path(output_dir, filename):
    if len(output_dir) > 0:
        output_path = os.path.join(output_dir, filename)
    else:
        output_path = filename
    return output_path

def Main():
    global logger, output_dir
    app_name = "DiffAlbumsAndPlaylists"

    try:
        good_args = []
        for arg in sys.argv[1:]:
            if (not arg.startswith('#')) and (not arg.startswith('--#')) and (not arg.startswith('-#')):
                good_args.append(arg)

        parser = argparse.ArgumentParser(description=app_name, fromfile_prefix_chars='@')
        parser.add_argument('--albums_file', default=None, help="iTunes albums", required=True)
        parser.add_argument('--playlists_file', default=None, help="iTunes playlists", required=True)
        parser.add_argument('--ignores_file', default=None, help="json file of ignore entries", required=False)
        parser.add_argument('--dont_show_fully_covered', default=False, action="store_true", help="when set, don't dump line on albums fully covered")
        parser.add_argument('--outputdir', help="directory where output files get written")
        parser.add_argument('--dump_album_keys', default=False, action="store_true", help="when set, dump keys to files")

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

        if args.ignores_file:
            load_ignores(args.ignores_file)

        itunes_albums, album_map, album_names_sorted = load_itunes_albums(args.albums_file)
        logger.info("Found %d albums in iTunes" %(len(album_names_sorted)))
        # dump the filenames  if requested
        if args.dump_album_keys:
            file_system_songs_sorted_keys = make_output_file_path(output_dir, "albums.txt")
            with open(file_system_songs_sorted_keys, "w", encoding='utf-8') as data_file:
                for fname in album_names_sorted:
                    data_file.write(fname+'\n')

        itunes_playlists, playlist_names_sorted = load_itunes_playlists(args.playlists_file)
        logger.info("Found %d playlists in itunes" %(len(itunes_playlists)))
        # dump the filenames  if requested
        if args.dump_album_keys:
            itunes_libary_songs_sorted_keys = make_output_file_path(output_dir, "playlists.txt")
            with open(itunes_libary_songs_sorted_keys, "w", encoding='utf-8') as data_file:
                for fname in playlist_names_sorted:
                    data_file.write(fname+'\n')

        match_playlists_to_albums(itunes_playlists, album_map)

        find_albums_with_no_playlists(args, album_map)




    except Exception as ex:
        log_func = logger.error if logger else print
        log_func('Got an exception in '+app_name)
        log_func(str(ex))
        log_func(traceback.format_exc())


if __name__ == '__main__':
    Main()