"""Download data from the Studs Terkel Archive."""
from pathlib import Path

import click
import requests
import pandas as pd
from rich import print
from bs4 import BeautifulSoup


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
    this_dir = Path(__file__).parent
    out_dir = this_dir.parent / "data"
    out_dir.mkdir(exist_ok=True)
    out_path = out_dir / "links.csv"
    df.to_csv(out_path, index=False)


if __name__ == "__main__":
    cli()