from bs4 import BeautifulSoup
import requests
import re
from selenium import webdriver
import time
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
import os
import transliterate
from FDATABASE import FDATABASE
import psycopg2
last_glava=0
def save():
    with open('titli.txt','a', encoding="utf-8") as file:
        file.write(f"{comp['title']};{comp['image']};{comp['href']}\n")
def connect_db():
    conn=psycopg2.connect(
    dbname='site',
    user='postgres',
    password='kutenchik',
    host='localhost'
)
    return conn
def create_db():
    db=connect_db()
    with open('sql.sql',mode='r') as file:
        db.cursor().execute(file.read())
    db.commit()
    db.close()

def get_db():
    if not hasattr(g,'link_db'):
        g.link_db=connect_db()
    return g.link_db
db=connect_db()
cursor=db.cursor()
    
def parse():
    URL='https://mangalib.me/manga-list?types[]=1'
    Headers={
        'User-Agent':'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/117.0.0.0 Safari/537.36 Edg/117.0.2045.43'
    }
    response=requests.get(URL,headers=Headers)
    soup=BeautifulSoup(response.content,'html.parser')
    items=soup.findAll('div',class_='media-card-wrap')
    comps=[]
    i=0
    for item in items:
        comps.append({
            'title':item.find('h3').get_text(strip=True),
            'image':item.find('a').get('data-src'),
            'href':item.find('a').get('href')
        })
    global comp
    for comp in comps:
        save()
    lines=[]                
    with open('titli.txt',encoding='utf-8') as fp:
        lines = fp.readlines()
    for line in lines:
        href=line.split(';')[2]
        glavi(href)
def glavi(URL,title,title_na_rus):
    Headers={
        'User-Agent':'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/117.0.0.0 Safari/537.36 Edg/117.0.2045.43'
    }
    driver = webdriver.Chrome()

    driver.get(URL)
    time.sleep(1)
    elem = driver.find_element(By.TAG_NAME,"Body")
    soup2=BeautifulSoup(driver.page_source)
    for i in soup2.find_all('li',{"class":"flex justify-between card variant-soft-surface mb-3 p-2 md:px-3"}):
        try:
            lan=int(i.find('span',{'class':'chapter-title'}).get_text(strip=True).split('Глава')[1])
            break
        except:
            pass
    no_of_pagedowns = round(int(lan)/4)

    while no_of_pagedowns:
        elem.send_keys(Keys.PAGE_DOWN)
        time.sleep(0.2)
        no_of_pagedowns-=1
        
    html = driver.page_source
    # try:
    #     os.mkdir(title)
    # except:
    #     pass
    soup = BeautifulSoup(html)
    comps=[]
    items=soup.findAll('li',{"class":"flex justify-between card variant-soft-surface mb-3 p-2 md:px-3"})
    primer=''
    cover=soup.find('button',{"class":"w-full"}).find('img').get('src')
    o_title=href.replace('?tab=chapters','')
    
    driver1 = webdriver.Chrome()
    driver1.get(o_title)
    soup1=BeautifulSoup(driver1.page_source)
    god=soup1.find('a',{"class":"badge variant-soft-tertiary"}).get_text(strip=True)
    opisanie=soup1.find('div',{"class":"manga-description overflow-hidden"}).get_text(strip=True)
    genres=''
    for i in soup1.find_all('a',class_='badge variant-soft-tertiary mb-1 mr-1'):
        genres+=f'{i.get_text(strip=True)};'
    i=1
    genres=genres[:-1]
    nomer_glavi=len(items)+1
    db=connect_db()
    dbase=FDATABASE(db)
    dbase.add_title(title_na_rus,title,opisanie,god,cover,genres)
    for item in items:
        glava=item.find('span',{'class':'chapter-title'}).get_text(strip=True)
        glava_url=item.find('a').get('href')
        # if i==0:
        #     global last_glava
        #     last_glava=glava.split('Глава')[1]
        try:
            nomer_glavi-=1
            cursor.execute(f"select title_id from titles where name_on_russian='{title_na_rus}'")
            title_id=cursor.fetchone()[0]
            otdelnaya_glava(title_id,nomer_glavi,glava,glava_url)
        except:
            pass
        i+=1
        # primer+=f'''<li><a href="glavi/Глава{glava.split("Глава")[1]}.html">{glava}</a></li>\n'''
