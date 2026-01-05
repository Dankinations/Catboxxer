import requests
from alive_progress import alive_bar
import os
from requests_toolbelt import MultipartEncoder, MultipartEncoderMonitor

class catboxAPI:
    REQUEST_URL = "https://catbox.moe/user/api.php"

    def __init__(self, hash: str):
        self.hash = hash

    def upload_file(self,file:str,hideBar:bool=False):
        if not file: return None
        with open(file,"rb") as f:
            encoder = MultipartEncoder(
                fields={
                    'reqtype': 'fileupload',
                    'fileToUpload': (os.path.basename(file), f, 'application/octet-stream')
                }
            )

            with alive_bar(encoder.len, title="Uploading", unit="B", scale="SI") as bar:
                monitor = MultipartEncoderMonitor(encoder, lambda monitor: bar( monitor.bytes_read - bar.current  ) )

                response = requests.post(
                    self.REQUEST_URL, 
                    data=monitor, 
                    headers={'Content-Type': monitor.content_type
                })
            return response