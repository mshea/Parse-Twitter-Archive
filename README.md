# Parse Tweet Archive Python Script

Michael E. Shea, 3 May 2013

## A Multi-Format Archive of All Your Tweets

Twitter's new [archive feature](http://blog.twitter.com/2012/12/your-twitter-archive.html) lets us download all of our tweets into a single archive we can store wherever we want. We finally have control over the content we've fed into this online service.

The archive itself, however, doesn't give us a lot of ways to process or use our tweets.

This script parses through the [JSON](http://en.wikipedia.org/wiki/JSON) records contained within the archive and outputs our tweets into a bunch of different formats including:

* A single HTML5 page.
* A single big text file.
* A single big JSON file with all the elements included.
* A SQLite3 database.
* Other fun files like a geo-coord csv file and a list of your most mentioned Twitter users (BFFs).

## Running This Script

When running this program, it will help you considerably if you have experience running Python programs at the command line. This script requires no external Python modules outside of the core modules included in Python 2.7.

This script is intended to be run at the command line at the same parent directory as the tweet archive.

You can modify the parameters to suit your own file locations and, if you want, your own output HTML headers. You can also filter tweets by seeking a single keyword. In order for tweet links to work properly, you'll want to enter your own Twitter screen name.

This file can also run as a module for use in other programs.

## Licensed Under Creative Commons Attribution Non-Commercial Share Alike 3.0

This program is licensed under the [Creative Commons Attribution-NonCommercial-ShareAlike 3.0 License](http://creativecommons.org/licenses/by-nc-sa/3.0/). You are free to share, copy, distribute, transmit, remix, and adapt it as long as you attribute it to Michael E. Shea at [http://mikeshea.net/](http://mikeshea.net/), share the work under the same license, and do so for non-commercial purposes. If you have a commercial idea, a note to mike@mikeshea.net to discuss it. To view a copy of this license, visit [http://creativecommons.org/licenses/by-nc-sa/3.0/](http://creativecommons.org/licenses/by-nc-sa/3.0/).