from chalice import Chalice, Response
import json, re

app = Chalice(app_name='reactathon-api')
app.debug = True

@app.route('/')
def index():
    return {'hello': 'world'}

@app.route('/parse', methods=['POST'])
def parse_handler():
    request = app.current_request
    data = []
    if request.method == 'POST' and 'message' in request.json_body:
        data = request.json_body['message']
        parse()
    else:
        return Response(
                    body={"error": "Message not provided!"},
                    status_code=400,
                    headers={'Content-Type': 'application/json'}
                    )

    return data

# parse() returns an array of valid parking times each day
def parse(text = 'NO PARKING ANY TIME'):
    numeric_map = ['ZERO', 'ONE', 'TWO', 'THREE', 'FOUR', 'FIVE', 'SIX', 'SEVEN', 'EIGHT', 'NINE']
    common_days = ['SUN', 'MON', 'TUE', 'WED', 'THU', 'FRI', 'SAT']
    common_minutes = [1, 2, 5, 10, 15, 20, 30]
    time_delimeters = ['MINUTE', 'HOUR']

    alt_text = 'ONE HOUR PARKING 9AM-7PM'

    split_text = text.split('PARKING')
    time_limit = split_text[0]
    when = split_text[1]

    if 'NO' in split_text[0]:




    # case for number followed by delimeter (2 hour parking, 30 minute parking)
    elif
