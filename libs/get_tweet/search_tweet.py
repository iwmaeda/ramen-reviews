import datetime
import json
import time
from urllib import parse

import pandas as pd
from requests_oauthlib import OAuth1Session


class TweetSearcher(object):
    def __init__(self, consumer_key=None, consumer_secret=None, access_token=None, access_token_secret=None):
        self.consumer_key = consumer_key
        self.consumer_secret = consumer_secret
        self.access_token = access_token
        self.access_token_secret = access_token_secret
        self.session = OAuth1Session(self.consumer_key, self.consumer_secret,
                                     self.access_token, self.access_token_secret)

    def search_with_query(self, search_query, gets=None, max_ite=100,
                          exclude_reply=False, exclude_retweet=False):
        '''
        Search tweets which meets search query
        :param search_query: 
        :param gets: Data acquired in addition to text(str or list of str, default=['text'])
        :param max_ite: 
        :return: 
        '''
        if gets is None:
            gets = []
        elif isinstance(gets, str):
            gets = [gets]
        elif not isinstance(gets, list):
            raise ValueError('gets must be str or list of str')

        url = 'https://api.twitter.com/1.1/search/tweets.json'
        params = {'q': parse.quote(search_query),
                  'count': 100}

        df_tweets = pd.DataFrame(columns=gets + ['text'])

        for ite in range(max_ite):
            # Request
            res = self.session.get(url, params=params)
            time_res_acquired = datetime.datetime.now()

            # Confirm response
            if res.status_code == 200:
                # Get tweets
                tweets = json.loads(res.text)['statuses']
                # Break if there is no tweet which meets the searching condition
                if len(tweets) == 0:
                    print('There is no matching tweet')
                    self._check_remaining_api(res, time_res_acquired)
                    break
                else:
                    print('Iteration: %s/%s' % (ite + 1, max_ite))
                    for tweet in tweets:
                        # Exclude reply or retweet
                        if self._is_appended(tweet, exclude_reply, exclude_retweet):
                            # Append tweet to df_tweets
                            data = {'text': tweet['text'].replace('\n', u'。')}
                            for g in gets:
                                data[g] = tweet[g]
                            df_tweets = df_tweets.append(pd.DataFrame(data, index=[0]), ignore_index=True)

                    # Set id of last tweet as max_id
                    params['max_id'] = tweets[-1]['id'] - 1
                    self._check_remaining_api(res, time_res_acquired)

        # Return df_tweets
        if len(df_tweets) == 0:
            return df_tweets
        else:
            return df_tweets.loc[:, gets + ['text']]

    def _is_appended(self, tweet, exclude_reply, exclude_retweet):
        if exclude_reply & exclude_retweet:
            return (tweet['in_reply_to_user_id'] is None) & ('retweeted_status' not in tweet)
        elif exclude_reply:
            return tweet['in_reply_to_user_id'] is None
        elif exclude_retweet:
            return 'retweeted_status' not in tweet
        else:
            return True

    def _check_remaining_api(self, res, time_res_aquired):
        # Print remaining API
        remaining_api = int(res.headers['x-rate-limit-remaining'])
        print('Remaining API: %s' % (remaining_api))

        # Sleep 15 minutes if there is no remain
        if remaining_api <= 1:
            time_to_stop = time_res_aquired + datetime.timedelta(minutes=15)
            print('There is no remaining API.\nSleeping until %s' % (time_to_stop))
            while True:
                if time_to_stop <= datetime.datetime.now():
                    break
                else:
                    time.sleep(1)
