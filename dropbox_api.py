import dropbox

import config

class API:
    def __init__(self):
        conf = config.get_config()
        # Create connection to Dropbox.
        self.dbx = dropbox.Dropbox(
            app_key = conf['dropbox_app_key'],
            app_secret = conf['dropbox_app_secret'],
            oauth2_refresh_token = conf['dropbox_refresh_token']
        )
    
    def upload_file(self, file, share=True):
        ''' Upload file to Dropbox.'''
        # Upload file.
        with open(f'tmp/{file}', "rb") as f:
            self.dbx.files_upload(f.read(), f'/{file}', mode=dropbox.files.WriteMode("overwrite"))
        if share:
            shared_link = self.share_file(file)
            return shared_link

    def share_file(self, file):    
        ''' Share file on Dropbox.''' 
        # Get shared link.
        shared_link_metadata = self.dbx.sharing_create_shared_link_with_settings(f'/{file}')
        shared_link = shared_link_metadata.url
        return shared_link.replace('?dl=0', '?dl=1')

