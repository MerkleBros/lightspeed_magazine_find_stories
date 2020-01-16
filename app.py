"""Functions for requesting and processing html from Science Fiction magazines"""
import os
import time
import pickle
import requests
from bs4 import BeautifulSoup

# Functions for paginated list of issues
def request_all_paginated_list_pages(base_url: str) -> list:
    """Return html for each page of a paginated list as list of BeautifulSoup objects"""
    print(f"Requesting paginated list pages from {base_url}")

    status = 200
    list_page = 0
    pages = []

    while status != 404:
        list_page += 1
        list_page_url = f"{base_url}/{list_page}"

        print(f"Request list page {list_page}")

        request = requests.get(list_page_url)
        status = request.status_code

        print(f"Received list page {list_page} with status {status}")

        if status == 404:
            break

        soup = BeautifulSoup(request.content, 'html.parser')
        pages.append(soup)

        time.sleep(5)
    return pages

def get_all_issues_links(issues_pages: list):
    """Find all issue url strings in a list of issue html pages (BeautifulSoup objects)"""
    print(f"Finding all issue links")

    urls = []

    for index, page in enumerate(issues_pages):
        print(f"Finding issue links in page {index + 1}")

        post_wrapper_divs = page.body \
            .find("div", {"id": "wrapper"}) \
            .find("div", {"id": "main"}) \
            .find("div", {"id": "content"}) \
            .find("div", {"class": "content_box"}) \
            .find_all("div", {"class": "post_wrapper"})

        for div in post_wrapper_divs:
            url = div \
                .find("div", {"class": "post_content"}) \
                .find("h2", {"class": "posttitle"}) \
                .find("a")["href"]
            urls.append(url)

        print(f"Total issue links found so far: {len(urls)}")

    return urls

def request_and_find_and_save_issue_links():
    """Request, find, and save list of issue link url strings as a pickle"""
    print(f"Getting all issue list pages")

    base_url = "http://www.lightspeedmagazine.com/category/issues/page"
    pages = request_all_paginated_list_pages(base_url=base_url)
    issue_links = get_all_issues_links(issues_pages=pages)

    print(f"Dumping {len(issue_links)} links to pickle issue_links")

    with open('issue_links.p', 'wb') as file_pointer:
        pickle.dump(issue_links, file_pointer)

def load_from_pickle(url: str):
    """Return an object loaded from a local pickle file"""
    with open(url, 'rb') as file_pointer:
        return pickle.load(file_pointer)

# Functions for specific issue pages
def request_soup_page(url: str):
    """Request an html page and return a BeautifulSoup object for that page"""
    print(f"Requesting page {url}")

    request = requests.get(url)
    status = request.status_code

    print(f"Received page {url} with status {status}")
    if status == 404:
        return {}

    soup = BeautifulSoup(request.content, 'html.parser')
    return soup

def get_all_story_links_from_issue(issue: object):
    """Return a list of all story url strings in an issue"""
    print(f"Getting all story links from issue")

    post_wrapper_divs = issue.body \
        .find("div", {"id": "wrapper"}) \
        .find("div", {"id": "main"}) \
        .find("div", {"id": "content"}) \
        .find("div", {"class": "content_box"}) \
        .find_all("div", {"class": "post_wrapper"})

    print(f"Found {len(post_wrapper_divs)} post_wrapper divs")

    links = []
    for post in post_wrapper_divs:
        post_content = post.find("div", {"class": "post_content"})
        category_header = post_content.find("h3")
        title_header_link = post_content.find("h2", {"class": "posttitle"}).find("a")

        if not category_header or not title_header_link:
            continue

        link = title_header_link["href"]

        if (category_header.contents[0] == "Science Fiction" or \
            category_header.contents[0] == "Fantasy"):
            print(f"Added link {link}")
            links.append(link)

    print(f"Found {len(links)} story links from issue")
    return links

def request_and_find_and_save_story_links_from_issues(issue_links: list, pickle_url: str):
    """Request, find, and save a list of all story url strings in issues as a pickle"""
    print(f"Getting all story links from issues")

    story_links = []
    for issue_link in issue_links:

        if os.path.exists(pickle_url):
            story_links = load_from_pickle(pickle_url)
            print(f"Loaded pickle {pickle_url} with {len(story_links)} story links")

        issue_page = request_soup_page(url=issue_link)
        links = get_all_story_links_from_issue(issue=issue_page)
        story_links = story_links + links

        print(f"Found {len(story_links)} story links so far")
        print(f"Dumping {len(story_links)} links to pickle {pickle_url}")

        with open(pickle_url, 'wb') as file_pointer:
            pickle.dump(story_links, file_pointer)

        time.sleep(5)

def main():
    """
    Run functions to retrieve and process html from online science fiction magazines.

    Only need to run each once to save data to pickle files.

    Two pickle files are saved:
    issue_links.p is a list of url strings for all magazine issues
    story_links.p is a list of url strings for all stories in the magazine
    """

    request_and_find_and_save_issue_links()
    issue_links = load_from_pickle("issue_links.p")
    request_and_find_and_save_story_links_from_issues( \
        issue_links=issue_links, pickle_url="story_links.p")

if __name__ == '__main__':
    main()
