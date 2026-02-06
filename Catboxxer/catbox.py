import requests
import os
from requests_toolbelt import MultipartEncoder, MultipartEncoderMonitor
from CTkMessagebox import CTkMessagebox
import utils
import cache

class catboxAPI:
    REQUEST_URL = "https://catbox.moe/user/api.php"

    def __init__(self, hash:str):
        self.hash = hash
        cache.update_cache("r",True,override=hash)

    def upload_file(self,file:str,set_progress:callable):
        if not file: return None
        with open(file,"rb") as f:
            encoder = MultipartEncoder(
                fields={
                    'reqtype': 'fileupload',
                    'userhash': self.hash,
                    'fileToUpload': (os.path.basename(file), f, 'application/octet-stream'),
                }
            )

            monitor = MultipartEncoderMonitor(encoder, lambda monitor: set_progress(monitor.bytes_read) )

            try:
                response = requests.post(
                    self.REQUEST_URL, 
                    data=monitor, 
                    headers={'Content-Type': monitor.content_type
                })

                if not "://" in response.text:
                    raise Exception(f"{response.text}")
                
                cache.add_file(response.text)
                return response.text
            except Exception as e:
                CTkMessagebox(title="Catboxxer", message=f"There was an error uploading your file\nException: {e}", icon = utils.catboxICO, sound=True)
    
    def create_album(self, title="New Album", desc="", files=(None)):
        try:
            response = requests.post(
            self.REQUEST_URL,
            data={
                'reqtype': 'createalbum',
                'userhash': self.hash,
                'files' : files,
                'desc': desc,
                'title':title 
              }
            )

            if not "://" in response.text:
                raise Exception(f"{response.text}")
            return response.text
        except Exception as e:
            CTkMessagebox(title="Catboxxer", message=f"There was an error creating your album\nException: {e}", icon = utils.catboxICO, sound=True)
    
    def delete_files(self, files=(None)):
        try:
            response = requests.post(
            self.REQUEST_URL,
            data={
                'reqtype': 'deletefiles',
                'userhash': self.hash,
                'files' : files,
              }
            )

            if not "successfully deleted" in response.text:
                raise Exception(f"{response.text}")
            return response.text
        except Exception as e:
            CTkMessagebox(title="Catboxxer", message=f"There was an error deleting your file{len(files) > 1 and "s" or ""}\nException: {e}", icon = utils.catboxICO, sound=True)

    def add_files_to_album(self,albumid:str,files=(None)):
        try:
            response = requests.post(
            self.REQUEST_URL,
            data={
                'reqtype': 'addtoalbum',
                'userhash': self.hash,
                'files': files,
                'short': albumid
              }
            )
            print(response.text)
            if not "://" in response.text:
                raise Exception(f"{response.text}")
            return response.text
        except Exception as e:
            CTkMessagebox(title="Catboxxer", message=f"There was an error adding files to your album {albumid}\nException: {e}", icon = utils.catboxICO, sound=True)

    def remove_files_from_album(self,albumid:str,files=(None)):
        try:
            response = requests.post(
            self.REQUEST_URL,
            data={
                'reqtype': 'removefromalbum',
                'userhash': self.hash,
                'files' : files,
                'short': albumid
              }
            )

            if not "://" in response.text:
                raise Exception(f"{response.text}")
            return response.text
        except Exception as e:
            CTkMessagebox(title="Catboxxer", message=f"There was an error removing files from your album {albumid}\nException: {e}", icon = utils.catboxICO, sound=True)

    def delete_album(self,albumid:str):
        try:
            response = requests.post(
            self.REQUEST_URL,
            data={
                'reqtype': 'deletealbum',
                'userhash': self.hash,
                'short': albumid
              }
            )

            if not "://" in response.text:
                raise Exception(f"{response.text}")
            return response.text
        except Exception as e:
            CTkMessagebox(title="Catboxxer", message=f"There was an error deleting your album {albumid}\nException: {e}", icon = utils.catboxICO, sound=True)