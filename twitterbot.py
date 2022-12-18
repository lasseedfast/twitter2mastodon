import subprocess

import os
import twitter_api
import sys

import config

def start_bot(default=True):
    print('Twitter bot started.')
    
    twitter = twitter_api.API()
    first_tweet = "Answer to this tweet to get a list of your twitter friends on Mastodon. If you include your own Mastodon username in the reply that username will be included in a database so that others can find you."
    
    if not default:
        print('\nShould I post this as a first tweet and instructions? (y/n)\n', first_tweet, '\n')
        
        if input('>>> ').lower() != 'y': # If custom first tweet.
            print('Write your first post and instructions:\n')
            first_tweet = input('>>> ')
            while len(first_tweet) > 140:
                print('Too long, max lenght 140. Try again:\n')
                first_tweet = input('>>> ')
    
    r_json = twitter.post_tweet(first_tweet).json()

    # Save the ID of the first tweet in the config.json file.
    first_tweet_id = r_json['data']['id']
    config.update_config('first_tweet_id', first_tweet_id)

    return first_tweet_id

if __name__ == "__main__":

    # Change working directory to the scripts' directory.
    os.chdir(os.path.dirname(os.path.realpath(__file__)))

    # Create the tmp folder if it does not exists.
    path_tmp = os.path.dirname(os.path.realpath(__file__)) + '/tmp'
    if not os.path.exists(path_tmp):
        os.mkdir(path_tmp)

    conf = config.get_config(check_for=['dropbox_refresh_token', 'twitter_access_token_secret'])

    if len(sys.argv) > 1:
        if sys.argv[1].lower() == 'start':
            if sys.argv[1].lower() == 'default':
                default = True
            else:
                default = False
            first_tweet_id = start_bot(default)
    else:
        if input('Start Twitter bot? (y/n) ') in ['yes', 'y']:
            conf  = config.get_config()
            if 'first_tweet_id' in conf:
                first_tweet_id = conf['first_tweet_id']
                print(f'Use this tweet as instructions? https://twitter.com/{conf["bot_username"]}/status/{first_tweet_id}')
                print('y/n')
                if input('>>> ').lower() != 'y':   
                    start_bot(default=False)
            else:
                first_tweet_id = start_bot(default=False)
        else:
            print('\nExiting...\n')
            exit()
    
    conf = config.get_config()

    print(f'You have posted your first tweet: https://twitter.com/{conf["bot_username"]}/status/{first_tweet_id}')

    # Start monitoring answers to the first tweet.    
    subprocess.Popen(['python', 'stream_answers.py', first_tweet_id], cwd=os.path.dirname(os.path.realpath(__file__)))

    # Start the answering machine.
    subprocess.run(['python', 'answering_machine.py'], cwd=os.path.dirname(os.path.realpath(__file__)))



