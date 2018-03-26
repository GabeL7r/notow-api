import boto3
import base64


def detect_text_handler(image, context):

    rekognition = boto3.client("rekognition", "us-west-2")
    response = rekognition.detect_text(Image={
        "Bytes": base64.decodestring(image)
    })

    return {
        'message' : response
    }
