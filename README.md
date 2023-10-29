# Crawl-PTT-Project
Search for PTT posts on a specific date, and then save the data into MySQL

## A brief introduction to program content
### crawl_page_url.py
- Use Selenium and Chromedriver to crawl pages
- Loop through each page of each category board
- Encounter an abnormal situation, store it in a csv file
- Fetch the URLs that match the date and store them in the csv file and the redis URL list
- When all URLs are crawled, use the socket to start listening to other machines.

### crawl_page_content.py
- Request the url from master
- Crawl page data and parse it
- Save to MySQL DB


## User Agent
This is currently hard code, but it will be adjusted to use python's fake_useragent package in the future.</br>
https://pypi.org/project/fake-useragent/