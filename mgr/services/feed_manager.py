import feedparser
from dataclasses import dataclass
from PyQt6.QtCore import Qt, QDateTime
import xml.etree.ElementTree as ET

@dataclass
class PostData:
    id: int = -1
    title: str = "Untitled Post"
    url: str = ""
    description: str = ""
    pubdate: QDateTime = QDateTime.currentDateTime()

class FeedData:
    def __init__(self, title: str = "Untitled Feed", url: str = "", description: str = ""):
        self.title = title
        self.url = url
        self.description = description
        self.posts = []

class FeedManager:
    def __init__(self):
        self.feed = None
    
    def import_feed(self, feed_data):
        feed = feedparser.parse(feed_data)

        if feed.bozo:
            raise Exception(f"Failed to parse feed: {feed.bozo_exception}")

        self.feed = FeedData(title=feed.feed.get("title", "Untitled Feed"), url=feed.feed.get("link", ""), description=feed.feed.get("description", ""))

        for index, entry in enumerate(feed.entries):
            id = index
            title = entry.get("title", "No Title")
            url = entry.get("link", "")
            description = entry.get("description", "")
            pubdate_str = entry.get("published", "")
            pubdate = pubdate_str.replace("GMT", "+0000")

            post_data = PostData(id=id, title=title, url=url, description=description, pubdate=pubdate)
            self.feed.posts.append(post_data)
        
    def add_new_post(self):
        if self.feed is not None:
            new_post = PostData(id=len(self.feed.posts), 
                                title="New Post", description="", 
                                pubdate=QDateTime.currentDateTime().toString(Qt.DateFormat.RFC2822Date))
            self.feed.posts.append(new_post)
            self.update_indexes()
    
    def delete_post(self, id):
        self.feed.posts.pop(id)
        self.update_indexes()
        
    def update_indexes(self):
        for index, post in enumerate(self.feed.posts):
            post.id = index
    
    def export_feed(self, file_path):
        if self.feed is None:
            raise Exception("No feed to export")

        root = ET.Element("rss", version="2.0")
        channel = ET.SubElement(root, "channel")

        ET.SubElement(channel, "title").text = self.feed.title
        ET.SubElement(channel, "link").text = self.feed.url
        ET.SubElement(channel, "description").text = self.feed.description

        for post in self.feed.posts:
            item = ET.SubElement(channel, "item")
            ET.SubElement(item, "title").text = post.title
            ET.SubElement(item, "link").text = post.url
            ET.SubElement(item, "description").text = post.description
            ET.SubElement(item, "pubDate").text = post.pubdate

        ET.indent(root, space="  ")
                
        tree = ET.ElementTree(root)
        tree.write(file_path, encoding="utf-8", xml_declaration=True)