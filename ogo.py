import psycopg2
import requests
from bs4 import BeautifulSoup
import re
import json
from collections import defaultdict
from FDATABASE import FDATABASE
conn=psycopg2.connect(
    dbname='site',
    user='postgres',
    password='kutenchik',
    host='localhost'
)
cursor=conn.cursor()
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
dbase=FDATABASE(conn)
# response=requests.get(url='https://mangalib.org/jojo-no-kimyou-na-bouken-part-7-steel-ball-run-solored/v24/c95?page=1',headers=Headers)
# soup=BeautifulSoup(response.content,'html.parser')
# chapter_url_match = re.search(r'window\.__info = ({.*?});', str(soup), re.DOTALL)
# if chapter_url_match:
#     info_data = json.loads(chapter_url_match.group(1))
#     chapter_url_part = info_data.get("img", {}).get("url")
#     image_server = info_data.get("servers", {}).get("main")
#     if chapter_url_part and image_server:
#         pages_match = re.search(r'window\.__pg = (\[.*?\]);', str(soup), re.DOTALL)
#         if pages_match:
#             pages_data = json.loads(pages_match.group(1))
#             image_links = [f"{image_server}{chapter_url_part}{page['u']}" for page in pages_data]
#             for link in image_links:
#                 print(link)

#ссылки на главы
# response=requests.get(url='https://mangalib.org/banana-fish?section=info',headers=Headers)
# soup=BeautifulSoup(response.content,'html.parser')
# script_tag = soup.find('script', string=lambda s: 'window.__DATA__' in s)
# if script_tag:
#     script_text = script_tag.string
#     match = re.search(r'window\.__DATA__ = ({.*?});', script_text)
#     if match:
#         data_json = match.group(1)
#         manga_data = json.loads(data_json)
#         slug_value = manga_data.get('manga', {}).get('slug')
# pattern = r'"list":\s*(\[.*?\])'
# matches = re.search(pattern, str(soup), re.DOTALL)
# if matches:
#     chapters_list = matches.group(1)
#     chapters = json.loads(chapters_list)
#     links = [f"/{slug_value}/v{chapter['chapter_volume']}/c{chapter['chapter_number']}" for chapter in chapters]
#     print(links)
    
    
    
    
# response=requests.get(url='https://mangalib.org/jojo-no-kimyou-na-bouken-jojorion?bid=8348&section=info',headers=Headers)
# soup=BeautifulSoup(response.content,'html.parser')
# all_items = soup.find_all('a', class_='media-info-list__item')
# for item in all_items:
#     title = item.find('div', class_='media-info-list__title')
#     value = item.find('div', class_='media-info-list__value')
#     if title and value and title.text.strip() == 'Год релиза':
#         year = value.text.strip()
#         break
# description=soup.find('div',class_='media-description__text').get_text(strip=True)
# cover=soup.find('div',class_='media-sidebar__cover paper').find('img').get('src')
# genre = [tag.get_text(strip=True) for tag in soup.find('div', class_='media-tags').find_all('a') if tag.get_text(strip=True)[0].islower()]
# genres = ';'.join(genre)
# print(description,year,cover,genres)
# ogoggoog
# hz=''
# with open('ogo.html','r',encoding='utf-8') as file:
#     hz=file.read()
# soup=BeautifulSoup(hz,'html.parser')
# script_tag = soup.find('script', string=lambda s: 'window.__DATA__' in s)
# if script_tag:
#     script_text = script_tag.string
#     match = re.search(r'window\.__DATA__ = ({.*?});', script_text)
#     if match:
#         data_json = match.group(1)
#         manga_data = json.loads(data_json)
#         slug_value = manga_data.get('manga', {}).get('slug')
# pattern = r'"list":\s*(\[.*?\])'
# matches = re.search(pattern, str(soup), re.DOTALL)
# if matches:
#     chapters_list = matches.group(1)
#     chapters = json.loads(chapters_list)
#     branch_id_count = defaultdict(int)
#     for chapter in chapters:
#         branch_id_count[chapter['branch_id']] += 1
#     max_count = max(branch_id_count.values())
#     result = [
#         chapter for chapter in chapters if branch_id_count[chapter['branch_id']] == max_count
#     ]
#     links = [f"/{slug_value}/v{chapter['chapter_volume']}/c{chapter['chapter_number']}" for chapter in result]
#     links = [f"/{slug_value}/v{chapter['chapter_volume']}/c{chapter['chapter_number']}" for chapter in chapters]
#     print(links)
# response=requests.get(url='https://mangavost.org/vod/3473')
# soup=BeautifulSoup(response.text,'html.parser')
# target_script = soup.find('script', text=lambda text: text and 'var player =' in text)
# divs_with_styles = soup.find_all('div', style='width:100%;height:100%')
# for div in divs_with_styles:
#     div['style'] = 'width:90%;height:100px;margin-left: auto;margin-right: auto;'
# div_elements = soup.find_all('div')
# nu_tip_text=''
# for i in div_elements:
#     nu_tip_text+=str(i)
# nu_tip_text+=str(target_script)
# print(nu_tip_text)