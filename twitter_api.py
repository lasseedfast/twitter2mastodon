import requests
import config
from requests_oauthlib import OAuth2Session, OAuth1Session

class API:
    def __init__(self):

        conf = config.get_config()
        if 'twitter_token' not in conf:
            config.update('twitter_token', input('Twitter token:'))
        self.bearer_token = conf['twitter_token']
        self.user_agent = "v2UserLookupPython"
        self.pagination_tokens = {}
        self.consumer_key = conf['twitter_consumer_key']
        self.consumer_secret = conf['twitter_consumer_secret']
        self.access_token_key = conf['twitter_access_token_key']
        self.access_token_secret = conf['twitter_access_token_secret']
        self.post_auth = OAuth1Session(
            self.consumer_key,
            client_secret=self.consumer_secret,
            resource_owner_key=self.access_token_key,
            resource_owner_secret=self.access_token_secret,
            )
    
    def post_tweet(self, text='', params={}):
        # Making the request
        if 'text' not in params:
            params['text'] = text
        response = self.post_auth.post("https://api.twitter.com/2/tweets",json=params)
        return response

    def bearer_oauth(self, r):
        """ Method required by bearer token authentication. """
        r.headers["Authorization"] = f"Bearer {self.bearer_token}"
        r.headers["User-Agent"] = self.user_agent
        return r

    def connect_to_endpoint(self, url, mode='GET', params='', pagination_token=False):
        """ Get the data from Twitter. """
        # Update pagination token.
        if pagination_token:
            for key, value in pagination_token:
                self.pagination_tokens[key] = value
        response = requests.request(mode, url, auth=self.bearer_oauth, params=params)
        if response.status_code != 200:
            raise Exception(f"Request returned an error: {response.status_code} {response.text}")

        return response.json()

    def bearer_oauth(self, r):
        """
        Method required by bearer token authentication.
        """

        r.headers["Authorization"] = f"Bearer {self.bearer_token}"
        r.headers["User-Agent"] = "v2FilteredStreamPython"
        return r

    def get_rules(self):
        response = requests.get(
            "https://api.twitter.com/2/tweets/search/stream/rules", auth=self.bearer_oauth
        )
        if response.status_code != 200:
            raise Exception(
                "Cannot get rules (HTTP {}): {}".format(response.status_code, response.text)
            )
        return response.json()


    def delete_all_rules(self, rules):
        if rules is None or "data" not in rules:
            return None

        ids = list(map(lambda rule: rule["id"], rules["data"]))
        payload = {"delete": {"ids": ids}}
        requests.post(
            "https://api.twitter.com/2/tweets/search/stream/rules",
            auth=self.bearer_oauth,
            json=payload
        )

    def set_rules(self, tweet_id):
        # You can adjust the rules if needed
        rules = [
            {"value": f"in_reply_to_tweet_id:{tweet_id}"}
        ]
        payload = {"add": rules}
        requests.post(
            "https://api.twitter.com/2/tweets/search/stream/rules",
            auth=self.bearer_oauth,
            json=payload,
        )

    def retweeted_by(self, id):
        """ Constructs an URL to look up who has retweeted a certain tweet. """
        id = "1354143047324299264"
        url = f"https://api.twitter.com/2/tweets/{id}/retweeted_by"
        return url

    def reply_with_url(self, tweet_id, url, username):
       
        params = {"reply": {"in_reply_to_tweet_id": str(tweet_id)}, "text": f"Hi {username}! Download a list of Mastodon users that you are following on Twitter: {url}"}
        self.post_tweet(params=params)