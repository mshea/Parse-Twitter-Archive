## This program takes data from a locally downloaded Twitter archive
## See http://blog.twitter.com/2012/12/your-twitter-archive.html
## It filters on a particular key word if desired and outputs
## HTML, CSV, Text, JSON, and SQLite3 files containing all of the
## tweets contained in the archive that included the keyword.
##
## Please visit https://github.com/mshea/Parse-Twitter-Archive
## for more information.
##
## This work is licensed under the Creative Commons Attribution
## NonCommercial-ShareAlike 3.0 License. You are free to share, copy, 
## distribute, transmit, remix, and adapt the work as long as you attribute 
## it to Michael E. Shea at http://slyflourish.com/, share the work under 
## the same license, and do so for non-commercial purposes. To view a copy 
## of this license, visit http://creativecommons.org/licenses/by-nc-sa/3.0/.

## If you want to give back, please take a look at the Lazy Dungeon Master,
## Sly Flourish's Dungeon Master Tips and Running Epic Tier D&D Games.

## Last updated 2 February 2013

import json
import os
import datetime
import re
import sqlite3
from datetime import datetime
from datetime import timedelta

params = {
	# Where the downloaded Twitter archive lives
	'data_folder': './tweets/data/js/tweets/', 
	# Where you want to send the archive files
	'output_folder': './',
	# The name of the files you want without an extension.
	'output_file_name': 'tweets', 
	# Filter out tweets with this such:
	#'filter_text': '#dnd tip:', 
	'filter_text': False, 
	# The ID of your Twitter account, used to generate tweet links.
	'twitter_user_id': 'SlyFlourish', 
	'html_header': '''
<!DOCTYPE html>
<meta name="viewport" content="user-scalable=yes, width=device-width">
<style>
body { font-family: Verdana, Geneva, sans-serif; 
color:#333; max-width:35em; margin:auto; }
time { font-size: .6em; }
ul { list-style:none; }
p.license { text-align: center; }
ul, h1, .updated { margin:0; padding:0; }
li, p {line-height: 1.6em; }
li { padding-left: 1.3em; padding-bottom: 1em; text-indent: -1em; }
h1 { font-weight: normal; font-size: 1.4em; 
padding-top: 1em; padding-bottom: 1em;}
</style>
<title>Sly Flourish #dnd Tips</title>
<h1>Sly Flourish #dnd Tips</h1>
<ul>
''',
	'html_footer': '\n</ul>'
	}

def load_json_data_from_files(data_folder):
	json_output = []
	filenames = os.listdir(data_folder)
	for file in filenames:
		if '.js' in file:
			f = open(data_folder + file)
			d = f.readlines()
			d[0] = '' # Twitter's JSON requires we remove the first line
			json_data = json.loads(''.join(d))
			for entry in json_data:
				try:
					if params['filter_text'] in entry['text']:
						json_output.append(entry)
				except:
					json_output.append(entry)
	return json_output
	
def output_json(json_data):
	f = open(params['output_folder']+params['output_file_name']+'.js','w')
	f.write(json.dumps(json_data, indent=4))
	f.close()
	return True

def output_sqlite(json_input):
	conn = sqlite3.connect(params['output_folder']
			+params['output_file_name']+'.sqlite3')
	c = conn.cursor()
	try:
		c.execute('select count(*) from tweets')
	except:
		c.execute('''CREATE TABLE tweets 
				(id int not null primary key, 
				created_at text, text text)''')
	conn.commit()
	data_to_write = []
	for item in json_input:
		data_to_write.append((int(item['id_str']), 
				item['created_at'], item['text']))
	c.executemany('''INSERT OR REPLACE 
					INTO tweets VALUES (?,?,?);'''
					, data_to_write)
	conn.commit()
	return True

def output_html(tweets):
	html_output = ""
	for item in tweets:
		id, created_at, text = item
		d = datetime.strptime(created_at, 
				'%a %b %d %H:%M:%S +0000 %Y') - timedelta(hours=5)
		day_string = d.strftime('%d %b %Y %I:%M %p')
		true_time_object = d + timedelta(hours=5)
		time_element = true_time_object.isoformat("T")
		html_output += "<li id="+str(id)+">"+link_https_in_text(text)+\
				"<a href=\"https://twitter.com/SlyFlourish/status/"+str(id)+\
				"\"><time datetime=\"" + time_element + "\">"+day_string+\
				"</time></a></li>\n\n"
	f = open(params['output_folder']+params['output_file_name']+'.html', "w")
	f.write(params['html_header'])
	f.write(html_output.encode('utf-8'))
	f.write(params['html_footer'])
	f.close()
	return True

def output_csv(tweets):
	csv_output = ''
	for item in tweets:
		id, created_at, text = item
		text = text.replace('"','""')
		csv_output += '\"'+str(id)+'\",\"'+created_at+'\",\"'+text+'\"\n'
	f = open(params['output_folder']+params['output_file_name']+'.csv', "w")
	f.write(csv_output.encode('utf-8'))
	f.close()

def output_text(tweets):
	text_output = ''
	for item in tweets:
		id, created_at, text = item
		text_output += str(id)+'\n'+created_at+'\n'+text+'\n\n'
	f = open(params['output_folder']+params['output_file_name']+'.txt', "w")
	f.write(text_output.encode('utf-8'))
	f.close()

def load_tweets_from_db(db_file):
	tweets = []
	conn = sqlite3.connect(db_file)
	c = conn.cursor()
	db_object = c.execute('''select id, created_at, text from tweets 
			order by id desc;''')
	for item in db_object:
		tweets.append(item)
	return tweets
	
def link_https_in_text(text):
	parsed_text = re.sub('http://[^ ,]*', lambda t: "<a href='%s'>%s</a>" % 
			(t.group(0), t.group(0)), text) # Find links and hyperlink them
	return parsed_text

def main():
	output = load_json_data_from_files(params['data_folder'])
	output_json(output)
	output_sqlite(output)

	# We load data from the database so we can correctly order it.
	db_input = load_tweets_from_db(
			params['output_folder']+params['output_file_name']+'.sqlite3'
			)
	output_html(db_input)
	output_csv(db_input)
	output_text(db_input)
	
main()