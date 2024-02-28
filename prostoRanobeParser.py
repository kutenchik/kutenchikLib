from bs4 import BeautifulSoup,Tag
import re
import json
import requests
from collections import defaultdict
import psycopg2
from FDATABASE import FDATABASE
Headers={
                'User-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) '
                'AppleWebKit/537.36 (KHTML, like Gecko) '
                'Chrome/85.0.4183.121 Safari/537.36',
                'Accept-Language': 'en',
                'accept': '*/*',
                'origin': 'https://best.aliexpress.ru',
                'sec-fetch-site': 'cross-site',
                'sec-fetch-mode': 'cors',
                'sec-fetch-dest': 'empty',
                'referer': 'https://best.aliexpress.ru/',
                'accept-language': 'ru-RU,ru;q=0.9,en-US;q=0.8,en;q=0.7'
                }
conn=psycopg2.connect(
    dbname='site',
    user='postgres',
    password='kutenchik',
    host='localhost'
)
dbase=FDATABASE(conn)
def nu_tip_glava(nomer_glavi,glava,href):
    response=requests.get(url=href,headers=Headers)
    soup=BeautifulSoup(response.content,'html.parser')
    content_glavi=[]
    items=soup.find('div',{"class":"reader-container container container_center"})
    items1 = items.contents
    image_urls = []
    # for div in items.find_all('div', class_='article-image'):
    #     img_tag = div.find('img')
    #     if img_tag:
    #         image_url = img_tag['data-src'] if img_tag.get('data-src') else img_tag['src']
    #         image_urls.append(image_url)
    for item in items1:
        if isinstance(item, Tag):
            if item.name == 'p':
                img_tag = item.find('img')
                if img_tag:
                    image_url = f"https://ranobelib.me{img_tag['src']}"
                    content_glavi.append(image_url)
                    print(image_url)
                else:
                    text_content = item.get_text(strip=True)
                    content_glavi.append(text_content)
            elif item.name == 'img':
                image_url = f"https://ranobelib.me{item['src']}"
                content_glavi.append(image_url)
                print(image_url)
            elif item.name=='div':
                image_url = f"{item.find('img')['data-src']}"
                content_glavi.append(image_url)
                print(image_url)
            else:
                content_glavi.append(item.get_text(strip=True))
        else:
            text_content = item.strip()
            content_glavi.append(text_content)
    # conn.cursor().execute('INSERT INTO RANOBE_GLAVI(TITLE_ID,nomer_glavi,glava,content_glavi) VALUES(%s,%s,%s,%s)',(149,nomer_glavi,glava,content_glavi))
    # conn.commit()
response=requests.get(url='https://ranobelib.me/jorge-joestar?section=info',headers=Headers)
soup=BeautifulSoup(response.content,'html.parser')
script_tags = soup.find_all('script')
data_script_tag = None
for script_tag in script_tags:
    if script_tag.string and 'window.__DATA__' in script_tag.string:
        data_script_tag = script_tag
        break

if data_script_tag:
    script_text = data_script_tag.string
    match = re.search(r'window\.__DATA__ = ({.*?});', script_text)
    if match:
        data_json = match.group(1)
        manga_data = json.loads(data_json)
        slug_value = manga_data.get('manga', {}).get('slug')
pattern = r'"list":\s*(\[.*?\])'
matches = re.search(pattern, str(soup), re.DOTALL)
description=soup.find('div',class_='media-description__text').get_text(strip=True)
all_items = soup.find_all('a', class_='media-info-list__item')
for item in all_items:
    title = item.find('div', class_='media-info-list__title')
    value = item.find('div', class_='media-info-list__value')
    if title and value and title.text.strip() == 'Год релиза':
        year = value.text.strip()
        break   
cover=soup.find('div',class_='media-sidebar__cover paper').find('img').get('src')
genre = [tag.get_text(strip=True) for tag in soup.find('div', class_='media-tags').find_all('a') if tag.get_text(strip=True)[0].islower()]
genres = ';'.join(genre) 
# dbase.add_title('Реинкарнация Безработного WN','jobless_reincarnation',description,year,cover,genres)
if matches:
    chapters_list = matches.group(1)
    chapters = json.loads(chapters_list)
    branch_id_count = defaultdict(int)
    for chapter in chapters:
        branch_id_count[chapter['branch_id']] += 1
    max_count = max(branch_id_count.values())
    result = [
        chapter for chapter in chapters if branch_id_count[chapter['branch_id']] == max_count
    ]
    glavi = [
            f"Том {chapter['chapter_volume']} Глава {chapter['chapter_number']} {chapter['chapter_name']}" 
            if chapter['chapter_name'] 
            else f"Том {chapter['chapter_volume']} Глава {chapter['chapter_number']}"
            for chapter in result
        ]
    links = [f"https://ranobelib.me/{slug_value}/v{chapter['chapter_volume']}/c{chapter['chapter_number']}" for chapter in result]
    nomer_glavi=len(links)+1
    for l in links:
        try:
            nomer_glavi-=1
            nu_tip_glava(nomer_glavi,glavi[len(links)-nomer_glavi],l)
        except:
            pass







#Получить главы
# response=requests.get(url='https://ranobelib.me/mushoku-tensei?section=info',headers=Headers)
# soup=BeautifulSoup(response.content,'html.parser')
# pattern = r'"list":\s*(\[.*?\])'
# matches = re.search(pattern, str(soup), re.DOTALL)

# if matches:
#     chapters_list = matches.group(1)
#     chapters = json.loads(chapters_list)
#     links = [f"/mushoku-tensei/v{chapter['chapter_volume']}/c{chapter['chapter_number']}" for chapter in chapters]
#     print(links)
#ogoggoog