"""Download data from the Studs Terkel Archive."""
import time
from pathlib import Path
import urllib.parse
import urllib.request

import click
import requests
import pandas as pd
from rich import print
from rich.progress import track
from bs4 import BeautifulSoup

THIS_DIR = Path(__file__).parent
DATA_DIR = THIS_DIR.parent / "data"


@click.group()
def cli():
    """Download data from the Studs Terkel Archive."""
    pass


@cli.command()
def links():
    """Download all of the show links from the Studs Terkel Archive index."""
    # Get the page
    url = "https://studsterkel.wfmt.com/explore#t=date"
    r = requests.get(url)
    assert r.ok

    # Parse the page
    html = r.text
    soup = BeautifulSoup(html, "html.parser")

    # Pull out all the blocks
    year_list = soup.find_all(class_="prog_year_block")

    # Loop through them and grab all the URLs, which lead to program pages.
    link_list = []
    for year in year_list:
        a_list = year.find_all("a")
        link_list.extend([a['href'] for a in a_list])

    # Make sure the links are unique
    unique_links = list(set(link_list))

    # Print the total number
    print(f"Found {len(unique_links)} unique links.")

    # Convert to a Dataframe
    df = pd.DataFrame(unique_links, columns=["url"])

    # Add https://studsterkel.wfmt.com/ to the URLs
    df["url"] = df["url"].apply(lambda x: f"https://studsterkel.wfmt.com{x}")

    # Write it out to the data folder
    df.to_csv(DATA_DIR / "links.csv", index=False)


@cli.command()
def html():
    """Download all of the show pages from the Studs Terkel Archive."""
    # Load the links
    df = pd.read_csv(DATA_DIR / "links.csv")

    # Set the HTML dir
    html_dir = DATA_DIR / "html"
    html_dir.mkdir(exist_ok=True)

    # Convert the URL column to a list
    urls = df["url"].tolist()

    print(f"Downloading {len(urls)} HTML pages")
    for url in track(urls):
        # Get the target name of the file from the URL
        name = url.split("/")[-1] + ".html"

        # Set the output path
        path = html_dir / name

        # If it already exists, skip it
        if path.exists():
            continue

        # Otherwise, download it
        print(f"Requesting {url}")
        headers = {
            'User-Agent': 'Studs Terkel Radio Archive Scraper (github.com/palewire/studs-terkel-radio-feed/)',
        }
        r = requests.get(url, headers=headers)

        # If it fails, print a message and skip
        if not r.status_code == 200:
            print(f"Failed with status code {r.status_code}: {url}")
            continue

        # Write the file
        with open(path, "w") as fh:
            fh.write(r.text)

        # Wait a bit
        time.sleep(0.15)


@cli.command()
def metadata():
    """Parse all the program metadata."""
    # Set the HTML dir
    html_dir = DATA_DIR / "html"

    # Get a list of all the files in the HTML directory
    html_list = list(html_dir.glob("*.html"))

    # Print the total number
    print(f"Parsing metadata for {len(html_list)} HTML files")

    def _parse_meta(e):
        """Parse a grid cell of metadata from the bottom of a program page."""
        # Get all the p tags
        p_list = e.find_all("p")
        d = {}
        for p in p_list:
            # Split out the bolded text as the label
            label = p.strong.text
            p.strong.extract()
            # Keep the rest as the value
            value = p.text.strip()
            # Add to the dictionary
            d[label] = value
        # Return all dictionaries in this block
        return d

    metadata_list = []
    for path in track(html_list):
        # Open the page
        with open(path, "r") as fh:
            html = fh.read()
        
        # Parse the HTML
        soup = BeautifulSoup(html, "html.parser")
        
        # Pull out the title
        title = soup.find("h1").text
        
        # Parse out all metadata
        meta = {}
        for e in soup.find(class_="meta_data__section").find_all(class_="col-4"):
            meta.update(_parse_meta(e))
        
        # Grab the MP3 URL, if it exists
        media = soup.find(class_="audio_trigger")
        if media:
            mp3_url = media['data-track-url']
        else:
            mp3_url = None
        
        # Grab the synopsis, if it exists
        summary = soup.find(class_="program_synopsis__body")
        if summary:
            synopsis = summary.h2.text
        else:
            synopsis = None
        
        # Return the scraped data
        d = dict(
            title=title,
            mp3_url=mp3_url,
            archive_url="/programs/" + path.stem,
            synopsis=synopsis,
            **meta
        )
        metadata_list.append(d)

    # Convert it to a dataframe
    df = pd.DataFrame(metadata_list).rename(columns={
        "Broadcast Date": "broadcast_date",
        "Physical Format": "physical_format",
        "Digital Format": "digital_format",
        "Ownership": "ownership",
        "Language": "language",
        "Program Sponsor": "program_sponsor",
        "Duration": "duration"
    })

    # Calculate extra columns
    df.archive_url = df.archive_url.str.strip()
    df['has_mp3_url'] = ~pd.isnull(df.mp3_url)

    def _parse_date(s):
        if pd.isnull(s):
            return None
        try:
            month, day, year = s.split(" ")
        except ValueError:
            return None
        return pd.to_datetime(s)

    df['broadcast_datetime'] = df.broadcast_date.apply(_parse_date)
    df['broadcast_year'] = df.broadcast_datetime.dt.year
    df['broadcast_month'] = df.broadcast_datetime.dt.month
    df['broadcast_monthday'] = df.broadcast_datetime.dt.day

    # Print a report on how many have MP3s
    print(f"Found {df.has_mp3_url.sum()} MP3 URLs out of {len(df)} programs.")

    # Sort it by month and day
    df = df.sort_values("broadcast_datetime")

    # Write it out to the data folder
    df.to_csv(DATA_DIR / "programs.csv", index=False)


@cli.command()
def mp3():
    """Download all the MP3 files."""
    # Load the metadata
    df = pd.read_csv(DATA_DIR / "programs.csv")

    # Set the MP3 dir
    mp3_dir = DATA_DIR / "mp3"
    mp3_dir.mkdir(exist_ok=True)

    # Filter to just the rows with MP3 URLs
    df = df[df.has_mp3_url].copy()

    # Convert the URL column to a list
    urls = df["mp3_url"].tolist()

    print(f"Downloading {len(urls)} MP3 files")
    for url in track(urls):
        # Get the target name of the file from the URL
        name = url.split("/")[-1].replace("published%2F", "")

        # Set the output path
        path = mp3_dir / name

        # If it already exists, skip it
        if path.exists():
            continue

        # Otherwise, download it
        print(f"Requesting {url}")
        opener = urllib.request.build_opener()
        opener.addheaders = [("Referer", "https://studsterkel.wfmt.com/")]
        urllib.request.install_opener(opener)
        urllib.request.urlretrieve(url, path)

        # Wait a bit
        time.sleep(0.15)


if __name__ == "__main__":
    cli()