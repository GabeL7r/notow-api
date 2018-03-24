from chalice import Chalice
import boto3

app = Chalice(app_name='reactathon-api')


@app.route('/')
def index():
    return {'hello': 'world'}


@app.route('/detect')
def detect_text_handler(image, context):

    rekognition = boto3.client("rekognition", "us-west-2")
    response = rekognition.detect_text(Image={
        "Bytes": image.encode()
    })

    return {
        'message' : response
    }
