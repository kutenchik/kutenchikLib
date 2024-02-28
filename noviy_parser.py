import requests
from bs4 import BeautifulSoup,Tag
import psycopg2
from FDATABASE import FDATABASE
from selenium import webdriver
import time
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
import os
import json
import re
from collections import defaultdict
conn=psycopg2.connect(
    dbname='site',
    user='postgres',
    password='kutenchik',
    host='localhost'
)
start_time = time.time()
cursor=conn.cursor()
dbase=FDATABASE(conn)
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
def otdelnaya_glava(title_id,nomer_glavi,glava,glava_url):
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
def glavi(URL,title,title_na_rus):
    driver = webdriver.Chrome()
    driver.get(URL)
    time.sleep(1)
    elem = driver.find_element(By.TAG_NAME,"Body")
    while True:
        soup2=BeautifulSoup(driver.page_source)
        el=soup2.find('li',class_='relative flex w-full')
        if not el:
            break
        elem.send_keys(Keys.PAGE_DOWN)
        time.sleep(0.2)
        soup2=BeautifulSoup(driver.page_source)
        el=soup2.find('li',class_='relative flex w-full')
    html = driver.page_source
    soup = BeautifulSoup(html)
    items=soup.findAll('li',{"class":"flex justify-between card variant-soft-surface mb-3 p-2 md:px-3"})
    nomer_glavi=len(items)+1
    o_title=URL.replace("?tab=chapters", "")
    response=requests.get(o_title,headers=Headers)
    soup1=BeautifulSoup(response.content,'html.parser')
    genres=''
    for i in soup1.find_all('a',class_='badge variant-soft-tertiary mb-1 mr-1'):
            genres+=f'{i.get_text(strip=True)};'
    genres=genres[:-1]
    god=soup1.find('a',class_='badge variant-soft-tertiary').get_text(strip=True)
    opisanie=soup1.find('div',class_='manga-description overflow-hidden').get_text(strip=True)
    cover=soup1.find('img',class_='rounded-container-token preload w-full h-auto max-w-3xs md:max-w-xs mx-auto').get('src')
    dbase.add_title(title_na_rus,title,opisanie,god,cover,genres,'манга')
    for item in items:
        glava=item.find('span', class_='chapter-title').text.strip()
        try:
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
        glava_url=item.find('a').get('href')
        try:
            nomer_glavi-=1
            cursor.execute(f"select title_id from titles where name_on_english='{title}'")
            title_id=cursor.fetchone()[0]
            otdelnaya_glava(title_id,nomer_glavi,glava.strip(),glava_url)
        except:
            pass
def mangalib_otdelnaya_glava(title_id,nomer_glavi,glava,glava_url):
    response=requests.get(glava_url,headers=Headers)
    soup=BeautifulSoup(response.content,'html.parser')
    images=''
    chapter_url_match = re.search(r'window\.__info = ({.*?});', str(soup), re.DOTALL)
    if chapter_url_match:
        info_data = json.loads(chapter_url_match.group(1))
        chapter_url_part = info_data.get("img", {}).get("url")
        image_server = info_data.get("servers", {}).get("main")
        if chapter_url_part and image_server:
            pages_match = re.search(r'window\.__pg = (\[.*?\]);', str(soup), re.DOTALL)
            if pages_match:
                pages_data = json.loads(pages_match.group(1))
                image_links = [f"{image_server}{chapter_url_part}{page['u']}" for page in pages_data]
                for link in image_links:
                    images+=f"{link};"
    images=images[:-1]
    if images: 
        dbase=FDATABASE(conn)
        dbase.add_glava(title_id,nomer_glavi,glava,images)
