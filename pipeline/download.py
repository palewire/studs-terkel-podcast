"""Download data from the Studs Terkel Archive."""
from pathlib import Path

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


if __name__ == "__main__":
    cli()