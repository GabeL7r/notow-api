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
        date = request.json_body['time']

        parse_sign(data, date)
    else:
        return Response(
                    body={"error": "Message not provided!"},
                    status_code=400,
                    headers={'Content-Type': 'application/json'}
                    )

    return request.json_body

def parse_sign(text, timestamp):
    current_date = timestamp_to_datetime(timestamp)
    common_days = ['MON', 'TUE', 'WED', 'THU', 'FRI', 'SAT', 'SUN']
    numeric_map = ['ZERO', 'ONE', 'TWO', 'THREE', 'FOUR', 'FIVE', 'SIX', 'SEVEN', 'EIGHT', 'NINE']
    common_minutes = [1, 2, 5, 10, 15, 20, 30]
    time_denominations = ['MINUTE', 'HOUR']


    split_text = text.split('PARKING')
    time_limit = split_text[0]
    when_rule_is_valid = split_text[1]
    parking_here_is_fine = False

    does_rule_apply = compare_time_to_sign(current_date, when_rule_is_valid)

    if does_rule_apply[0]:
        print("Rule applies!")
        if time_limit == 'NO':
            parking_here_is_fine = False
    else:
        print("Rule doesn't apply!")
        parking_here_is_fine = True

    return parking_here_is_fine

def timestamp_to_datetime(timestamp):
    return datetime.strptime(timestamp, '%Y-%m-%d %H:%M:%S.%f')

# True/False, does the sign apply to the user given current time?
def compare_time_to_sign(current_date, when_rule_is_valid):
    common_days = ['MON', 'TUE', 'WED', 'THU', 'FRI', 'SAT', 'SUN']
    broad_statements = ['ANY', 'EVERY']
    current_week_day = common_days[current_date.weekday()]
    # time_range_regex = re.compile(r'^\d{1,2}[aA|pP][.]?[mM][.]?-\d{1,2}[aA|pP][.]?[mM][.]?$')
    pm_regex = re.compile(r'[pP][.]?[mM][.]?')
    am_regex = re.compile(r'[aA][.]?[mM][.]?')

    if not any(day in when_rule_is_valid for day in common_days):   # day is not specified
        if any(statement in when_rule_is_valid for statement in broad_statements):
            # the rule applies; day is not specified, and broad statement is being used
            return [True, 0]
        else:
            # the rule applies iff the user's current time fits within sign's specified range
            return check_time_against_sign(current_date, when_rule_is_valid)
    elif current_week_day in when_rule_is_valid:    # today is specified
        if not re.search(am_regex, when_rule_is_valid) and not re.search(pm_regex, when_rule_is_valid):
            # the rule applies iff the user's current time fits within sign's specified range
            return [True, 0]
        else:
            return check_time_against_sign(current_date, when_rule_is_valid.split(current_week_day, 1)[1])
    else:
        return [False]

def check_time_against_sign(current_date, when_rule_is_valid):
    time_delimeters = ['-', 'THRU', 'TO']

    temp_regex_string = '[' + '|'.join(time_delimeters) + ']'
    time_delimiter_regex = re.compile(r'{}'.format(temp_regex_string))

    # Check times
    time_range_strings = re.split(time_delimiter_regex, when_rule_is_valid)
    time_range_strings = [time.strip(' ') for time in time_range_strings]   # Strip spaces

    min_time = re.split('(\d+)', time_range_strings[0])[1:]
    max_time = re.split('(\d+)', time_range_strings[1])[1:]
    time_range_ints = [time_to_int(min_time), time_to_int(max_time)]

    if time_range_ints[0] > time_range_ints[1]:     # second time is larger than first time; range wraps around EoD
        if current_date.hour >= time_range_ints[0]: # if current time is after min...
            time_remaining = 24 - current_date.hour + time_range_ints[1]
            return [True, time_remaining]
        if current_date.hour <= time_range_ints[1]: # if current time is before max...
            # the rule applies; range wraps around EoD, but user is still in range
            time_remaining = time_range_ints[1] - current_date.hour
            return [True, time_remaining]
        return [False]
    elif current_date.hour >= time_range_ints[0] and current_date.hour <= time_range_ints[1]:
        # the rule applies; the user's current hour is between min and max
        time_remaining = time_range_ints[1] - current_date.hour
        return [True, time_remaining]
    else:
        return [False, ]

def time_to_int(time):
    pm_regex = re.compile(r'[pP][.]?[mM][.]?')

    if time[0] == '12' and not re.match(pm_regex, time[1]):
        time[0] = 0
    elif re.search(pm_regex, time[1]) and time[0] != '12':
        time[0] = int(time[0]) + 12

    return int(time[0])
