"""
    ratings-sync.py

    gmusic-ratings-sync: Sync your iTunes song ratings with Google Music
    ====================================================================

    Pretty much exactly what it sounds like:
    1.	Point it at your "iTunes Library.xml" file
    2.	Provide your Google Music credentials
    3.	...?
    4.	Profit!

    *NOTE*:
        This only syncs ratings from iTunes to Google Music and will overwrite
        any ratings you've set in Google Music. Also, it assumes you're using
        5-star ratings (because thumbs up/down is just not sufficient for rating music).

"""
__author__ = 'Derek Gould'

from gmusicapi.exceptions import CallFailure
from gmusicapi import Webclient
from bs4 import BeautifulSoup

# iTunes uses a 100 point scale
RATING_CONVERSION = 0.05

SONG_DICT = {
    'rating': 0,
    'name': '',
    'album': '',
    'albumArtist': '',
    'artist': '',
    'composer': '',
    'disc': 0,
    'genre': '',
    'playCount': 0,
    'totalDiscs': 0,
    'totalTracks': 0,
    'track': 0,
    'year': 0
}


class switch(object):
    value = None

    def __new__(cls, value):
        cls.value = value
        return True


def case(*args):
    return any((arg == switch.value for arg in args))


class RatingsSync(object):
    email = None
    password = None
    xml_file = None
    only_no_rating = False

    def __init__(self, email='', password='', xml_file='', only_no_rating=False):
        self.email = email
        self.password = password
        self.xml_file = xml_file
        self.only_no_rating = only_no_rating

    def start(self):
        """
        Start the sync
        """

        api = Webclient()

        try:
            api.login(self.email, self.password)
            xml_file = open(self.xml_file)

            print "Parsing songs from iTunes XML file..."
            itunes_song_list = self.__get_itunes_song_list(xml_file)
            print "iTunes XML file parsing complete"

            print "Retrieving songs from Google Music..."
            gmusic_song_list = self.__get_gmusic_song_list(api)
            print "Google Music song retrieval complete"

            print "Computing the intersection of the song lists..."
            song_list = self.__get_intersection(gmusic_songs=gmusic_song_list, itunes_songs=itunes_song_list,
                                                only_no_rating=self.only_no_rating)
            print "Song list intersection computed"

            print "Syncing song ratings..."
            self.__sync_song_ratings(api, song_list)
            print "Song ratings sync complete!"

        except CallFailure:
            print "Error: Couldn't log in to Google Music!"
        except IOError:
            print "Error: iTunes XML file not found"

    def __get_gmusic_song_list(self, api):
        """
        Download the user's Google Music song list
        """

        tracks = []

        for songs in api.get_all_songs(True):
            tracks += songs
            print "\t", len(tracks), " songs retrieved..."

        tracks = [song for song in tracks]

        return sorted(tracks, key=lambda t: t['name'])

    def __get_itunes_song_list(self, xml_file):
        """
        Extract the song list from the given iTunes XML file
        """

        print "\tLoading XML file... (this may take a minute or two)"
        xml = BeautifulSoup(xml_file)
        print "\tXML file loaded"

        print "\tExtracting songs..."
        tracks = xml.select("dict > dict > dict")
        print "\tSongs extracted"

        parsed = []

        print "\tParsing songs..."
        for songs in self.__parse_itunes_songs(tracks):
            parsed += songs
            print "\t\t", len(parsed), " songs parsed..."

        print "\tSongs parsed"

        return sorted(parsed, key=lambda t: t['name'])

    def __parse_itunes_songs(self, it_songs):
        """
        Parse an iTunes XML song dictionary into a gmusicapi song dictionary
        """
        get_next_chunk = True
        start = 0
        num_songs = len(it_songs)

        while get_next_chunk:

            songs = []
            end = start + 1000
            if end > num_songs:
                end = num_songs

            for i in range(start, end):

                song = SONG_DICT.copy()

                for key in it_songs[i]('key'):

                    value = key.next_sibling

                    while switch(key.string):
                        if case('Album'):
                            song['album'] = value.string
                            break
                        if case('Artist'):
                            song['artist'] = value.string
                            break
                        if case('Album Artist'):
                            song['albumArtist'] = value.string
                            break
                        if case('Name'):
                            song['name'] = value.string
                            break
                        if case('Composer'):
                            song['composer'] = value.string
                            break
                        if case('Genre'):
                            song['genre'] = value.string
                            break
                        if case('Track'):
                            song['track'] = int(value.string)
                            break
                        if case('Track Count'):
                            song['totalTracks'] = int(value.string)
                            break
                        if case('Year'):
                            song['year'] = int(value.string)
                            break
                        if case('Disc Number'):
                            song['disc'] = int(value.string)
                            break
                        if case('Disc Count'):
                            song['totalDiscs'] = int(value.string)
                            break
                        if case('Play Count'):
                            song['playCount'] = int(value.string)
                            break
                        if case('Rating'):
                            song['rating'] = int(int(value.string) * RATING_CONVERSION)
                            break
                        break

                songs.append(song)

            yield songs

            start = end
            get_next_chunk = start < num_songs - 1

    def __get_intersection(self, gmusic_songs=[], itunes_songs=[], only_no_rating=False):
        """
        Gets the intersection of the two lists with differing ratings
        Returns the intersection as a list of dictionaries containing the matched song dictionaries with different
        ratings
        """

        remaining_songs = itunes_songs
        matched_songs = []
        gm_unmatched_songs = []

        print "\tTotal Google Music songs: ", len(gmusic_songs)
        print "\tTotal iTunes songs: ", len(itunes_songs)
        if only_no_rating:
            print "\tGetting songs with no rating in Google Music..."
            gmusic_songs = [song for song in gmusic_songs if song['rating'] == 0]
            print "\tGoogle Music songs with no rating: ", len(gmusic_songs)

        print "\tIntersecting..."
        for gm_song in gmusic_songs:

            matches = [it_song for it_song in remaining_songs if it_song['name'] == gm_song['name']]

            if len(matches) > 1:
                matches = [it_song for it_song in matches if it_song['album'] == gm_song['album']]

            if len(matches) > 1:
                matches = [it_song for it_song in matches
                           if it_song['artist'] == gm_song['artist'] or
                              it_song['albumArtist'] == gm_song['albumArtist'] or
                              it_song['artist'] == gm_song['albumArtist'] or
                              it_song['albumArtist'] == gm_song['artist']
                ]

            if len(matches) > 1:
                matches = [it_song for it_song in matches if it_song['year'] == gm_song['year']]

            if len(matches) > 1:
                matches = [it_song for it_song in matches if it_song['genre'] == gm_song['genre']]

            if len(matches) > 0:
                remaining_songs.remove(matches[0])
                if matches[0]['rating'] < 0 or matches[0]['rating'] > 5:
                    print matches[0]['rating']
                if gm_song['rating'] != matches[0]['rating']:
                    gm_song['rating'] = matches[0]['rating']
                    matched_songs.append(gm_song)
            else:
                gm_unmatched_songs.append(gm_song)

        print "\tSongs ready for ratings sync: ", len(matched_songs)

        return matched_songs

    def __sync_song_ratings(self, api, songs):
        """
        Sync ratings to Google Music
        """

        api.change_song_metadata(songs)
