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

## Last updated 2 February 2013

import json
import os
import datetime
import re
import sqlite3
from datetime import datetime
from datetime import timedelta

params = {
    'data_folder': './mshea_tweets/data/js/tweets/',
    'output_folder': './',
    'output_file_name': 'tweets',
    'twitter_user_id': 'mshea',
    'html_header': '<!DOCTYPE html><meta charset="UTF-8">'
                   '<title>mshea Tweets</title><h1>mshea Tweets</h1><ul>',
    'html_footer': '\n</ul>'}


def load_json_data_from_files(data_folder):
    json_output = []
    filenames = os.listdir(data_folder)
    for file in filenames:
        if '.js' in file:
            d = open(data_folder + file).readlines()
            d[0] = ''  # Twitter's JSON requires we remove the first line
            json_data = json.loads(''.join(d))
            for entry in json_data:
                json_output.append(entry)
    return json_output


def output_json(json_data):
    fpath = params['output_folder']+params['output_file_name']+'.js'
    with open(fpath, 'w') as f:
        f.write(json.dumps(json_data, indent=4))


def output_sqlite(json_input):
    dbpath = params['output_folder']+params['output_file_name']+'.sqlite3'
    conn = sqlite3.connect(dbpath)
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
    return True


def output_html(tweets):
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
                       '<time datetime="%s">%s</time></a></li>\n\n' \
                        % (item['id'],
                           text,
                           tweet_link,
                           time_element,
                           day_string)
    fpath = params['output_folder']+params['output_file_name']+'.html'
    with open(fpath, "w") as f:
        f.write(params['html_header'])
        f.write(html_output.encode('utf-8'))
        f.write(params['html_footer'])


def output_text(tweets):
    text_output = ''
    for item in tweets:
        text_output += '%s\n%s\n%s\n\n' % (item['id'],
                                           item['created_at'],
                                           item['text'])
    fpath = params['output_folder']+params['output_file_name']+'.txt'
    with open(fpath, "w") as f:
        f.write(text_output.encode('utf-8'))


def load_tweets_from_db(db_file):
    tweets = []
    conn = sqlite3.connect(db_file)
    conn.row_factory = sqlite3.Row
    c = conn.cursor()
    db_object = c.execute('select id, created_at, text from tweets '
                          'order by id desc;')
    for row in db_object:
        tweets.append(dict(zip(row.keys(), row)))
    return tweets


def link_https_in_text(text):
    parsed_text = re.sub('http://[^ ,]*', lambda t: "<a href='%s'>%s</a>" %
        (t.group(0), t.group(0)), text)  # Find links and hyperlink them
    return parsed_text


def main():
    output = load_json_data_from_files(params['data_folder'])
    output_json(output)
    output_sqlite(output)
    db_path = params['output_folder']+params['output_file_name']+'.sqlite3'
    db_input = load_tweets_from_db(db_path)
    output_html(db_input)
    output_text(db_input)

main()
