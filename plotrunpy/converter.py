import datetime
import re

INPUT_DATE_FORMATS = [
    '%Y-%m-%d %H:%M:%S',
    '%Y-%m-%d %H:%M:%S.%f',
    #'%Y-%m-%d %H:%M:%S%z',
    #'%Y-%m-%d %H:%M:%S.%f%z',
]
OUTPUT_DATE_FORMAT = '%Y-%m-%dT%H:%M:%SZ'

def parse_time(string):
    if not string:
        return None
    if 'T' in string:
        string = string.replace('T', ' ')
    if 'Z' in string:
        string = string.replace('Z', '')
    if '.' in string:
        string = string.split('.')[0]
    if len(string) > 19:
        # remove the timezone part
        d = max(string.rfind('+'), string.rfind('-'))
        string = string[0:d]
    if len(string) < 19:
        # string has some single digits
        p = '^([0-9]{4})-([0-9]{1,2})-([0-9]{1,2}) ([0-9]{1,2}):([0-9]{1,2}):([0-9]{1,2}).*$'
        s = re.findall(p, string)
        if len(s) > 0:
            string = '{0}-{1:02d}-{2:02d} {3:02d}:{4:02d}:{5:02d}'\
                .format(*[int(x) for x in s[0]])
    for date_format in INPUT_DATE_FORMATS:
        try:
            return datetime.datetime.strptime(string, date_format)
        except ValueError:
            pass
    raise Exception('Invalid time: %s' % string)



class FloatConverter(object):
    def __init__(self):
        self.from_string = lambda string: None if string is None else float(string.strip())
        self.to_string = lambda flt: str(flt)


class IntConverter(object):
    def __init__(self):
        self.from_string = lambda string: None if string is None else int(string.strip())
        self.to_string = lambda flt: str(flt)


class TimeConverter(object):
    def from_string(self, string):
        try:
            return parse_time(string)
        except:
            return None
    def to_string(self, time):
        return time.strftime(OUTPUT_DATE_FORMAT) if time else None


INT_TYPE = IntConverter()
FLOAT_TYPE = FloatConverter()
TIME_TYPE = TimeConverter()