#     else:
#         with open(f'{title}/{title}glavi.html','w',encoding="utf-8") as file:
#             file.write(f'''<!DOCTYPE html>
# <html lang="en">
# <head>
#     <meta charset="UTF-8">
#     <meta name="viewport" content="width=device-width, initial-scale=1.0">
#     <title>Document</title>
#     <link rel="stylesheet" href="../style.css">
# </head>
# <body bgcolor="#f7f7f7">
#     <div style="display: inline-block;vertical-align: top;margin-left:200px;margin-top: 35px;">
#         <img src="{cover}">
#         <a class="glavi_s_pervoy" href="glavi/Глава{glava.split("Глава")[1]}.html">
#             <div class="glavi_s_pervoy">
#                 <b>Читать с 1 главы</b>
#             </div>
#         </a>
#     </div>
#     <div class="container-glavi" style="display: inline-block;">
#         <div class="center">
#             <h2>{title_na_rus}</h2>
#             <p>Год:{god}</p>
#             <p>Описание:{opisanie}</p>
#             <p>Главы:</p>
#             <ul>
#                 {primer}
#             </ul>
#         </div>
#     </div>
# </body>
# </html>''')    
    
        # comps.append({
        #         'title':item.find('span',{"class":"src-pages-TitleView-components-ChapterItem-___styles-module__name"}).get_text(strip=True),
        #         'tom':item.find('span',{"class":"src-pages-TitleView-components-ChapterItem-___styles-module__volume src-pages-TitleView-components-ChapterItem-___styles-module__mobile"}).get_text(strip=True),
        #         'href':f"https://mangalib.me{item.find('a').get('href')}"
        #     })
    # global comp
    # for comp in comps:
    #     print(comp['title'],comp[tom],comp['href'])
        # save()
def otdelnaya_glava(title_id,nomer_glavi,glava,href):
    Headers={
        'User-Agent':'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/117.0.0.0 Safari/537.36 Edg/117.0.2045.43'
    }
    driver = webdriver.Chrome()

    driver.get(href)
    html = driver.page_source.encode('utf-8') 
    soup = BeautifulSoup(html)
    images=''
    # primer=''
    i=1
    for link in soup.find("div", {"class": "pt-4 mx-auto outline-0 cursor-auto w-full"}).findAll("img"):
        # if i==1:
        #     primer+=f'''<div class="carousel-item active">
        #     <img class="d-block mx-auto" src="{link.get('src')}" alt="First slide">
        #   </div>'''
        # else:
        #     primer+=f'''<div class="carousel-item">
        #     <img class="d-block mx-auto" src="{link.get('src')}" alt="Third slide">
        #   </div>'''
        # i+=1
        images+=f"{link.get('src')};"
    else:
        images=images[:-1]
    # path=f'{title}/glavi'
    db=connect_db()
    dbase=FDATABASE(db)
    dbase.add_glava(title_id,nomer_glavi,glava,images)

