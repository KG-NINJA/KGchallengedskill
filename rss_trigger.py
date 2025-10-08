#!/usr/bin/env python3
import feedparser
import random

RSS_FEEDS = [
    "https://www.nasa.gov/rss/dyn/breaking_news.rss",
    "https://www.sciencedaily.com/rss/top/science.xml"
]

def fetch_latest(feed_url):
    feed = feedparser.parse(feed_url)
    if not feed.entries:
        return None
    latest = feed.entries[0]
    return f"{latest.title} - {latest.link}"

# Pick one feed randomly to vary the signal
feed_url = random.choice(RSS_FEEDS)
msg = fetch_latest(feed_url)

if msg:
    print(msg)
else:
    print("No news")
