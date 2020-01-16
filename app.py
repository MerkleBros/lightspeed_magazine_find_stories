from bs4 import BeautifulSoup
import requests

issues_list_page = 1
URL = f"http://www.lightspeedmagazine.com/category/issues/page/{issues_list_page}"
page = requests.get(URL)
soup = BeautifulSoup(page.content, 'html.parser')
print(soup.prettify())
content_boxes = soup.body.find("div", {"id": "wrapper"}).find("div", {"id": "main"}).find("div", {"id": "content"}).find_all("div", {"class": "content_box"})
print("content_boxes")
print(content_boxes)