#     try:
#         os.mkdir(path)
#     except:
#         pass
#     comment='''<script>
#   let comments=[];
#   loadComments();
#   document.getElementById('comment-add').onclick=function(){
#     event.preventDefault();
#     let comment_author=document.getElementById('author');
#     let comment_text=document.getElementById('comment-text');
#     let comment={
#         'author':comment_author.value,
#         'text':comment_text.value
#     }
#     comment_author.value='';
#     comment_text.value='';
#     comments.push(comment);
#     saveComment();
#     showComments();
#   }
#   function showComments(){
#     let comment_field=document.getElementById('comment-field');
#     let out='';
#     comments.forEach(function(item){
#       out+=`<div class="odinComment"><h2>Пользователь: ${item.author}</h2>`;
#       out+=`<p>${item.text}</p></div>`;
#     });
#     comment_field.innerHTML = out;
#   }
# '''
#     save_com="""function saveComment(){
#     localStorage.setItem('"""+f"""{title}glava{"".join(glava.split("Глава")[1])}',JSON.stringify(comments));"""+"}"
#     load_com="""function loadComments(){if (localStorage.getItem('"""+f"""{title}glava{"".join(glava.split("Глава")[1])}')) comments = JSON.parse(localStorage.getItem('{title}glava{"".join(glava.split("Глава")[1])}'));
#     showComments();"""+"}"
#     comment+=f"{save_com}\n{load_com}</script>"
#     next_prev_glavi=''
#     global last_glava
#     if int(glava.split("Глава")[1])==1:
#         next_prev_glavi=f'''<a style="margin-left: 200px;" class="nextGlava" href="Глава {int(glava.split("Глава")[1])+1}.html">
#         <div  class="nextGlava">
#             <b>Следующая глава</b>
#         </div>
#       </a>'''
#     elif int(glava.split("Глава")[1])==int(last_glava):
#         next_prev_glavi=f'''<a style="margin-left: 350px;"class="nextGlava" href="Глава {int(glava.split("Глава")[1])-1}.html">
#         <div class="nextGlava">
#             <b>Предыдущая глава</b>
#         </div>
#       </a>'''
#     else:
#         next_prev_glavi=f'''<a style="margin-left: 350px;"class="nextGlava" href="Глава {int(glava.split("Глава")[1])-1}.html">
#         <div class="nextGlava">
#             <b>Предыдущая глава</b>
#         </div>
#       </a>
#       <a style="margin-left: 200px;" class="nextGlava" href="Глава {int(glava.split("Глава")[1])+1}.html">
#         <div  class="nextGlava">
#             <b>Следующая глава</b>
#         </div>
#       </a>'''
#     with open(f'{title}/glavi/Глава{glava.split("Глава")[1]}.html','w',encoding="utf-8") as file:
#         file.write(f'''<!DOCTYPE html>
# <html lang="en">
# <head>
#     <meta charset="UTF-8">
#     <meta name="viewport" content="width=device-width, initial-scale=1.0">
#     <title>Document</title>
#     <link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/bootstrap@4.0.0/dist/css/bootstrap.min.css" integrity="sha384-Gn5384xqQ1aoWXA+058RXPxPg6fy4IWvTNh0E263XmFcJlSAwiGgFAW/dAiS6JXm" crossorigin="anonymous">
#     <link rel="stylesheet" href="..\..\style.css">
# </head>
# <body>
#     <div style="max-width: 100%;margin: 0 auto;" id="carouselExampleControls" class="carousel slide" data-ride="carousel" data-interval="false">
#         <div class="carousel-inner">
#          {primer}
#         </div>
#         <a class="carousel-control-prev" style="width: 50%;" href="#carouselExampleControls" role="button" data-slide="prev">
#           <span class="carousel-control" aria-hidden="true"></span>
#           <span class="sr-only">Previous</span>
#         </a>
#         <a class="carousel-control-next" style="width: 50%;" href="#carouselExampleControls" role="button" data-slide="next">
#           <span class="carousel-control" aria-hidden="true"></span>
#           <span class="sr-only">Next</span>
#         </a>
#       </div>
#       {next_prev_glavi}
      
#       <center><h2 style="margin-top: 50px;">Обусудить главу</h2></center>
#       <div class="comment-container">
#         <form>
#           <div class="group">
#             <label for="author">Имя:</label>
#             <input type="name" class="commnet-name" id="author" placeholder="Введите свое имя">
#           </div>
#           <div class="group">
#             <label for="comment-text">Комментарий:</label>
#             <input type="name" class="commnet-text" id="comment-text" placeholder="Введите коммент">
#           </div>
#           <div class="group">
#             <button type="submit" id="comment-add" class="add_comment">Добавить комментарий</button>
#           </div>
#         </form>
#         <div class="comments">
#           <div id="comment-field">
            
#           </div>
#         </div>
        
#       </div>
#       {comment}
#       <script src="https://code.jquery.com/jquery-3.2.1.slim.min.js" integrity="sha384-KJ3o2DKtIkvYIK3UENzmM7KCkRr/rE9/Qpg6aAZGJwFDMVNA/GpGFF93hXpG5KkN" crossorigin="anonymous"></script>
# <script src="https://cdn.jsdelivr.net/npm/popper.js@1.12.9/dist/umd/popper.min.js" integrity="sha384-ApNbgh9B+Y1QKtv3Rn7W3mgPxhU9K/ScQsAP7hUibX39j7fakFPskvXusvfa0b4Q" crossorigin="anonymous"></script>
# <script src="https://cdn.jsdelivr.net/npm/bootstrap@4.0.0/dist/js/bootstrap.min.js" integrity="sha384-JZR6Spejh4U02d8jOt6vLEHfe/JQGiRRSQQxSfFWpi1MquVdAyjUar5+76PVCmYl" crossorigin="anonymous"></script>
# </body>
# </html>''')
dbase=FDATABASE(db)
allTitles=dbase.getAllTitles()
titles_from_bd=[]
for i in allTitles:
    titles_from_bd.append(i[2])
