import os
import json


def create_config():
    # Create a config file. #* Add more keys if necessary.
    config = {}
    with open("config.json", "w") as f:
        # Token for Twitter.
        twitter_token = input("Twitter token bearer: ")
        if len(twitter_token) > 5:
            config["twitter_token"] = twitter_token
            config['bot_username'] = input('Bot username: ')
            config['twitter_consumer_key'] = input('Twitter consumer key: ')
            config['twitter_consumer_secret'] = input('Twitter consumer secret: ')
            config['twitter_access_token_key'] = input('Twitter access token key: ')
            config['twitter_access_token_secret'] = input('Twitter access token secret')

            config['dropbox_app_key'] = input('Dropbox app key:')
            config['dropbox_app_secret'] = input('Dropbox app secret:')
            
            if input('Do you have refresh token? (y/n)') not in ['y', 'yes']:
                # Login to Dropbox using a webbrowser to get refresh token.
                oauth_result = get_dropbox_tokens(config['dropbox_app_key'])
                config['dropbox_refresh_token'] = oauth_result.refresh_token
                config['dropboc_access_token'] = oauth_result.access_token
            
            config['dropbox_refresh_token'] = input('Dropbox refresh token:')
            config['dropboc_access_token'] = input('Dropbox access token:')
            
        else:
            print("Twitter credentials skipped.")
        # Token for Dropbox.
        dropbox_token = input("Dropbox token: ")
        if len(dropbox_token) > 5:
            config["dropbox_token"] = dropbox_token
        else:
            print("Dropbox token skipped.")
        # Write to file.
        json.dump(config, f)
    return config


def update_config(key, value):
    # Check if the config files with the token exist, create it if not.
    if os.path.exists("config.json"):
        with open("config.json") as f:
            config = json.load(f)
            config[key] = value
    else:
        print("No config file, creating one...")
        config = create_config()
        config[key] = value
    
    # Write updated config to file.
    with open("config.json", "w") as f:
        json.dump(config, f)
    return config


def get_config():
    # Returns a config file, creating one if not existing.
    if os.path.exists("config.json"):
        with open("config.json") as f:
            config = json.load(f)
    else:
        config = create_config()
    return config


def get_dropbox_tokens(app_key):
    from dropbox import DropboxOAuth2FlowNoRedirect
    '''
    Populate your app key in order to run this locally
    '''

    auth_flow = DropboxOAuth2FlowNoRedirect(app_key, use_pkce=True, token_access_type='offline')

    authorize_url = auth_flow.start()
    print("1. Go to: " + authorize_url)
    print("2. Click \"Allow\" (you might have to log in first).")
    print("3. Copy the authorization code.")
    auth_code = input("Enter the authorization code here: ").strip()

    oauth_result = auth_flow.finish(auth_code)
    return oauth_result


if __name__ == "__main__":
    os.chdir(os.path.dirname(os.path.realpath(__file__)))
    create_config()
    print(f'Configuration file created at {os.path.realpath("config.json")}.')
