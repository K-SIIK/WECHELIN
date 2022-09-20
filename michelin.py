import requests
from bs4 import BeautifulSoup

from pymongo import MongoClient

client = MongoClient('mongodb+srv://test:sparta@cluster0.wzrslas.mongodb.net/Cluster0?retryWrites=true&w=majority')
db = client.dbsparta

headers = {
  'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)AppleWebKit/537.36 (KHTML, like Gecko) Chrome/73.0.3683.86 Safari/537.36'}
data = requests.get(
  'https://guide.michelin.com/kr/ko/selection/south-korea/restaurants/3-stars-michelin/2-stars-michelin/1-star-michelin',
  headers=headers)

soup = BeautifulSoup(data.text, 'html.parser')

trs = soup.select(
  'body > main > section.section-main.search-results.search-listing-result > div.row > div > div.row.restaurant__list-row.js-toggle-result.js-geolocation.js-restaurant__list_items > div')

for tr in trs:
  image = tr.select_one('div > div.card__menu-image > a > noscript > img')['src']
  star = tr.select_one('div > div.card__menu-content.js-match-height-content > div > i').text
  name = tr.select_one('div > div.card__menu-content.js-match-height-content > h3 > a').text.strip()
  type = tr.select_one('div > div.card__menu-footer.d-flex > div.card__menu-footer--price.pl-text').text.strip()
  # 1스타 - 'm', 2스타 - 'n', 3스타 - 'o'
  star = ord(star) - ord('l')
  print(star)

  doc = {
    'image': image,
    'star': star,
    'name': name,
    'type': type
  }

  db.michelin.insert_one(doc)