title_id=1
lines=[] 
with open('titli.txt',encoding='utf-8') as fp:
    lines = fp.readlines()
for line in lines:
    title=line.split(';')[0]
    href=line.split(';')[1]
    title_na_rus=line.split(';')[2]
    if title not in titles_from_bd:
        glavi(href,title,title_na_rus)
    title_id+=1
os.system('shutdown -s')




# db=connect_db()
# dbase=FDATABASE(db)
# title_id=1
# lines=[] 
# with open('titli.txt',encoding='utf-8') as fp:
#     lines = fp.readlines()
# for line in lines:
#     if title_id>5:
#         title=line.split(';')[0]
#         href=line.split(';')[1]
#         title_na_rus=line.split(';')[2]
#         Headers={
#             'User-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) '
#             'AppleWebKit/537.36 (KHTML, like Gecko) '
#             'Chrome/85.0.4183.121 Safari/537.36',
#             'Accept-Language': 'en',
#             'accept': '*/*',
#             'origin': 'https://best.aliexpress.ru',
#             'sec-fetch-site': 'cross-site',
#             'sec-fetch-mode': 'cors',
#             'sec-fetch-dest': 'empty',
#             'referer': 'https://best.aliexpress.ru/',
#             'accept-language': 'ru-RU,ru;q=0.9,en-US;q=0.8,en;q=0.7'
#             }
#         response=requests.get(href[:-13],headers=Headers)
#         soup=BeautifulSoup(response.content,'html.parser')
#         genres=''
#         for i in soup.find_all('a',class_='badge variant-soft-tertiary mb-1 mr-1'):
#             genres+=f'{i.get_text(strip=True)};'
#         genres=genres[:-1]
#         print(genres)
#     title_id+=1

# os.system('shutdown -s')


# parse()



#без дупликатов
# lines_seen = set() 
# with open("itemsInfo.txt", "r", encoding="utf-8") as file:
#     with open("itemsIsaac.txt", "w", encoding="utf-8") as output:
#         for line in file:
#             if line not in lines_seen: 
#                 output.write(line) 
#                 lines_seen.add(line)


                
# lines=[]                
# with open('itemsIsaac.txt',encoding='utf-8') as fp:
#     lines = fp.readlines()
# cards=''
# row=''
# ladno=0
# for line in lines:
#     name=line.split(';')[0]
#     id=line.split(';')[1]
#     quality=line.split(';')[2]
#     description=line.split(';')[3]
#     image=line.split(';')[4]
    # href=line.split(';')[5]
