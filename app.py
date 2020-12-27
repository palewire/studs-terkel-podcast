import csv
from email import utils
from flask import Flask
from datetime import date
from dateutil.parser import parse
from flask import render_template, make_response
app = Flask(__name__)


@app.route('/')
def index():
    return render_template("index.html")


@app.route('/feed.xml')
def feed():
    t = render_template("feed.xml", item_list=DATA)
    r = make_response(t)
    r.headers['Content-type'] = 'text/xml; chartset=utf-8'
    return r


def format_datetime(s):
    dt = parse(s)
    return utils.format_datetime(dt)


def format_duration(s):
    parts = s.split(", ")
    hours, minutes, seconds = 0, 0, 0
    parse_str = lambda x: int(x.split(" ")[0].strip())
    for p in parts:
        if 'hour' in p:
            hours += parse_str(p)
        elif 'minute' in p:
            minutes += parse_str(p)
        elif 'second' in p:
            seconds += parse_str(p)
    return "%02d:%02d:%02d" % (hours, minutes, seconds)


with open("./data/feed.csv", "r") as f:
    reader = csv.DictReader(f)
    DATA = []
    TODAY = date.today()
    for row in reader:
        row['date_rfc822'] = format_datetime(row['feed_date'])
        row['duration'] = format_duration(row['duration'])
        dt = parse(row['feed_date'])
        if dt.date() <= TODAY:
            DATA.append(row)
