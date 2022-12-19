Simple script to find out if Twitter accounts one is following are on Mastodon. Identifying mastodon handles from Twitter accounts' bio, adding them to a CSV file, uploading that file to Dropbox and then answering with a link to a shared Dropbox file.

_To run this you'll need:_
- [Twitter API credentials](https://developer.twitter.com/en/docs/twitter-api)
- [Dropbox API credentials](https://www.dropbox.com/developers/)

When you have created a bot accound and got your keys for Twitter and Dropbox API, and Python on installed, run
```
pip install -r requirements.txt
```
and then twitterbot.py. This will set up a json-file with credentials (config.json) and start the bot.

Please keep in mind that Twitter tends to lock down anything related to Mastodon when you're writing your bio and tweets. [I didn't in my first attempt](https://twitter.com/lasseedfast/status/1604850583940354049)...