#     if quality=='Качество: 0':
#         xz=f'''<div class="card1"><a style="color: inherit;" href="{href}">
#                             <center>
#                                 <h2 class="FIO">{name}</h2>
#                                 <img class="Fotka1" src="{image}">
#                                 <p style="color: #7C8097; font-style:italic">
#                                     <h2>{id}</h2>
#                                     <p>{quality}</p>
#                                     <p>Описание:{description}</p>
#                                 </p>
#                             </center>
#                         </a></div>'''
#         row+=xz
#         ladno+=1
#         if ladno==4:
#             cards+=f'''<div class="row">
#                     {row}
#                 </div>'''
#             row=''
#             ladno=0
#     elif quality=='Качество: 1':
#         xz=f'''<div class="card1 cardQuality1"><a style="color: inherit;" href="{href}">
#                             <center>
#                                 <h2 class="FIO">{name}</h2>
#                                 <img class="Fotka1" src="{image}">
#                                 <p style="color: #7C8097; font-style:italic">
#                                     <h2>{id}</h2>
#                                     <p>{quality}</p>
#                                     <p>Описание:{description}</p>
#                                 </p>
#                             </center>
#                         </a></div>'''
#         row+=xz
#         ladno+=1
#         if ladno==4:
#             cards+=f'''<div class="row">
#                     {row}
#                 </div>'''
#             row=''
#             ladno=0
#     elif quality=='Качество: 2':
#         xz=f'''<div class="card1 cardQuality2"><a style="color: inherit;" href="{href}">
#                             <center>
#                                 <h2 class="FIO">{name}</h2>
#                                 <img class="Fotka1" src="{image}">
#                                 <p style="color: #7C8097; font-style:italic">
#                                     <h2>{id}</h2>
#                                     <p>{quality}</p>
#                                     <p>Описание:{description}</p>
#                                 </p>
#                             </center>
#                         </a></div>'''
#         row+=xz
#         ladno+=1
#         if ladno==4:
#             cards+=f'''<div class="row">
#                     {row}
#                 </div>'''
#             row=''
#             ladno=0
#     elif quality=='Качество: 3':
#         xz=f'''<div class="card1 cardQuality3"><a style="color: inherit;" href="{href}">
#                             <center>
#                                 <h2 class="FIO">{name}</h2>
#                                 <img class="Fotka1" src="{image}">
#                                 <p style="color: #7C8097; font-style:italic">
#                                     <h2>{id}</h2>
#                                     <p>{quality}</p>
#                                     <p>Описание:{description}</p>
#                                 </p>
#                             </center>
#                         </a></div>'''
#         row+=xz
#         ladno+=1
#         if ladno==4:
#             cards+=f'''<div class="row">
#                     {row}
#                 </div>'''
#             row=''
#             ladno=0
#     elif quality=='Качество: 4':
#         xz=f'''<div class="card1 cardQuality4"><a style="color: inherit;" href="{href}">
#                             <center>
#                                 <h2 class="FIO">{name}</h2>
#                                 <img class="Fotka1" src="{image}">
#                                 <p style="color: #7C8097; font-style:italic">
#                                     <h2>{id}</h2>
#                                     <p>{quality}</p>
#                                     <p>Описание:{description}</p>
#                                 </p>
#                             </center>
#                         </a></div>'''
#         row+=xz
#         ladno+=1
#         if ladno==4:
#             cards+=f'''<div class="row">
#                         {row}
#                     </div>'''
#             row=''
#             ladno=0
# cards+=f'''<div class="row">
#                     {row}
#                 </div>'''
# html= f'''<!DOCTYPE html>
# <html lang="en">
# <head>
#     <meta charset="UTF-8">
#     <meta name="viewport" content="width=device-width, initial-scale=1.0">
#     <title>Предметы</title>
#     <link rel="stylesheet" href="css.css">
#     <link rel="icon" href="https://res.cloudinary.com/teepublic/image/private/s--aN4wT6aJ--/t_Resized%20Artwork/c_fit,g_north_west,h_1054,w_1054/co_ffffff,e_outline:53/co_ffffff,e_outline:inner_fill:53/co_bbbbbb,e_outline:3:1000/c_mpad,g_center,h_1260,w_1260/b_rgb:eeeeee/c_limit,f_auto,h_630,q_90,w_630/v1485610939/production/designs/1153908_1.jpg">
# </head>
# <body bgcolor="#89C52B" style="margin: 0;overflow-x: hidden;">
#     <ul id="menu">
#         <li><a href="main.html">Главная страница</a></li>
#         <li><a href="characters.html">Персонажи</a></li>
#         <li><a href="items.html">Предметы</a></li>
#         <li><a href="mods.html">Моды</a></li>
#       </ul>
#     {cards}
#     <br>
#     <br>
#     <br>
#     <br>
#     <footer>
#         <center>
#         <div class="container">
#           <div class="row">
#             <div class="col-sm-12 col-md-6">
#               <h6>Инфо</h6>
#               <p class="text-justify">Сайт был сделан я ну кароче хз сами думайте Реклама:В игре «Танки Онлайн» изменится система контейнеров: все контейнеры будут конвертированы в ключи, либо открыты автоматически.

#                 Накапливать теперь нужно ключи, а не контейнеры. Везде, где раньше вы получали контейнеры, теперь будут ключи: миссии, челленджи, спецпредложения. Под каждый тип контейнера существует свой ключ. 1 ключ — 1 открытый контейнер. Из стандартных контейнеров возможно получить ключ к ультраконтейнерам, а из них — к скин-контейнерам.</p>
#               <p class="copyright-text">Copyright &copy; 2023 Made by Kutenchik/Nurken/DontPanic.
#                    </p>
#             </div>
#           </div>
#         </div>
#         </center>
#       </footer>
# </body>
# </html>'''
# with open('items.html','w',encoding="utf-8") as file:
#   file.write(html)
