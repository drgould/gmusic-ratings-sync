gmusic-ratings-sync: Sync your iTunes song ratings to Google Music
==================================================================

Syncs your song ratings from iTunes to Google Music...Duh!

***NOTE***: This only syncs ratings from iTunes to Google Music and will overwrite any ratings you've set in Google Music. Also, it assumes you're using 5-star ratings (because thumbs up/down is just not sufficient for rating music).

Usage
-----
From the command line:

	python sync.py

Follow the prompts:

	Google Music Email:
    Password:
    iTunes library XML file:
    Only sync ratings for songs that are unrated in Google Music (y/n)?

Then let it do its thing.
That's it!


Requirements
------------
-	[The Unofficial Google Music API](http://github.com/simon-weber/Unofficial-Google-Music-API) (pip install gmusicapi)
-	[BeautifulSoup 4](http://www.crummy.com/software/BeautifulSoup/) (pip install BeautifulSoup4)
