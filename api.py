import json
import re
from datetime import date, datetime
from pathlib import Path

import requests
from bs4 import BeautifulSoup as bs

today = datetime.today()
now = datetime.utcnow()

END_TIME = 18


def get_soup(url: str) -> bs:
    html = requests.get(url, timeout=10).text
    soup = bs(html, "lxml")

    with open("index.html", "w", encoding="UTF-8") as f:
        f.write(html)

    return soup


def yield_foods(food_list: dict):
    schema = []
    for _date, _list in food_list.items():
        if _date.weekday() < today.weekday():  # before
            schema.append((False, _date.strftime("%d %B %Y %A"), _list))
        elif _date.weekday() == today.weekday():  # today
            if 0 < now.hour < END_TIME:
                schema.append((True, _date.strftime("%d %B %Y %A"), _list))
            else:
                schema.append((False, _date.strftime("%d %B %Y %A"), _list))
        else:  # after
            schema.append((True, _date.strftime("%d %B %Y %A"), _list))

    for i in schema:
        yield i


def get_table(soup: bs):
    table = soup.find("table", {"class": "table table-bordered"})

    next = False
    strings = list(table.tbody.tr.td.stripped_strings)

    formatted_text = ""
    for i in strings[3:]:
        if i.isspace():
            continue

        if i == "PERSONEL":
            break

        if next:
            next = not next
            formatted_text += i + "\n"
            continue

        if not re.match(r"^([A-Za-zçğıöüÇĞİÖÜ]+.)+$", i):
            if re.match(r"^[\d]{1,2}.[\w]+.[\d]{4}.[\w]+.\([\w-]+\)", i):
                formatted_text += i + "\n"
                continue
            else:
                next = True
                formatted_text += i + " "
                continue

        formatted_text += "\t" + i + "\n"

    yemek_verileri = {}

    tarih = ""
    for i in formatted_text.split("\n"):
        if i.startswith("\t"):
            yemek_verileri[tarih].append(i.strip())
        else:
            if not i:
                continue
            tarih = i.split("(")[0].strip()
            yemek_verileri[tarih] = []

    with open(Path("./aylar.json").absolute(), "r", encoding="UTF-8") as f:
        month_ids: dict = json.load(f)

    for _date, _ in list(yemek_verileri.items()).copy():
        day, month, year, _ = _date.split()
        dt = date.fromisoformat("%s-%s-%s" % (year, month_ids.get(month), day))
        yemek_verileri[dt] = yemek_verileri.pop(_date)
    return yemek_verileri


def get_as_json():
    url = "https://sksd.kayseri.edu.tr/tr/i/1-2/yemek-listesi"

    soup = get_soup(url)
    food_list = get_table(soup)

    return [i for i in yield_foods(food_list)]
