"""
Core XML Parsing of RSS documents. This is generally focused on RSS 2.0
"""
import requests
from xml.etree import ElementTree
from pprint import pprint
import csv
from pathlib import Path
from typing import NamedTuple, List

class SourceRSS(NamedTuple):
    """Extract of raw RSS data"""
    title: str
    link: str
    description: str
    pubDate: str


class ExpandedRSS(NamedTuple):
    """Data expanded by the :func:`decompose_the_title()` function"""
    title: str
    link: str
    description: str
    pubDate: str
    docket: str
    parties_title: str


def xml_reader(url) -> List[SourceRSS]:
    """
    Extract RSS data given a URL to read.

    The root document is the <rss> which has a single <channel>.

    This will gather "title", "link", "description", and "pubDate" from each item.

    :param url: URL to read.
    :return: All of the SourceRSS from the channel of the feed. List[SourceRSS]
    """
    items = []
    response = requests.get(url)
    rss = ElementTree.fromstring(response.content)
    channel = rss.find('channel')

    # If a visual dump is helpful...
    print(channel.findtext('title'))
    print(channel.findtext('link'))
    print(channel.findtext('description'))
    print(channel.findtext('lastBuildDate'))

    for item in channel.iter('item'):
        item_row = SourceRSS(
            title=item.findtext('title'),
            link=item.findtext('link'),
            description=item.findtext('description'),
            pubDate=item.findtext('pubDate'),
        )
        items.append(item_row)
    return items

def decompose_the_title(items: List[SourceRSS]) -> List[ExpandedRSS]:
    """
    Parse titles for court docket RSS feeds.

    :param items: A list of SourceRSS items built by xml_reader()
    :return: A new list of ExpandedRSS, with some additional attributes for each item.
    """
    new_items = []
    for row in items:
        docket, _, parties_title = row.title.partition(' ')
        _, _, real_docket = docket.partition(":")
        result = ExpandedRSS(
            title=row.title,
            link=row.link,
            description=row.description,
            pubDate=row.pubDate,
            docket=real_docket,
            parties_title=parties_title,
        )
        new_items.append(result)
    return new_items

def csv_writer(data: List[ExpandedRSS], output_path: Path) -> None:
    """
    Saves expanded data to a Path.

    :param data: List of ExpandedRSS items, built by :func:`decompose_the_title`.
    :param output_path: Path to which to write the file.
    """
    with output_path.open('w', newline='') as output_file :
        headings = ['title', 'docket', 'parties_title', 'link', 'description', 'pubDate']
        writer = csv.DictWriter(output_file, headings)
        writer.writeheader()
        for row in data:
            writer.writerow(row._asdict())

def demo():
    data1 = xml_reader("https://ecf.dcd.uscourts.gov/cgi-bin/rss_outside.pl")
    data1_decomposed = decompose_the_title(data1)
    csv_writer(data1_decomposed, Path("file1.csv"))

    data2 = xml_reader("https://ecf.nyed.uscourts.gov/cgi-bin/readyDockets.pl")
    data2_decomposed = decompose_the_title(data2)
    pprint(data2_decomposed)
    csv_writer(data2_decomposed, Path("file2.csv"))


if __name__ == "__main__":
    demo()