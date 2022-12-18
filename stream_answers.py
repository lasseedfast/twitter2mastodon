import json
import time
import requests

import collect_followers
import sql_api
import twitter_api


def stream(tweet_id):
    """ Monitor answers to a tweet. """
    # Make connection to SQL databse.
    db = sql_api.DB()
    api = twitter_api.API()

    rules = api.get_rules()
    api.delete_all_rules(rules)
    api.set_rules(tweet_id)
    response = requests.get(
        "https://api.twitter.com/2/tweets/search/stream?expansions=referenced_tweets.id,author_id", auth=api.bearer_oauth, stream=True,
    )
    for response_line in response.iter_lines():
        if response_line:
            json_response = json.loads(response_line)
            try:
                twitter_username =  json_response['includes']['users'][0]['username']
                mastodon_username = collect_followers.extract_mastodon_handle(json_response['includes']['tweets'][0]['text'])
                
                # Add Mastodon username to db.
                columns = '"t_username", "m_username"'
                values = [f'"{twitter_username}"', f'"{mastodon_username}"']
                sql = f'INSERT OR REPLACE INTO  usernames ({columns}) VALUES ({", ".join(values)})'
                db.commit(sql)

                # Add reply to queue
                id = str(json_response['data']['id'])
                columns = '"t_username", "tweet_id", "timestamp"'
                values = [f'"{twitter_username}"', f'"{id}"', str(int(time.time()))]
                sql = f'INSERT OR REPLACE INTO  queue ({columns}) VALUES ({", ".join(values)})'
                db.commit(sql)
            except KeyError:
                pass


if __name__ == "__main__":

    import sys
    if len(sys.argv) > 1:
        tweet_id = sys.argv[1]
    else:
        tweet_id = input('Tweet ID: ')
    
    stream(tweet_id)
