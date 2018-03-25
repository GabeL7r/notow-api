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


def parse_sign(text, current_date):

    numeric_map = ['ZERO', 'ONE', 'TWO', 'THREE', 'FOUR', 'FIVE', 'SIX', 'SEVEN', 'EIGHT', 'NINE']
    common_days = ['MON', 'TUE', 'WED', 'THU', 'FRI', 'SAT', 'SUN']
    common_minutes = [1, 2, 5, 10, 15, 20, 30]
    time_denominations = ['MINUTE', 'HOUR']
    time_delimeters = ['-', 'THRU', 'TO']
    broad_statements = ['ANY', 'EVERY']

    time_range_regex = re.compile(r'^\d{1,2}[aA|pP][.]?[mM][.]?-\d{1,2}[aA|pP][.]?[mM][.]?$')
    alt_text = 'ONE HOUR PARKING 9AM-7PM'

    current_week_day = common_days[current_date.weekday()]

    split_text = text.split('PARKING')
    time_limit = split_text[0]
    when_rule_is_valid = split_text[1]
    can_you_park_here = True

    if not any(day in when_rule_is_valid for day in common_days):
        print("This sign doesn't specify a particular day, so it might apply to us. Keep checking.\n")
        if any(statement in when_rule_is_valid for statement in broad_statements):
            print("You can't park here. Sorry.\n")
            can_you_park_here = False
        else:
            temp_regex_string = '[' + '|'.join(time_delimeters) + ']'
            time_delimiter_regex = re.compile(r'{}'.format(temp_regex_string))
            # Check times
            time_range_strings = re.split(time_delimiter_regex, when_rule_is_valid)
            time_range_strings = [time.strip(' ') for time in time_range_strings]   # Strip spaces
            min_time = re.split('(\d+)', time_range_strings[0])[1:]
            max_time = re.split('(\d+)', time_range_strings[1])[1:]

            time_range_ints = [time_to_int(min_time), time_to_int(max_time)]

            print("You can park here from " + str(time_range_ints[0]) + " to " + str(time_range_ints[1]))

        # we need to check the times, compared to our current time
    elif current_week_day in when_rule_is_valid:
        print("This sign specifically applies to today. Keep checking.")
        # we need to check the times for sure, maybe compount this condition with the following
    else:
        print("This sign specified a day or days, but did not specify today. It does not apply.")

    return can_you_park_here

def time_to_int(time):
    pm_regex = re.compile(r'[pP][.]?[mM][.]?')

    if time[0] is '12' and not re.match(pm_regex, time[1]):
        time[0] = 0
    elif re.match(pm_regex, time[1]):
        time[0] = int(time[0]) + 12

    return time[0]
