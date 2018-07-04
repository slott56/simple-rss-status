import requests
from xml.etree import ElementTree
from pprint import pprint
import csv


def parse_my_url(url):
    items = []
    response = requests.get(url)
    document = ElementTree.fromstring(response.content)
    for channel in document.iter('channel'):
        print(channel.find('title').text)
        print(channel.find('link').text)
        print(channel.find('description').text)
        print(channel.find('lastBuildDate').text)
        for item in channel.iter('item'):
            item_row = {
                'title': item.find('title').text,
                'link': item.find('link').text,
                'description': item.find('description').text,
                'pubDate': item.find('pubDate').text,
            }
            items.append(item_row)
    return items

def decompose_the_title(items):
    new_items = []
    for row in items:
        docket, _, parties_title = row['title'].partition(' ')
        _, _, real_docket = docket.partition(":")
        row['docket'] = real_docket
        row['parties_title'] = parties_title
        new_items.append(row)
    return new_items

def save_my_url(data, name):
    with open(name, 'w') as output_file:
        headings = ['title', 'docket', 'parties_title', 'link', 'description', 'pubDate']
        writer = csv.DictWriter(output_file, headings)
        writer.writeheader()
        for row in data:
            writer.writerow(row)

data1 = parse_my_url("https://ecf.dcd.uscourts.gov/cgi-bin/rss_outside.pl")
data1_decomposed = decompose_the_title(data1)
save_my_url(data1_decomposed, "file1.csv")

data2 = parse_my_url("https://ecf.nyed.uscourts.gov/cgi-bin/readyDockets.pl")
data2_decomposed = decompose_the_title(data2)
pprint(data2_decomposed)
save_my_url(data2_decomposed, "file2.csv")
