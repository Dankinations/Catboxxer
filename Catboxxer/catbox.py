import requests
import os
from requests_toolbelt import MultipartEncoder, MultipartEncoderMonitor
import utils

class catboxAPI:
    REQUEST_URL = "https://catbox.moe/user/api.php"

    def __init__(self, hash: str):
        self.hash = hash

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
                return response.text
            except:
                utils.displayNotification("Catboxxer", "There was an error uploading your file!", icon = utils.toastIcon)
            