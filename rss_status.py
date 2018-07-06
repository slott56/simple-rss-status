"""
Core XML Parsing of RSS documents. This is generally focused on RSS 2.0
"""
import requests
from xml.etree import ElementTree
from pprint import pprint
import csv
from pathlib import Path
from urllib.parse import urlparse
import datetime
from typing import NamedTuple, List

class SourceRSS(NamedTuple):
    """Extract of raw RSS data"""
    title: str  #: The title
    link: str  #: The link
    description: str  #: The description
    pubDate: str  #: The publication date


class ExpandedRSS(NamedTuple):
    """
    Data expanded by the :func:`title_transform()` function.

    Note that the names of the fields in this class will be the column
    titles on saved CSV files. Any change here will be reflected in the files
    created.
    """
    title: str  #: The title
    link: str  #: The link
    description: str  #: The description
    pubDate: str  #: The publication date
    docket: str  #: The parsed docket from the title
    parties_title: str  #: The parsed parties from the title


def xml_reader(url: str) -> List[SourceRSS]:
    """
    Extract RSS data given a URL to read.

    The root document is the ``<rss>`` tag which has a single ``<channel>`` tag.
    The ``<channel>`` has some overall attributes, but contains a sequence
    of ``<item>`` tags.

    This will gather "title", "link", "description", and "pubDate" from each item
    and build a :class:`SourceRSS` object.

    It might be helpful to return the overall channel properties along with
    the list of items.

    :param url: URL to read.
    :return: All of the SourceRSS from the channel of the feed, List[SourceRSS].
    """
    items = []
    response = requests.get(url)
    rss = ElementTree.fromstring(response.content)
    channel = rss.find('channel')

    # Dump the overall channel properties
    print("title", channel.findtext('title'))
    print("link", channel.findtext('link'))
    print("description", channel.findtext('description'))
    print("last build date", channel.findtext('lastBuildDate'))

    for item in channel.iter('item'):
        item_row = SourceRSS(
            title=item.findtext('title'),
            link=item.findtext('link'),
            description=item.findtext('description'),
            pubDate=item.findtext('pubDate'),
        )
        items.append(item_row)
    return items

