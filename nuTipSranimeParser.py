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
cursor=conn.cursor()
dbase=FDATABASE(conn)
def add_seriya(title_id,nomer_serii,seriya,seriya_url):
    response=requests.get(url=seriya_url)
    soup=BeautifulSoup(response.text,'html.parser')
    target_script = soup.find('script', text=lambda text: text and 'var player =' in text)
    divs_with_styles = soup.find_all('div', style='width:100%;height:100%')
    for div in divs_with_styles:
        div['style'] = 'width:90%;height:100px;margin-left: auto;margin-right: auto;'
    div_elements = soup.find_all('div')
    nu_tip_text=''
    for i in div_elements:
        nu_tip_text+=str(i)
    nu_tip_text+=str(target_script)
    cursor.execute('INSERT INTO ANIME_SERII(TITLE_ID,nomer_glavi,glava,html_code) VALUES(%s,%s,%s,%s)',(title_id,nomer_serii,seriya,nu_tip_text))
    conn.commit()
def add_anime(href,title_na_angl,title_na_rus):
    response=requests.get(url=href,headers=Headers)
    soup=BeautifulSoup(response.content,'html.parser')
    hz = soup.find('div', class_='tabs-block__content video-inside')
    pervaya_seriya=hz.find('iframe').get('src')
    ostalnie_serii=[pervaya_seriya]
    pon=hz.find('div',class_='kontaiher').find_all('a',class_='BatcoH BatcoH-5 nav_video_links')
    serii=['1 серия']
    for i in pon:
        ostalnie_serii.append(i.get('data-vlnk'))
        serii.append(i.get_text(strip=True))
    with open('ogo.html','w',encoding='utf-8') as file:
        file.write(str(soup))
    all_items = soup.find_all('ul', class_='ulpad')
    match = re.search(r'<span>Год:</span>\s*<a[^>]*>(\d{4})</a>', str(all_items))
    year=match.group(1)
    description=soup.find('div',class_='pmovie__text full-text clearfix').get_text()
    cover=f"https://amedia.online{soup.find('div',class_='pmovie__img img-fit-cover img-mask').find('img').get('src')}"
    genre = [tag.get_text(strip=True) for tag in soup.find('div', class_='animli').find_all('a') if tag.get_text(strip=True)[0].islower()]
    genres = ';'.join(genre)
    dbase.add_title(title_na_rus,title_na_angl,description,year,cover,genres,'аниме')
    cursor.execute(f"select title_id from titles where name_on_english='{title_na_angl}'")
    title_id=cursor.fetchone()[0]
    nomer_serii=len(ostalnie_serii)
    for i in ostalnie_serii:
        try:
            nomer_serii-=1
            add_seriya(title_id,nomer_serii+1,serii[nomer_serii],i)
        except:
            pass
add_anime('https://amedia.online/231-neveroyatnye-priklyucheniya-dzhodzho-5.html','jjba_pt5_tv','Невероятные Приключения ДжоДжо — Часть 5: Золотой ветер TV')