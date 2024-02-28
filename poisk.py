from bs4 import BeautifulSoup
import requests
import re
from selenium import webdriver
import time
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
import os
import transliterate
name=input()
URL=f'https://mangahub.ru/search?query={name}'
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
response=requests.get(URL,headers=Headers)
soup=BeautifulSoup(response.content,'html.parser')
items=soup.findAll('div',class_='comic-slide position-relative')
for item in items:
    title=item.find('a',class_='fw-medium').get_text(strip=True)
    href=f"https://mangahub.ru{item.find('a',class_='fw-medium').get('href')}"
    href=re.sub(r'/title/','/chapters/',href)
    print(title,href)
    try:
        os.mkdir(f'poisk/{transliterate.translit(title,reversed=True)}')
    except:
        pass
    href1=re.sub(r'/chapters/','/title/',href)
    response1=requests.get(href,Headers)
    soup1=BeautifulSoup(response1.content,'html.parser')
    items1=soup1.findAll('div',class_='detail-chapter rounded d-flex align-items-center py-2 px-3 position-relative') 
    # counter=0
    god=soup.find('div',class_='text-muted mt-1 fs-1').get_text(strip=True)
    response2=requests.get(href1,Headers)
    soup2=BeautifulSoup(response2.content,'html.parser')
    opisanie=soup2.find('text-expandable',class_='mt-4').find('div',class_='markdown-style text-expandable-content').find('p').get_text(strip=True)
    cover=soup2.find('img',class_='cover cover-detail').get('src')
    primer=''
    for item1 in items1:
        glava=item1.find('span',class_='text-truncate').get_text(strip=True)
        glava_url=f"https://mangahub.ru{item1.find('a',class_='d-inline-flex ms-2 fs-2 fw-medium text-reset min-w-0 flex-lg-grow-1').get('href')}"
        primer+=f'''<li><a href="{glava_url}">{glava}</a></li>\n'''
    else:
        try:
            with open(f'poisk/{transliterate.translit(title,reversed=True)}/{transliterate.translit(title,reversed=True)}glavi.html','w',encoding="utf-8") as file:
                file.write(f'''<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Document</title>
    <link rel="stylesheet" href="../../style.css">
</head>
<body bgcolor="#f7f7f7">
    <div style="display: inline-block;vertical-align: top;margin-left:200px;margin-top: 35px;">
        <img width="280px" height="392px" src="{cover}">
        <a class="glavi_s_pervoy" href="{glava_url}">
            <div class="glavi_s_pervoy">
                <b>Читать с 1 главы</b>
            </div>
        </a>
    </div>
    <div class="container-glavi" style="display: inline-block;">
        <div class="center">
            <h2>{title}</h2>
            <p>Год:{god}</p>
            <p>Описание:{opisanie}</p>
            <p>Главы:</p>
            <ul>
                {primer}
            </ul>
        </div>
    </div>
</body>
</html>''')
        except:
            pass   