def title_transform(items: List[SourceRSS]) -> List[ExpandedRSS]:
    """
    A "transformation": this will parse titles for court docket RSS feeds.

    >>> from rss_status import title_transform, SourceRSS, ExpandedRSS

    The data is a list witha  single document [SourceRSS()]

    >>> data = [
    ... SourceRSS(
    ...    title='1:15-cv-00791 SAVAGE  v. BURWELL et al',
    ...    link='https://ecf.dcd.uscourts.gov/cgi-bin/DktRpt.pl?172013',
    ...    description='[Reply to opposition to motion] (<a href="https://ecf.dcd.uscourts.gov/doc1/04516660233?caseid=172013&de_seq_num=555" >137</a>)',
    ...    pubDate='Thu, 05 Jul 2018 06:26:07 GMT'
    ... ),
    ... ]
    >>> title_transform(data)
    [ExpandedRSS(title='1:15-cv-00791 SAVAGE  v. BURWELL et al', link='https://ecf.dcd.uscourts.gov/cgi-bin/DktRpt.pl?172013', description='[Reply to opposition to motion] (<a href="https://ecf.dcd.uscourts.gov/doc1/04516660233?caseid=172013&de_seq_num=555" >137</a>)', pubDate='Thu, 05 Jul 2018 06:26:07 GMT', docket='15-cv-00791', parties_title='SAVAGE  v. BURWELL et al')]

    :param items: A list of :class:`SourceRSS` items built by :func:`xml_reader`
    :return: A new list of :class:`ExpandedRSS`, with some additional attributes for each item.
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

def csv_dump(data: List[ExpandedRSS], output_path: Path) -> None:
    """
    Save expanded data to a file, given the Path.

    Note that the headers are the field names from the ExpandedRSS class definition.
    This assures us that all fields will be written properly.

    :param data: List of :class:`ExpandedRSS` items, built by :func:`title_transform`.
    :param output_path: Path to which to write the file.
    """
    with output_path.open('w', newline='') as output_file :
        headings = list(ExpandedRSS._fields)
        writer = csv.DictWriter(output_file, headings)
        writer.writeheader()
        for row in data:
            writer.writerow(row._asdict())


def csv_load(input_path: Path) -> List[ExpandedRSS]:
    """
    Recover expanded data from a file, given a Path.

    Note that the headers **must be** the field names from the ExpandedRSS class definition.
    If their isn't a trivial match, then this won't read properly.

    :param input_path: Path from which to read the file.
    :returns: List of ExpandedRSS objects used to compare previous day's feed
        with today's feed.
    """
    data = []
    with input_path.open() as input_file:
        reader = csv.DictReader(input_file)
        for row in reader:
            expanded_rss = ExpandedRSS(**row)
            data.append(expanded_rss)
    return data


def path_maker(url: str, now: datetime.datetime=None, format: str="%Y%m%d") -> Path:
    """
    Builds a Path from today's date and the base name of the URL.

    The default format is "%Y%m%d" to transform the date to a YYYYmmdd string.
    An alternative can be ""%Y%W%w" to create a  YYYYWWw string,
    where WW is the week of the year and w is the day of the week.

    >>> from rss_status import path_maker
    >>> import datetime
    >>> now = datetime.datetime(2018, 9, 10)
    >>> str(path_maker("https://ecf.dcd.uscourts.gov/cgi-bin/rss_outside.pl", now))
    '20180910/rss_outside'

    :param url: An RSS-feed URL.
    :param now: Optional date/time object. Defaults to datetime.datetime.now().
    :return: A Path with the date string / base name from the URL.
    """
    url_details = urlparse(url)
    base_name = Path(url_details.path).stem
    if not now:
        now = datetime.datetime.now()
    today_str = now.strftime(format)
    return Path(today_str) / base_name


def find_yesterday(directory: Path, url: str, date_pattern: str='[0-9]*') -> Path:
    """
    We need to search for the most recent previous entry. While we can hope for
    dependably running this every day, that's a difficult thing to guarantee.

    It's much more reliable to look for the most recent date which
    contains files for a given channel. This means

    Example. Here's two dates. One date has one channel, the other has two channels.

    ::

        20180630/one_channel/daily.csv
        20180630/one_channel/new.csv
        20180630/one_channel/save.csv
        20180701/one_channel/daily.csv
        20180701/one_channel/new.csv
        20180701/one_channel/save.csv
        20180701/another_channel/daily.csv
        20180701/another_channel/new.csv
        20180701/another_channel/save.csv

    If there's nothing available, returns None.

    :param directory: The base directory to search
    :param url: The full URL from which we can get the base name
    :param date_pattern: Most of the time, the interesting filenames will begin with a digit
        If the file name pattern is changed, however, this can be used to match dates,
        and exclude non-date files that might be confusing.
    :return: A Path with the date string / base name from the URL or None.
    """
    url_details = urlparse(url)
    base_name = Path(url_details.path).stem
    candidates = list(directory.glob(f"{date_pattern}/{base_name}"))
    if candidates:
        return max(candidates)


def channel_processing(url: str, directory: Path=None, date: datetime.datetime=None):
    """
    The daily process for a given channel.

    Ideally there's a "yesterday" directory. Pragmatically, this may not exist.
    We use :func:`find_yesterday` to track down the most recent file and
    work with that. If there's no recent file, this is all new. Welcome.

    :param url: The URL for the channel
    :param directory: The working directory, default is the current working directory.
    :param date: The date to assign to the files, by default, it's datetime.datetime.now.
    """
    if directory is None:
        directory = Path.cwd()

    if date is None:
        date = datetime.datetime.now()

    yesterdays_path = find_yesterday(directory, url)
    todays_path = path_maker(url)

    todays_data = title_transform(xml_reader(url))
    if yesterdays_path:
        saved_data = csv_load(yesterdays_path / "save.csv")
    else:
        saved_data = []

    new_data = set(todays_data) - set(saved_data)
    all_data = set(todays_data) | set(saved_data)

    todays_path.mkdir(parents=True, exist_ok=True)
    csv_dump(todays_data, todays_path / "daily.csv")
    csv_dump(new_data, todays_path / "new.csv")
    csv_dump(all_data, todays_path / "save.csv")


def demo():
    """
    This is downloads, enriches, and saves the daily files to the current
    working directory.
    """
    target_path = Path.cwd()

    data1 = xml_reader("https://ecf.dcd.uscourts.gov/cgi-bin/rss_outside.pl")
    data1_decomposed = title_transform(data1)
    # pprint(data1_decomposed)
    csv_dump(data1_decomposed, target_path / "file1.csv")

    data2 = xml_reader("https://ecf.nyed.uscourts.gov/cgi-bin/readyDockets.pl")
    data2_decomposed = title_transform(data2)
    # pprint(data2_decomposed)
    csv_dump(data2_decomposed, target_path / "file2.csv")

    recovered = csv_load(target_path / "file2.csv")
    assert set(recovered) == set(data2_decomposed), "Weird, recovering the file was a problem."


if __name__ == "__main__":
    # demo()
    for channel_url in (
        "https://ecf.dcd.uscourts.gov/cgi-bin/rss_outside.pl",
        "https://ecf.nyed.uscourts.gov/cgi-bin/readyDockets.pl",
        # More channels here.
    ):
        channel_processing(channel_url)