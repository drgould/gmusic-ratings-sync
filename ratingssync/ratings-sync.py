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

from gmusicapi import Webclient

# iTunes uses a 100 point scale
RATING_CONVERSION = 0.20

class RatingsSync(object):

	def __init__(self, email=None, password=None, filename=None):

		self.gmusic.api = Webclient()

		if not email:
			email = raw_input("Email: ")
		if not password:
			password = getpass()
		if not filename:
			filename = raw_input("iTunes library XML file:")

		self.gmusic.songs = self.get_gmusic_song_list(email,password)
		print "song count: " % len(self.gmusic.songs)


	def get_gmusic_song_list(self, email, password):
		"""Downloads the user's Google Music song list"""

		if self.gmusic.api.login(email,password):
			return self.gmusic.api.get_all_songs();

		return False