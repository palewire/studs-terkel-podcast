import sys
import pytz
import pandas as pd
from datetime import datetime


def main():
    """
    Get the latest post to tweet.
    """
    df = pd.read_csv("./data/feed.csv", parse_dates=["feed_date"]).sort_values("feed_date")

    tz = pytz.timezone('America/Chicago')
    today = datetime.now(tz)

    past_filter = df.feed_date.dt.date <= today.date()
    untweeted_filter = df.tweeted != True

    untweeted_df = df[past_filter & untweeted_filter]
    to_tweet = untweeted_df.iloc[0]

    txt = f"First broadcast on {to_tweet.broadcast_date}. {to_tweet.title}"
    sys.stdout.write(txt)

    # df.loc[df.archive_url == to_tweet.archive_url, 'tweeted'] = True
    # df.to_csv("../data/feed.csv")


if __name__ == '__main__':
    main()