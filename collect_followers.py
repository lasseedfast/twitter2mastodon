import re
from time import sleep

import sql_api
import dropbox_api
import twitter_api

def user_data(usernames, fields=['public_metrics']):
    twitter = twitter_api.API()
    url = f"https://api.twitter.com/2/users/by?usernames={','.join(usernames)}&user.fields={','.join(fields)}"
    json_response = twitter.connect_to_endpoint(url)
    return json_response

def _sleep(s):
    """
    Sleep and print.
    """
    for i in range(s, 0, -1):
        sleep(1)
        print(' ', f'{i}   ', end='\r')

def get_followings(username):
    followings = []
    pagination_token = {}

    # Get basic data, info on API.
    json_response = user_data([username])
    id = json_response['data'][0]['id'] # To use in the coming requests

    ## Get followers for the account
    pagination_token = {}
    while True:
        twitter = twitter_api.API()
        result = twitter.connect_to_endpoint(
            f"https://api.twitter.com/2/users/{id}/following", 
            params = {'pagination_token': pagination_token, "max_results": 1000, 'user.fields': 'description'}
            )
        if 'errors' in result:
            try:
                error_title = result['errors'][0]['title']
                if error_title == 'Authorization Error':
                    return 'private'
            except:
                break
        if 'data' not in result:
            break
        # Append data to list json_response_list.
        followings += result['data']
        # Get token used for requesting the next page.
        if 'next_token' in result['meta']:
            pagination_token = result['meta']['next_token'] 
            _sleep(3) 
        else: # If there is no moreresults.
            break
    return followings


def update_db(followings):
    """ Update Mastodon username DB. Returns the followings who has a Mastodon hansle in their bio. """
    # Create SQL-query.
    l = []
    tweeters_with_mastodon = []
    for i in followings:
        m_username = extract_mastodon_handle(i["description"].replace('"', "'")) # Can't be double quotes when sending to SQL.
        if m_username:
            t_username = i['username']
            m_username = m_username.strip("@")
            l.append(f'("{t_username}", "{m_username}")')
            tweeters_with_mastodon.append(t_username)
    columns = '"t_username", "m_username"'
    sql = f'INSERT OR REPLACE INTO  usernames ({columns}) VALUES {", ".join(l)}'
    # Put data into DB.
    db = sql_api.DB()
    db.commit(sql)
    return tweeters_with_mastodon
    

def extract_mastodon_handle(text):
    """ Get a mastodon alias form a text (assuming a word with 
    two @ and a . in the later part of the wordis a mastodon alias). """
    handle = re.search(r'@\w+@\w+.\w+', text)
    if handle:
        handle = handle.group()
    else:
        handle = False
    return handle


def export_followings(users, t_username):
    """ Export CSV-file with accounts to follow. """
    db = sql_api.DB()
    sql = 'select * from usernames'
    sql = f"select m_username from usernames where t_username in ('" + "','".join(users) + "')"
    m_usernames = [i['m_username'] for i in db.select(sql)]
    # Write CSV-file.
    with open(f'tmp/{t_username}_followings.csv', 'a+') as f:
        f.truncate(0)
        f.write('Account address,Show boosts,Notify on new posts,Languages\n')
        for m_username in m_usernames:
            f.write(f'{m_username},true,false,\n')

    return f"{t_username}_followings.csv"


if __name__ == "__main__":
    import sys
    if len(sys.argv) > 1:
        username = sys.argv[1]
    else:
        username = input('Your Twitter username : ')
    # Remove @ and spaces from username.
    username = username.replace('@', '').replace(' ', '')

    #* Run the script: 
    #* 1) Get the accounts the user follows
    #* 2) Export CSV with usernames.
    #* 3) Upload to Dropbox and share file (requires a Dropbox developer account/token).
    
    twitter = twitter_api.API()
    followings = get_followings(username)
    followings = update_db(followings)
  
    filename = export_followings(followings, username)

    # Share to dropbox    
    dropbox = dropbox_api.API()
    shared_file_url = dropbox.upload_file(filename)
    print(shared_file_url)
