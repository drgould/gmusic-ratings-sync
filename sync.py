__author__ = 'Derek Gould'

import getpass
import readline
from tabcomplete import Completer
from ratingssync import RatingsSync

comp = Completer()
# we want to treat '/' as part of a word, so override the delimiters
readline.set_completer_delims(' \t\n;')
readline.parse_and_bind("tab: complete")
readline.set_completer(comp.complete)

email = raw_input("Google Music Email: ")
password = getpass.getpass()
filename = raw_input("iTunes library XML file: ")
only_no_rating = raw_input("Only sync ratings for songs that are unrated in Google Music (y/n)? ")
only_no_rating = (only_no_rating == 'y' or only_no_rating == 'Y' or only_no_rating == 'yes')
sync = RatingsSync(email=email, password=password, xml_file=filename, only_no_rating=only_no_rating)
sync.start()