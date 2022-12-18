import time

import collect_followers
import dropbox_api
import sql_api
import twitter_api


def main(tweet):
    # Make connection to Twitter.
    twitter = twitter_api.API()

    t_username = tweet["t_username"]
    followings = collect_followers.get_followings(t_username)
    if followings == 'private':
        twitter_api.reply_to_private(tweet["tweet_id"], t_username)
    followings = collect_followers.update_db(followings)

    filename = collect_followers.export_followings(followings, t_username)

    # Share to dropbox
    dropbox = dropbox_api.API()
    shared_file_url = dropbox.upload_file(filename)

    # Reply to tweet with url.
    twitter.reply_with_url(tweet["tweet_id"], shared_file_url, t_username)

    sql = f'DELETE FROM queue WHERE t_username == "{t_username}"'
    db.commit(sql)

if __name__ == "__main__":
    
    # Make connection to SQL databse.
    db = sql_api.DB()

    while True:
        tweet = db.select(f"SELECT * FROM queue ORDER BY timestamp LIMIT 1")
        if tweet != []:
            main(tweet[0])
        else:
            time.sleep(3)
