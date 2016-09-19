#! /usr/bin/env python

import csv
from dateutil import parser
import os
import json
import sys

missing = "https://twitter.com/bismark/status/158019945467363328/"

already_imported = [
        "748507006424608768",
        "748860394593087488",
        "748902429408669696",
        "749358871467200512"]

ignored_tweets = [
#bad subjects
884488812,945357081,947106190,948488225,875813956,

        # canabalt
5612051264, 5625668106, 5630484315,
5746516180, 5746605787, 5925123345,
6010610128, 6657874560, 6671630602,

        #astronut
7609424533262336, 8322997374951424, 8412894668529664,

        #spam
46768330832482304, 3679859817, 836941173, 16175650677, 19323197202,
21420025674, 27797889912668160, 48497203475517440, 1422449868, 8928371411,
260402661512335360,260810301421789185,99500936753459200,94948699083522048,
94948755169742848,94948908756779008,94948962322219009,94949211082194944,
85429550909112320,27798382642728960,27797599234826240,27748898600652800,
19485913092464640,14336428867592193,8075048059,7528128879,6803631175,6577606962,
5926901347,5903361802,5685902321,5499158798,5097089053,4918593287,4735594891,
4373520535,4085351565,3914882105,3766093008,3459226925,
3314108569,3184560709,2825909685,2692920409,2574523768,2134325416,2240904800,2345861038,
553993509913370625,191750056993505280,694634814897537024,235015483655593986,
119129511173435392,
        # dead link
1063025960, 3819482765, 9569677873258496, 57904553420525568,
175029994152660992,1581273713,

        #tech support replies
749916908762398720,232940205831753729,551918602379485185,523158065818771456,
717716082367315969,717702067305979905,711684316632317952,711662702616137728,
694130689852203008,665165130955669504,637211001004421120,611529362572214272,
523202773467152384,523202378799919105,523158263030755329,508875324092727297,
473939958319697920,463333803763970048,460726728487231488,460726070497796096,
454318792295079936,425328376484597760,425322493297954816,420326167753654272,
399331039396388864,393023813241171968,392775657073037312,392775499094560768,
347774862363865088,193135436078661632,193113148985843712,463679950504361984,

# junk replies / bad identity
608531582954164224,482191029106651136,444833286419120128,
419981732176482304,449221431495495680,470131579235602432,
642334144668766208, 677649242,

#missing replies
535195556998832129,480302886073954304,454313815782727680,
13931950699,

# cutlerite
1109804241,1086286128,770529310,2799417761,877863613,
1884850751,6054812187,1150526260,1038450977,767717290,
1008919769,778860798,788002200,1081204070,771599410,
885757866,

# deleted dupes
255318672,767400917,127972562847285249,911895607,903554606, 800658423
        ]

counts = {'basic': 0, 'old_rt': 0, 'media': 0, 'reply': 0, 'mention': 0}

def get_ts():
    timestamps = {}
    with open("/Users/ryan/Downloads/8611982_0cd37e856cbbeb3423dd06024ee6cd57b8ebf806/updated_tweets.csv", 'rb') as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            timestamps[row['tweet_id']] = parser.parse(row['timestamp'])
    return timestamps

timestamps = get_ts()

tweets = {
        "regular_tweets": {},
        "media_tweets": {},
        "mention_tweets": {},
        "url_tweets": {},
        "hashtag_tweets": {},
        "old_rt_tweets": {},
        "old_reply_tweets": {},
        "retweeted_tweets": {},
        "bad_reply_tweets": {},
}

for root, dirs, files in os.walk("/Users/ryan/Downloads/8611982_0cd37e856cbbeb3423dd06024ee6cd57b8ebf806/data/js/tweets"):
    for filename in files:
        if not filename.endswith(".js"):
            continue
        path = os.path.join(root, filename)
        with open(path, 'r') as f:
            f.readline()
            data = json.load(f)

            for tweet in data:
                tweet_id = tweet['id']
                del tweet['id']
                del tweet['id_str']
                del tweet['user']
                del tweet['source']

                if len(tweet['geo']) == 0:
                    del tweet['geo']

                del tweet['created_at']
                tweet['timestamp'] = timestamps[str(tweet_id)].isoformat()

                #if  and not 'in_reply_to_user_id' in tweet:
                if 'in_reply_to_status_id' in tweet and len(tweet['entities'][u'user_mentions']) == 0:
                    print tweet_id, tweet['text']
                continue


                if 'retweeted_status' in tweet:
                    tweets['retweeted_tweets'][tweet_id] = tweet
                    continue
                if tweet['text'].startswith("RT"):
                    tweets['old_rt_tweets'][tweet_id] = tweet
                    continue
                if len(tweet['entities'][u'media']) > 0:
                    tweets['media_tweets'][tweet_id] = tweet
                    continue
                if len(tweet['entities'][u'user_mentions']) > 0:
                    tweets['mention_tweets'][tweet_id] = tweet
                    continue
                if len(tweet['entities'][u'urls']) > 0:
                    tweets['url_tweets'][tweet_id] = tweet
                    continue
                if 'in_reply_to_user_id' in tweet:
                    tweets['old_reply_tweets'][tweet_id] = tweet
                    continue
                if tweet['text'].startswith("@"):
                    tweets['bad_reply_tweets'][tweet_id] = tweet
                    continue
                if len(tweet['entities'][u'hashtags']) > 0:
                    tweets['hashtag_tweets'][tweet_id] = tweet
                    continue

                del tweet['entities']

                if len(tweet) > 2:
                    print tweet_id, tweet
                    sys.exit(1)


                tweets['regular_tweets'][tweet_id] = tweet

#print counts
#for key in tweets.keys():
#    with open('{}.json'.format(key), 'w') as of:
#        json.dump(tweets[key], of, sort_keys=True, indent=4, separators=(',', ': '))
#
