## This set of tools parses data from a downloaded Twitter archive
## and outputs various files including JSON, HTML, and Text dumps
## as well as some other fun stuff like best friends (bffs) and geo-coords
##
## It can run either as a dedicated program or as a module
##
## Last updated 3 May 2013

import glob
import json
import csv
import datetime
import collections
import re
from datetime import datetime
from datetime import timedelta
from itertools import islice, izip
from collections import Counter

params = {
	'data_files': './mshea_tweets/data/js/tweets/*.js',
	'geo_output': 'mshea_geo.csv',
	'text_output': 'mshea_tweets.txt',
	'json_output': 'mshea_tweets.json',
	'bff_output': 'mshea_bffs.csv',
	'csv_output': 'mshea_tweets.csv',
	'html_output': 'mshea_tweets.html',
	'text_output': 'mshea_tweets.txt',
	'twitter_user_id': 'mshea',
	}

def load_data(files):
	items = []
	files = glob.glob(files)
	for file in files:
		with open(file) as f:
			d = f.readlines()[1:] # get rid of first line
			d = "".join(d) # turn it into a string
			j = json.loads(d) # Parse the JSON
			for tweet in j:
				items.append(tweet)
	return items

def get_bffs(d):
	words = []
	for item in d:
		item_words = item['text'].split()
		for word in item_words:
			if '@' in word:
				words.append(word.replace(':', '').lower())
	return collections.Counter(words).most_common(50)

def get_bigrams(d):
	words = []
	for item in d:
		item_words = re.findall('\w+', item['text'])
		words += item_words
	output = (Counter(zip(words,words[1:])).most_common(100))
	for item in output:
		print item

def get_geo(d):
	output = [('date', 'tweet', 'lat', 'long')]
	for item in d:
		try:
			lat = item['geo']['coordinates'][0]
			long = item['geo']['coordinates'][1]
			date = item['created_at']
			text = item['text'].encode('utf-8')
			output.append((date, text, lat, long))
		except:
			error = "no coordinates"
	return output

def link_https_in_text(text):
    parsed_text = re.sub('http://[^ ,]*',
    		lambda t: "<a href='%s'>%s</a>" %
			(t.group(0), t.group(0)), text)
    return parsed_text

def write_html(tweets, output_file):
    html_output = ""
    for item in tweets:
        d = datetime.strptime(item['created_at'],
            '%a %b %d %H:%M:%S +0000 %Y') - timedelta(hours=5)
        day_string = d.strftime('%d %b %Y %I:%M %p')
        true_time_object = d + timedelta(hours=5)
        time_element = true_time_object.isoformat("T")
        text = link_https_in_text(item['text'])
        tweet_link = 'http://twitter.com/%s/status/%s'\
                     % (params['twitter_user_id'], item['id'])
        html_output += '<li id=%s>%s - <a href="%s">'\
                       '<time datetime="%s">%s</time></a></li>\n' \
                        % (item['id'],
                           text,
                           tweet_link,
                           time_element,
                           day_string)
    with open(output_file, "w") as f:
        f.write('<!DOCTYPE html>\n'
        		'<title>Twitter Archive Output</title>\n'
        		'<ul>\n')
        f.write(html_output.encode('utf-8'))
        f.write('</ul>')


def write_text(tweets, output_file):
    text_output = ''
    for item in tweets:
        text_output += '%s\n%s\n%s\n\n' % (item['id'],
                                           item['created_at'],
                                           item['text'])
    with open(output_file, "w") as f:
        f.write(text_output.encode('utf-8'))

def write_csv(d, csv_file):
	with open(csv_file, 'w') as f:
		writer = csv.writer(f)
		writer.writerows(d)

def write_json(json_data, output_file):
    with open(output_file, 'w') as f:
        f.write(json.dumps(json_data, indent=4))


def main():
	d = load_data(params['data_files'])
	#get_bigrams(d)
	write_csv(get_bffs(d), params['bff_output'], )
	write_csv(get_geo(d), params['geo_output'])
	write_html(d, params['html_output'])
	write_text(d, params['text_output'])
	write_json(d, params['json_output'])

if __name__=="__main__":
	main()