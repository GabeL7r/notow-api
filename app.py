from chalice import Chalice, Response
from datetime import datetime
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
        # date = request.json_body['date'] # uncomment me later!

        parse_sign(data, datetime.now())
    else:
        return Response(
                    body={"error": "Message not provided!"},
                    status_code=400,
                    headers={'Content-Type': 'application/json'}
                    )

    return request.json_body

# parse() returns an array of valid parking times each day
"""
[

]
"""
def parse_sign(text, current_date):

    numeric_map = ['ZERO', 'ONE', 'TWO', 'THREE', 'FOUR', 'FIVE', 'SIX', 'SEVEN', 'EIGHT', 'NINE']
    common_days = ['MON', 'TUE', 'WED', 'THU', 'FRI', 'SAT', 'SUN']
    common_minutes = [1, 2, 5, 10, 15, 20, 30]
    time_delimeters = ['MINUTE', 'HOUR']

    time_range_regex = re.compile(r'^\d{1,2}[aA|pP][mM]-\d{0,2}[aA|pP][mM]$')
    alt_text = 'ONE HOUR PARKING 9AM-7PM'

    current_week_day = common_days[current_date.weekday()]

    split_text = text.split('PARKING')
    time_limit = split_text[0]
    when_rule_is_valid = split_text[1]

    if current_week_day in when_rule_is_valid:
        print("this sign specifically applies to today")
    elif not any(day in when_rule_is_valid for day in common_days):
        print("this sign doesn't specify any day")
    else:
        print("this sign may not matter")

    # if time_limit is 'NO':
    #     # Figure out when this rule applies...
    #     if time_range_regex.search(when_rule_is_valid):
    #         print('doop')
    #         # do something
