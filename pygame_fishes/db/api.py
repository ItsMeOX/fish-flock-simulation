import firebase_admin
from firebase_admin import credentials, storage
import datetime

class Firebase:
    def __init__(self):
        cred = credentials.Certificate("./db/key.json")
        firebase_admin.initialize_app(cred)

        storageURL = 'dti-drawing.appspot.com'
        app = firebase_admin.initialize_app(cred, {
            'storageBucket': storageURL,
        }, name='storage')

        self.bucket = storage.bucket(app=app)
        

    def get_imageURL(self, bucket_name, img_name, extension = 'png'):
        '''
        bucket_name: user_name
        img_name: username_date.png
        '''
        blob = self.bucket.blob(f"drawings/{bucket_name}/{img_name}.{extension}")
        imgURL = blob.generate_signed_url(datetime.timedelta(seconds=1110), method='GET')
        print(imgURL)
        return imgURL

    def list_buckets(self):
        for b in list(self.bucket.list_blobs()):
            print(b)

if __name__ == '__main__':
    import requests
    from io import BytesIO
    from PIL import Image

    firebase = Firebase()
    firebase.list_buckets()
    # response = requests.get(firebase.get_imageURL('fff', 'fff_1712646657298'))

    # img = BytesIO(response.content)
    # im = Image.open(img)
    # im.show()