def mangalibGlavi(href,title_na_angl,title_na_rus):
    response=requests.get(url=href,headers=Headers)
    soup=BeautifulSoup(response.content,'html.parser')
    all_items = soup.find_all('a', class_='media-info-list__item')
    for item in all_items:
        title = item.find('div', class_='media-info-list__title')
        value = item.find('div', class_='media-info-list__value')
        if title and value and title.text.strip() == 'Год релиза':
            year = value.text.strip()
            break
    description=soup.find('div',class_='media-description__text').get_text(strip=True)
    cover=soup.find('div',class_='media-sidebar__cover paper').find('img').get('src')
    genre = [tag.get_text(strip=True) for tag in soup.find('div', class_='media-tags').find_all('a') if tag.get_text(strip=True)[0].islower()]
    genres = ';'.join(genre)
    dbase.add_title(title_na_rus,title_na_angl,description,year,cover,genres,'манга')
    cursor.execute(f"select title_id from titles where name_on_english='{title_na_angl}'")
    title_id=cursor.fetchone()[0]
    script_tag = soup.find('script', string=lambda s: 'window.__DATA__' in s)
    if script_tag:
        script_text = script_tag.string
        match = re.search(r'window\.__DATA__ = ({.*?});', script_text)
        if match:
            data_json = match.group(1)
            manga_data = json.loads(data_json)
            slug_value = manga_data.get('manga', {}).get('slug')
    chapters_list = json.dumps(manga_data.get("chapters", {}).get("list", []))
    chapters = json.loads(chapters_list)
    chapters = json.loads(chapters_list)
    branch_id_count = defaultdict(int)
    for chapter in chapters:
        branch_id_count[chapter['branch_id']] += 1
    max_count = max(branch_id_count.values())
    result = [
        chapter for chapter in chapters if branch_id_count[chapter['branch_id']] == max_count
    ]
    links = [f"https://mangalib.org/{slug_value}/v{chapter['chapter_volume']}/c{chapter['chapter_number']}" for chapter in result]
    nomer_glavi=len(links)+1
    glavi = [
            f"Том {chapter['chapter_volume']} Глава {chapter['chapter_number']} {chapter['chapter_name']}" 
            if chapter['chapter_name'] 
            else f"Том {chapter['chapter_volume']} Глава {chapter['chapter_number']}"
            for chapter in result
        ]
    for l in links:
        try:
            nomer_glavi-=1
            mangalib_otdelnaya_glava(title_id,nomer_glavi,glavi[len(links)-nomer_glavi],l)
        except:
            pass
def ranobeOtdelnayaGlava(title_id,nomer_glavi,glava,glava_url):
    response=requests.get(url=glava_url,headers=Headers)
    soup=BeautifulSoup(response.content,'html.parser')
    content_glavi=[]
    items=soup.find('div',{"class":"reader-container container container_center"})
    items1 = items.contents
    for item in items1:
        if isinstance(item, Tag):
            if item.name == 'p':
                img_tag = item.find('img')
                if img_tag:
                    image_url = f"https://ranobelib.me{img_tag['src']}"
                    content_glavi.append(image_url)
                else:
                    text_content = item.get_text(strip=True)
                    content_glavi.append(text_content)
            elif item.name == 'img':
                image_url = f"https://ranobelib.me{item['src']}"
                content_glavi.append(image_url)
            elif item.name=='div':
                image_url = f"{item.find('img')['data-src']}"
                content_glavi.append(image_url)
            else:
                content_glavi.append(item.get_text(strip=True))
        else:
            text_content = item.strip()
            content_glavi.append(text_content)
    dbase.add_ranobe_glava(title_id,nomer_glavi,glava,content_glavi)
def ranobeGlavi(href,title_na_angl,title_na_rus):
    response=requests.get(url=href,headers=Headers)
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
    dbase.add_title(title_na_rus,title_na_angl,description,year,cover,genres,'ранобе')
    cursor.execute(f"select title_id from titles where name_on_english='{title_na_angl}'")
    title_id=cursor.fetchone()[0]
    chapters_list = json.dumps(manga_data.get("chapters", {}).get("list", []))
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
            ranobeOtdelnayaGlava(title_id,nomer_glavi,glavi[len(links)-nomer_glavi],l)
        except:
            pass
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
    dbase.add_seriya(title_id,nomer_serii,seriya,nu_tip_text)
def add_anime(href,title_na_angl,title_na_rus):
    response=requests.get(url=href,headers=Headers)
    soup=BeautifulSoup(response.content,'html.parser')
    hz = soup.find('div', class_='tabs-block__content video-inside')
    pervaya_seriya=hz.find('iframe').get('src')
    ostalnie_serii=[pervaya_seriya]
    pon=hz.find('div',class_='kontaiher').find_all('a',class_='BatcoH BatcoH-5 nav_video_links')
    serii=[hz.find('a',class_='BatcoH BatcoH-5 sel-active nav_video_links').get_text(strip=True)]
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
allTitles=dbase.getAllTitles()
titles_from_bd=[]
for i in allTitles:
    titles_from_bd.append(i[2])
lines=[] 
with open('titli.txt',encoding='utf-8') as fp:
    lines = fp.readlines()
for line in lines:
    try:
        title=line.split(';')[0]
        href=line.split(';')[1]
        title_na_rus=line.split(';')[2]
        if title not in titles_from_bd:
            if 'mangapoisk' in href:
                glavi(href,title,title_na_rus)
            elif 'mangalib' in href:
                mangalibGlavi(href,title,title_na_rus)
            elif 'ranobelib' in href:
                ranobeGlavi(href,title,title_na_rus)
            elif 'amedia' in href:
                add_anime(href,title,title_na_rus)
    except Exception as e:
        print(e)