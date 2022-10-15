"""
A Flask site for https://studs.show
"""
import csv
from email import utils
from flask import Flask
from datetime import date, datetime
from dateutil.parser import parse
from flask import render_template, make_response
app = Flask(__name__)


@app.route('/')
def index():
    """
    The homepage.
    """
    return render_template("index.html")


@app.route('/feed.xml')
def feed():
    """
    The RSS feed.
    """
    t = render_template(
        "feed.xml",
        item_list=DATA,
        last_build_date=utils.format_datetime(datetime.now())
    )
    r = make_response(t)
    r.headers['Content-type'] = 'text/xml; chartset=utf-8'
    return r


def format_datetime(s):
    """
    Format a datetime string in RFC822 format for RSS.
    """
    dt = parse(s)
    return utils.format_datetime(dt)


def format_duration(s):
    """
    Format the duration of a recording for iTunes RSS format.
    """
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


# Read in our raw data and format it for the feed
with open("./data/feed.csv", "r") as f:
    reader = csv.DictReader(f)
    DATA = []
    TODAY = date.today()
    for row in reader:
        row['date_rfc822'] = format_datetime(row['feed_date'])
        row['duration'] = format_duration(row['duration'])
        row['feed_date'] = parse(row['feed_date']).date()
        try:
            row['broadcast_datetime'] = parse(row['broadcast_datetime'])
        except:
            row['broadcast_datetime'] = None
        # Do not allow in items that will published in the future
        if row['feed_date'] <= TODAY:
            DATA.append(row)
