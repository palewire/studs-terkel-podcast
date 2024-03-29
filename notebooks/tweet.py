import sys
import pytz
import pandas as pd
from datetime import datetime


def main(max_title_length=150):
    """
    Get the latest post to tweet.
    """
    # Read in the feed
    df = pd.read_csv("./data/feed.csv", parse_dates=["feed_date"]).sort_values("feed_date")

    # Set the current time in Chicago
    tz = pytz.timezone('America/Chicago')
    today = datetime.now(tz)

    # Create filters to get the latest untweeted episodes
    past_filter = df.feed_date.dt.date <= today.date()
    untweeted_filter = df.tweeted != "x"

    # Get the earliest one that hasn't been tweeted yet
    untweeted_df = df[past_filter & untweeted_filter]
    to_tweet = untweeted_df.iloc[0]

    # Format a tweet and write it out to the console
    if len(to_tweet.title) > max_title_length:
        title = to_tweet.title[0:max_title_length] + '...'
    else:
        title = to_tweet.title
    txt = f"{title}. Subscribe at https://studs.show to listen."
    sys.stdout.write(txt)

    # Mark the tweet as tweeted and write back to the source file
    df.loc[df.archive_url == to_tweet.archive_url, 'tweeted'] = "x"
    df.to_csv("./data/feed.csv", index=False)


if __name__ == '__main__':
    main()
