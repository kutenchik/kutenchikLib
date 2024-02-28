import requests
from bs4 import BeautifulSoup

url = 'https://ru.wikipedia.org/wiki/%D0%A1%D0%BB%D1%83%D0%B6%D0%B5%D0%B1%D0%BD%D0%B0%D1%8F:%D0%A1%D0%BB%D1%83%D1%87%D0%B0%D0%B9%D0%BD%D0%B0%D1%8F_%D1%81%D1%82%D1%80%D0%B0%D0%BD%D0%B8%D1%86%D0%B0'

response = requests.get(url)
soup = BeautifulSoup(response.content, 'html.parser')

mw_content = soup.find('div', class_='mw-content-ltr mw-parser-output')
if mw_content:
    first_p = mw_content.find('p')
    if first_p:
        print(first_p.text)
