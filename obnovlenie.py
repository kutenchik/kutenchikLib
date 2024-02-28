import requests
from bs4 import BeautifulSoup
import psycopg2
from FDATABASE import FDATABASE
import re
conn=psycopg2.connect(
    dbname='site',
    user='postgres',
    password='kutenchik',
    host='localhost'
)
cursor=conn.cursor()
def stranitsya_glavi(title_id,glava,glava_url,nomer_glavi):
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
    response=requests.get(glava_url,headers=Headers)
    soup=BeautifulSoup(response.content,'html.parser')
    images=''
    items=soup.findAll('img',{"class":"page-image preload mx-auto"})
    for i in items:
        images+=f"{i.get('src')};"
    else:
        images=images[:-1]
    if images:
        dbase=FDATABASE(conn)
        dbase.add_glava(title_id,nomer_glavi,glava,images)
def hz(title,url):
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
    response=requests.get(url,headers=Headers)
    soup=BeautifulSoup(response.content,'html.parser')
    items=soup.findAll('li',{"class":"flex justify-between card variant-soft-surface mb-3 p-2 md:px-3"})
    cursor.execute("SELECT GLAVA FROM GLAVA INNER JOIN TITLES USING(TITLE_ID) WHERE NAME_ON_ENGLISH=%s ORDER BY NOMER_GLAVI DESC",(title,))
    glavi=cursor.fetchall()
    cursor.execute("SELECT title_id FROM GLAVA INNER JOIN TITLES USING(TITLE_ID) WHERE NAME_ON_ENGLISH=%s",(title,))
    title_id=cursor.fetchone()[0]
    norm_glavi=[item[0].strip() for item in glavi]
    counter=soup.find('span',class_='text-xs pl-1').get_text(strip=True)
    nums = re.findall(r'\d+', counter)
    nums = [int(i) for i in nums]
    counter=nums[0]
    for item in items:
        glava=item.find('span', class_='chapter-title').text.strip()
        try:
            if not item.find('a').contents[-1].strip():
                try:
                    glava_parts = []
                    for span in item.find('a', class_='italic text-sm false'):
                        text = span.text.strip()
                        if text:
                            glava_parts.append(text)
                    glava = ' '.join(glava_parts)
                except:
                    pass
            else:
                glava+=f" {item.find('a').contents[-1].strip()}"
                    
        except:
            try:
                glava_parts = []
                for span in item.find('a', class_='italic text-sm false'):
                    text = span.text.strip()
                    if text:
                        glava_parts.append(text)
                glava = ' '.join(glava_parts)
            except:
                pass
        if glava.strip() not in norm_glavi:
            glava_url=f"https://mangapoisk.me{item.find('a').get('href')}"
            stranitsya_glavi(title_id,glava,glava_url,counter)
        counter-=1
lines=[] 
with open('titli.txt',encoding='utf-8') as fp:
    lines = fp.readlines()
for line in lines:
    title=line.split(';')[0]
    href=line.split(';')[1]
    title_na_rus=line.split(';')[2]
    hz(title,href)
# Headers={
#                 'User-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) '
#                 'AppleWebKit/537.36 (KHTML, like Gecko) '
#                 'Chrome/85.0.4183.121 Safari/537.36',
#                 'Accept-Language': 'en',
#                 'accept': '*/*',
#                 'origin': 'https://best.aliexpress.ru',
#                 'sec-fetch-site': 'cross-site',
#                 'sec-fetch-mode': 'cors',
#                 'sec-fetch-dest': 'empty',
#                 'referer': 'https://best.aliexpress.ru/',
#                 'accept-language': 'ru-RU,ru;q=0.9,en-US;q=0.8,en;q=0.7'
#                 }
# response=requests.get(url='https://mangapoisk.me/manga/sorcery-fight-abs38J0/chapter/17-152',headers=Headers)
# soup=BeautifulSoup(response.content,'html.parser')
# items=soup.findAll('img',{"class":"page-image preload mx-auto"})
# print(items)
# URL='https://mangapoisk.me/manga/pocket-monster-special'
# Headers={
#         'User-Agent':'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/117.0.0.0 Safari/537.36 Edg/117.0.2045.43'
#     }
# response=requests.get(URL,headers=Headers)
# soup=BeautifulSoup(response.content,'html.parser')
# genres=''
# for i in soup.find_all('a',class_='badge variant-soft-tertiary mb-1 mr-1'):
#         genres+=f'{i.get_text(strip=True)};'
# genres=genres[:-1]
# god=soup.find('a',class_='badge variant-soft-tertiary').get_text(strip=True)
# opisanie=soup.find('div',class_='manga-description overflow-hidden').get_text(strip=True)
# cover=soup.find('img',class_='rounded-container-token preload w-full h-auto max-w-3xs md:max-w-xs mx-auto').get('src')
# print(cover,genres,god,opisanie)