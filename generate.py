import pytz

from datetime import datetime, timedelta

from icalendar import Calendar, Event

from selenium import webdriver
from selenium.webdriver.common.by import By

with open("links.txt", "r") as f:
    urls = [u.strip() for u in f.readlines()]
    urls = [u for u in urls if u]

driver = webdriver.Chrome()

class Concert:
    def __init__(self, what, when, where, details):
        self.what = what
        self.when = when
        self.where = where
        self.details = details

def parse_page(url):
    driver.get(url)

    title = driver.find_element(By.CSS_SELECTOR, ".ev-act-summary__title").text
    start_time_and_date_and_location_str = driver.find_element(By.CSS_SELECTOR, ".ev-act-summary__performance-information").text

    parts = start_time_and_date_and_location_str.split(" ")
    start_time_and_date_str = " ".join(parts[0:5])
    location_str = " ".join(parts[5:])

    local_date_and_time = pytz.timezone("Europe/London").localize(datetime.strptime(start_time_and_date_str, "%H:%M %a %d %b %Y"))
    utc_date_and_time = local_date_and_time.astimezone(pytz.utc)

    piece_elements = driver.find_elements(By.CSS_SELECTOR, ".ev-act-schedule__performance-composer-segments-list > li")

    details = "\n".join([url] + [p.text for p in piece_elements])

    return Concert(title, utc_date_and_time, location_str, details)

cal = Calendar()

for index, url in enumerate(urls):
    try:
        concert = parse_page(url)
        if index == 0:
            cal.add("NAME", f"Proms {concert.when.year}")
        event = Event()
        event.add("DTSTART", concert.when)
        event.add("DTEND", concert.when + timedelta(hours=2))
        event.add("SUMMARY", f"?{concert.what}?")
        event.add("DESCRIPTION", concert.details)
        event.add("LOCATION", concert.where)
        cal.add_component(event)
    except Exception as e:
        print(f"Error handling URL {url}: {e}")

print(cal.to_ical().decode("utf-8"))

driver.quit()
