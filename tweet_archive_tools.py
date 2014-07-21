## Last updated 8 Dec 2013
##
## This program takes data from a locally downloaded Twitter archive
## and outputs HTML, Text, JSON, geo-coords in CSV, and best friends in csv.
## See http://blog.twitter.com/2012/12/your-twitter-archive.html
##
## It can run either as a dedicated program or as a module.
##
## Please visit https://github.com/mshea/Parse-Twitter-Archive
## for more information.
##
## This work is licensed under the Creative Commons Attribution
## NonCommercial-ShareAlike 3.0 License. You are free to share, copy,
## distribute, transmit, remix, and adapt the work as long as you attribute
## it to Michael E. Shea at http://mikeshea.net/, share the work under
## the same license, and do so for non-commercial purposes. To view a copy
## of this license, visit http://creativecommons.org/licenses/by-nc-sa/3.0/.
##

import glob
import json
import csv
import datetime
import collections
import re
import sqlite3
from datetime import datetime
from datetime import timedelta
from itertools import islice, izip
from collections import Counter

params = {
    'data_files': './data/js/tweets/*.js',
    'geo_output': 'dnd_tip_tweets_geo.csv',
    'text_output': 'dnd_tip_tweets.txt',
    'json_output': 'dnd_tip_tweets.json',
    'bff_output': 'dnd_tip_bffs.csv',
    'csv_output': 'dnd_tip_tweets.csv',
    'sqlite3_output': 'dnd_tip_tweets.sqlite3',
    'html_output': 'dnd_tip_tweets.html',
    'twitter_user_id': 'slyflourish',
}


def load_data(files):
    items = []
    files = glob.glob(files)
    for file in files:
        with open(file) as f:
            d = f.readlines()[1:]  # Twitter's JSON first line is bogus
            d = "".join(d)
            j = json.loads(d)
            for tweet in j:
                r = 1
                # Comment out above and uncomment below to filter tweets by an re match.
                # r = re.compile("^#dnd tip:").match(tweet['text'])
                if r:
                    items.append(tweet)
    return sorted(items, key=lambda k: k['id'])


def get_bffs(d):
    words = []
    for item in d:
        item_words = item['text'].split()
        for word in item_words:
            if '@' in word:
                words.append(word.replace(':', '').lower().encode('utf-8'))
    return collections.Counter(words).most_common(50)


def get_bigrams(d):
    words = []
    for item in d:
        item_words = re.findall('\w+', item['text'])
        words += item_words
    output = (Counter(zip(words, words[1:])).most_common(100))
    for item in output:
        print item

def get_csv_output(d):
    output = [('id', 'date', 'tweet')]
    for item in d:
        output.append((
                item['id_str'],
                item['created_at'],
                item['text'].encode('utf-8')
                ))
    return output
        

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
                              '%Y-%m-%d %H:%M:%S +0000')
        - timedelta(hours=5)
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
                '<style>'
                'body {'
                'max-width:40em; '
                'margin:auto; '
                'line-height: 1.5em; '
                'font-family: Georgia, serif; '
                'font-size:1.2em;} '
                'ul {list-style-type: none} '
                'li {padding:.5em;}'
                '</style>'
                '<title>Twitter Archive Output</title>\n'
                '<ul>\n')
        f.write(html_output.encode('utf-8'))
        f.write('</ul>')


def write_sqlite3(json_input, output_file):
    conn = sqlite3.connect(output_file)
    c = conn.cursor()
    try:
        c.execute('select count(*) from tweets')
    except:
        c.execute('CREATE TABLE tweets'
                  '(id int not null primary key, '
                  'created_at text, text text)')
    conn.commit()
    data_to_write = []
    for item in json_input:
        data_to_write.append((int(item['id_str']),
                              item['created_at'],
                              item['text']))
    c.executemany('INSERT OR REPLACE '
                  'INTO tweets VALUES (?,?,?);',
                  data_to_write)
    conn.commit()


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
    write_csv(get_bffs(d), params['bff_output'])
    write_csv(get_geo(d), params['geo_output'])
    write_csv(get_csv_output(d), params['csv_output'])
    write_html(d, params['html_output'])
    write_text(d, params['text_output'])
    write_json(d, params['json_output'])
    write_sqlite3(d, params['sqlite3_output'])


if __name__ == "__main__":
    main()