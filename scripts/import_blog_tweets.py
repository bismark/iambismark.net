#! /usr/bin/env python

import codecs
import json
from dateutil import parser
from hugo_helper import utils
import calendar

import os
import sys
import yaml

output_dir = os.path.join(os.getcwd(), "iambismark.net", "content", "post")

with open('blog_tweets.json', 'r') as f:
    tweets = json.load(f)
    for tweet_id, tweet in tweets.iteritems():
        if 'text' in tweet:
            text = tweet['text']

            metadata = {}
            ts = parser.parse(tweet['timestamp'])
            metadata['date'] = ts.isoformat()
            metadata['slug'] = str(calendar.timegm(ts.timetuple()))
            metadata['archive'] = [ts.strftime("%Y-%m")]
            metadata['alturls'] = ["https://twitter.com/bismark/status/{}".format(tweet_id)]

            if 'slug' in tweet:
                metadata['type'] = 'link'
                if 'title' in tweet:
                    metadata['title'] = tweet['title']
                else:
                    post_metadata = utils.slug_to_metadata(tweet['slug'])
                    metadata['title'] = post_metadata['title']
                    metadata['rellink'] = tweet['slug']
                text += "\n"
            else:
                new_text = ""
                for idx, slug in enumerate(tweet['slugs']):
                    post_metadata = utils.slug_to_metadata(slug)
                    new_text += "[{}][{}]\n\n".format(post_metadata['title'], idx)
                new_text += text + "\n\n"
                for idx, slug in enumerate(tweet['slugs']):
                    new_text += "[{}]: {{{{< relref \"{}.md\" >}}}}\n".format(idx, slug)
                new_text += "\n"
                text = new_text

            year = ts.strftime("%Y")
            month = ts.strftime("%m")

            output_path = os.path.join(output_dir, year, month)
            if not os.path.isdir(output_path):
                os.makedirs(output_path)

            output_filename = os.path.join(output_path, metadata['slug']+".md")
            if os.path.isfile(output_filename):
                print "filename conflict", output_filename
                sys.exit(1)


            with codecs.open(output_filename, 'w', encoding='utf-8') as output_file:
                output_file.write("---\n")
                yaml.safe_dump(metadata, output_file, encoding='utf-8', default_flow_style=False, indent=4)
                output_file.write("---\n\n")

                output_file.write(text)
                output_file.write("\n")
        else:
            metadata = utils.slug_to_metadata(tweet['slug'])
            if 'alturls' in metadata:
                metadata['alturls'].append("https://twitter.com/bismark/status/{}".format(tweet_id))
            else:
                metadata['alturls'] = ["https://twitter.com/bismark/status/{}".format(tweet_id)]

            if 'flickr_url' in tweet:
                metadata['alturls'].append(tweet['flickr_url'])

            utils.update_metadata(tweet['slug'], metadata)



        #os.rename(media_file, os.path.join(processed_dir, tweet['filename']))

