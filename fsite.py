from flask import Flask,render_template,url_for,request,session,redirect,g,abort,flash,jsonify
import psycopg2
import os
from FDATABASE import FDATABASE
from UserLogin import UserLogin
from werkzeug.security import generate_password_hash,check_password_hash
from werkzeug.utils import secure_filename
from flask_login import LoginManager,login_user,login_required,logout_user,current_user
import re
from numerize import numerize
from datetime import datetime
from bs4 import BeautifulSoup
import requests
import json
import subprocess
DATABASE='site'
DEBUG=True
SECRET_KEY='SFNOLNSAOL$231FDSAO'
app=Flask(__name__)
upload_folder = os.path.join('static', 'uploads')
app.config['UPLOAD'] = upload_folder
app.config.from_object(__name__)
login_manager=LoginManager(app)
login_manager.login_view='login'
login_manager.login_message='Чтоб посмотреть нужно зарегистрироваться'
login_manager.login_message_category='success'
@login_manager.user_loader
def load_user(user_id):
    return UserLogin().fromDb(user_id,dbase)

def connect_db():
    conn=psycopg2.connect(
    dbname=app.config['DATABASE'],
    user='postgres',
    password='kutenchik',
    host='localhost'
)
    return conn
def create_db():
    db=connect_db()
    with app.open_resource('sql.sql',mode='r') as file:
        db.cursor().execute(file.read())
    db.commit()
    db.close()

def get_db():
    if not hasattr(g,'link_db'):
        g.link_db=connect_db()
    return g.link_db
dbase=None
@app.before_request
def before_request():
    global dbase
    db=get_db()
    dbase=FDATABASE(db)
@app.context_processor
def poRofluRandomIzWiki():
    # try:
    #     url = 'https://ru.wikipedia.org/wiki/%D0%A1%D0%BB%D1%83%D0%B6%D0%B5%D0%B1%D0%BD%D0%B0%D1%8F:%D0%A1%D0%BB%D1%83%D1%87%D0%B0%D0%B9%D0%BD%D0%B0%D1%8F_%D1%81%D1%82%D1%80%D0%B0%D0%BD%D0%B8%D1%86%D0%B0'
    #     response = requests.get(url)
    #     soup = BeautifulSoup(response.content, 'html.parser')
    #     mw_content = soup.find('div', class_='mw-content-ltr mw-parser-output')
    #     if mw_content.find('p'):
    #         first_p = mw_content.find('p').get_text()
    # except:
    #     first_p='Ра́йан То́мас Го́слинг (англ. Ryan Thomas Gosling, род. 12 ноября 1980 (1980-11-12), Лондон, Онтарио, Канада) — канадский актёр и музыкант. Известный в независимом кино, он также работал в блокбастерах различных жанров. Получил различные награды, в том числе премию «Золотой глобус», а также номинации на две премии «Оскар», четыре премии Гильдии киноактёров США и премию BAFTA.'
    first_p='Ра́йан То́мас Го́слинг (англ. Ryan Thomas Gosling, род. 12 ноября 1980 (1980-11-12), Лондон, Онтарио, Канада) — канадский актёр и музыкант. Известный в независимом кино, он также работал в блокбастерах различных жанров. Получил различные награды, в том числе премию «Золотой глобус», а также номинации на две премии «Оскар», четыре премии Гильдии киноактёров США и премию BAFTA.'
    return dict(footer_text=first_p)
@app.teardown_appcontext
def close_db(error):
    if hasattr(g,'link_db'):
        g.link_db.close()
@app.route('/')
def index():
    vse=dbase.getAllTitles()
    numerized=dbase.get_numerized(vse)
    recomend_titles=dbase.find_user_recommendations(current_user.get_id())
    last_updated_titles=dbase.get_last_updated_titles()
    return render_template('mainPage.html',titles=vse,mostPopular=dbase.getMostPopularTitles(),title='Главная страница',amount_of_views=numerized,recomend_titles=recomend_titles,last_updated_titles=last_updated_titles)

def is_valid_input(input_string):
    pattern = r'^[a-zA-Z0-9_]+$'
    return bool(re.match(pattern, input_string))

@app.route('/registration', methods=['POST', 'GET'])
def registration():
    if request.method == 'POST':
        if not all(is_valid_input(request.form[field]) for field in ['username', 'password']):
            flash('Пожалуйста, используйте только английские буквы, цифры и символ подчеркивания для имени пользователя и пароля', 'error')
            return render_template('reg.html')
        hash = generate_password_hash(request.form['password'])
        res = dbase.add_user(request.form['username'], hash, request.form['email'])
        if res:
            user=dbase.getUserByEmailOrUsername(request.form['username'])
            userlogin=UserLogin().create(user)
            login_user(userlogin,remember=True)
            return redirect(url_for('profile'))
        else:
            flash('Пользователь с данным именем или почтой уже зарегистрирован', 'error')
    return render_template('reg.html')
@app.errorhandler(404)
def pageNotFound(error):
    return render_template('pageNotFound.html')
@app.route("/titles/<nazvanie>")
def showTitle(nazvanie):
    titile_id,title_name_on_english,title_name_on_russian,description,year,cover_url,genres,amount_of_views,glava_count,rating=dbase.getTitle(nazvanie)
    if not title_name_on_english:
        abort(404)
    if not rating:
        rating=0
    url = nazvanie
    vse=dbase.getAllTitles()
    numerized=dbase.get_numerized(vse)
    if 'lastTitles' in session:
        urls_list = session['lastTitles']
        if url not in urls_list:
            urls_list.append(url)
            if len(urls_list) > 5:
                urls_list.pop(0)
            session['lastTitles'] = urls_list
    else:
        session['lastTitles'] = [url]
    readed_chapters=[]
    if current_user.is_authenticated:
        readed_chapters=dbase.get_readed_chapters(current_user.get_id(),titile_id)
    glavi=dbase.getGlavi(titile_id)
    is_favorite = dbase.title_in_favorites(current_user.get_id(), titile_id)
    lastChapter=dbase.get_last_readed_chapter(current_user.get_id(),titile_id)
    recomend_titles=dbase.find_title_recommendations(titile_id)
    return render_template('primerTitle.html',rating=rating,title=title_name_on_russian,description=description,year=year,cover=cover_url,glavi=glavi,dlyaUrl=title_name_on_english,genres=genres.split(';'),prosmotri=numerize.numerize(int(dbase.add_view(title_name_on_english))),id=titile_id,is_favorite=is_favorite,lastChapter=lastChapter,recomend_titles=recomend_titles,amount_of_views=numerized,readed_chapters=readed_chapters)
@login_required
@app.route('/titles/<int:title_id>/rate', methods=['POST'])
def rate_title(title_id):
    rating_value = round(float(request.get_json().get('rating')), 2)
    dbase.add_rating_to_title(current_user.get_id(),title_id,rating_value)
    return redirect(request.referrer)
@app.route("/titles/<nazvanie>/<int:nomer_glavi>",methods=['POST','GET'])
@login_required
def showGlava(nazvanie,nomer_glavi):
    dbase.glava_achievement(current_user.get_id())
    title_id = dbase.get_title_id_by_name(nazvanie)
    title_type = dbase.get_type(title_id)
    if request.method=='POST':
        if request.form['comment_input'].rstrip()=='':
            flash('Комментарий не должен быть путсым','error')
        else:
            com=request.form['comment_input'].replace("'","''")
            comment_date=datetime.today().strftime('%d/%m/%Y')
            dbase.addComment(title_name=nazvanie,glava_number=nomer_glavi,user_id=current_user.get_id(),comment_text=com.rstrip(),comment_date=comment_date)
    try:
        if title_type=='манга':
            images=dbase.showGlava(nazvanie,nomer_glavi)[0].split(';')
            name_on_russian=dbase.showGlava(nazvanie,nomer_glavi)[2]
            comments=dbase.getComments(nazvanie,nomer_glavi)
            first_image=images[0]
            images.pop(0)
            last_glava=dbase.getLastGlava(nazvanie)[0]
            glavi=dbase.getGlavi(title_id)
            glava=dbase.showGlava(nazvanie,nomer_glavi)[3]
        elif title_type=='ранобе':
            content_glavi=dbase.showGlava(nazvanie,nomer_glavi)[0]
            name_on_russian=dbase.showGlava(nazvanie,nomer_glavi)[2]
            comments=dbase.getComments(nazvanie,nomer_glavi)
            last_glava=dbase.getLastGlava(nazvanie)[0]
            glavi=dbase.getGlavi(title_id)
            glava=dbase.showGlava(nazvanie,nomer_glavi)[3]
        elif title_type=='аниме':
            html_code=dbase.showGlava(nazvanie,nomer_glavi)[0]
            name_on_russian=dbase.showGlava(nazvanie,nomer_glavi)[2]
            comments=dbase.getComments(nazvanie,nomer_glavi)
            last_glava=dbase.getLastGlava(nazvanie)[0]
            glavi=dbase.getGlavi(title_id)
            glava=dbase.showGlava(nazvanie,nomer_glavi)[3]
    except:
        abort(404)
    readed_chapters=dbase.get_readed_chapters(current_user.get_id(),title_id)
    if nomer_glavi not in [_[0] for _ in readed_chapters]:
        dbase.add_exp(current_user.get_id(),10)
    dbase.add_last_readed_chapter(current_user.get_id(),dbase.get_title_id_by_name(nazvanie),nomer_glavi)
    dbase.user_chapter_status(current_user.get_id(),dbase.get_title_id_by_name(nazvanie),nomer_glavi)
    readed_chapters=dbase.get_readed_chapters(current_user.get_id(),title_id)
    if title_type=='манга':
        try:
            return render_template('Glava.html',title=name_on_russian,first_page=first_image,pages=images,dlyaUrl=nazvanie,nomer=nomer_glavi,last_glava=last_glava,comments=comments,kolvo_com=len(comments),glavi=glavi,cur_glava=glava,readed_chapters=readed_chapters)
        except:
            return render_template('Glava.html',title=name_on_russian,first_page=first_image,pages=images,dlyaUrl=nazvanie,nomer=nomer_glavi,last_glava=last_glava,comments=comments,glavi=glavi,cur_glava=glava,readed_chapters=readed_chapters)
    elif title_type=='ранобе':
        try:
            return render_template('ranobeGlava.html',title=name_on_russian,content_glavi=content_glavi,dlyaUrl=nazvanie,nomer=nomer_glavi,last_glava=last_glava,comments=comments,kolvo_com=len(comments),glavi=glavi,cur_glava=glava,readed_chapters=readed_chapters)
        except:
            return render_template('ranobeGlava.html',title=name_on_russian,content_glavi=content_glavi,dlyaUrl=nazvanie,nomer=nomer_glavi,last_glava=last_glava,comments=comments,glavi=glavi,cur_glava=glava,readed_chapters=readed_chapters)
    elif title_type=='аниме':
        try:
            return render_template('animeSeriya.html',title=name_on_russian,html_code=html_code,dlyaUrl=nazvanie,nomer=nomer_glavi,last_glava=last_glava,comments=comments,kolvo_com=len(comments),glavi=glavi,cur_glava=glava,readed_chapters=readed_chapters)
        except:
            return render_template('animeSeriya.html',title=name_on_russian,html_code=html_code,dlyaUrl=nazvanie,nomer=nomer_glavi,last_glava=last_glava,comments=comments,glavi=glavi,cur_glava=glava,readed_chapters=readed_chapters)
@app.route('/login',methods=['POST','GET'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('profile'))
    if request.method=='POST':
        user=dbase.getUserByEmailOrUsername(request.form['emialOrUsername'])
        if user and check_password_hash(user[2],request.form['password']):
            userlogin=UserLogin().create(user)
            rm=True if request.form.get('remainme') else False
            login_user(userlogin,remember=rm)
            return redirect(request.args.get('next') or url_for('profile'))
        flash('Неверный логин или пароль','error')
    return render_template('login.html',title='Авторизация')
@app.route('/logout')
@login_required
def logout():
    logout_user()
    flash('Вы успешно вышли из аккаунта','success')
    return redirect(url_for('login'))

@app.route('/profile', methods=['GET', 'POST'])
@login_required
def profile():
    user_achievements=dbase.show_users_achievements(current_user.get_id())
    level,rem_exp,lvl_porog=dbase.get_level(int(current_user.get_exp()))
    if request.method == 'POST':
        if request.files['img']:
            file = request.files['img']
            filename = secure_filename(file.filename)
            save_path = os.path.join(app.config['UPLOAD'], filename)
            base, ext = os.path.splitext(filename)
            counter = 1
            while os.path.exists(save_path):
                new_filename = f"{base}({counter}){ext}"
                save_path = os.path.join(app.config['UPLOAD'], new_filename)
                counter += 1
            file.save(save_path)
            img = save_path
            dbase.add_profile_pic(current_user.get_id(),img)
        if request.form['description']!='Пусто':
            dbase.add_description(current_user.get_id(),request.form['description'])
    try:
        vse=dbase.getAllTitles()
        prosmotrennie=[]
        for i in session['lastTitles']:
            for j in vse:
                if i==j[2]:
                    prosmotrennie.append(j)
        fav_nazv=dbase.get_user_favorites(current_user.get_id())
        fav=[]
        for i in fav_nazv:
            for j in vse:
                if i[0]==j[2]:
                    fav.append(j)
        numerized=dbase.get_numerized(prosmotrennie)
        numerized2=dbase.get_numerized(fav)
        if current_user.get_profilePic()!='None':
            return render_template('profile.html',title='Профиль',user_id=current_user.get_id(),last_seen=prosmotrennie,amount_of_views=numerized,profile_pic=current_user.get_profilePic(),description=current_user.get_description().replace('\n', '<br>'),fav=fav,amount=numerized2,user_achievements=user_achievements,level=level,rem_exp=rem_exp,lvl_porog=lvl_porog)
        else:
            return render_template('profile.html',title='Профиль',user_id=current_user.get_id(),last_seen=prosmotrennie,amount_of_views=numerized,description=current_user.get_description().replace('\n', '<br>'),fav=fav,amount=numerized2,user_achievements=user_achievements,level=level,rem_exp=rem_exp,lvl_porog=lvl_porog)
    except:
        if current_user.get_profilePic()!='None':
            return render_template('profile.html',title='Профиль',user_id=current_user.get_id(),profile_pic=current_user.get_profilePic(),description=current_user.get_description().replace('\n', '<br>'),user_achievements=user_achievements,level=level,rem_exp=rem_exp,lvl_porog=lvl_porog)
        else:
            return render_template('profile.html',title='Профиль',user_id=current_user.get_id(),description=current_user.get_description().replace('\n', '<br>'),user_achievements=user_achievements,level=level,rem_exp=rem_exp,lvl_porog=lvl_porog)
@app.route("/users/<username>")
@login_required
def showProfile(username):
    id,user,profile_pic,description,status,exp=dbase.get_another_user(username)
    if not id:
        abort(404)
    if user==current_user.get_username():
        return redirect(url_for('profile'))
    user_achievements=dbase.show_users_achievements(str(id))
    level,rem_exp,lvl_porog=dbase.get_level(exp)
    vse=dbase.getAllTitles()
    fav_nazv=dbase.get_user_favorites(str(id))
    fav=[]
    for i in fav_nazv:
        for j in vse:
            if i[0]==j[2]:
                fav.append(j)
    numerized2=dbase.get_numerized(fav)
    return render_template('user.html',id=id,username=user,profile_pic=profile_pic,description=description.replace('\n', '<br>'),user_achievements=user_achievements,fav=fav,amount=numerized2,status=status,level=level,rem_exp=rem_exp,lvl_porog=lvl_porog)
@app.route('/poisk', methods=['GET', 'POST'])
def poisk():
    vse=dbase.getAllTitles()
    numerized=dbase.get_numerized(vse)
    uniq_genres=dbase.get_uniq_genres()
    if request.method == 'POST':
        if request.form.get('search_form') == 'name_search':
            name=request.form['poisk']
            titles=dbase.poisk(name)
            if titles:
                return render_template('poisk.html',title='Поиск',titles=titles,amount_of_views=numerized,uniq_genres=uniq_genres)
            else:
                try:
                    xz=[]
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
                    items1=soup.findAll('div',class_='scroller-item me-3')
                    for i in items1:
                        title=i.find('a',class_='fw-medium').get_text(strip=True)
                        href=f"https://mangahub.ru{i.find('a',class_='d-block rounded fast-view-layer').get('href')}"
                        cover=i.find('div',class_='fast-view-layer-scale').get('data-background-image')
                        xz.append([title,cover,href])
                    if xz:
                        return render_template('poisk.html',data=xz,title='Поиск',uniq_genres=uniq_genres)
                    else:
                        return render_template('poisk.html',title='Поиск',titles=vse,amount_of_views=numerized,uniq_genres=uniq_genres)
                except:
                    return render_template('poisk.html',title='Поиск',titles=vse,amount_of_views=numerized,uniq_genres=uniq_genres)
        elif request.form.get('search_form') == 'filter_search':
            selected_items = request.form.getlist('selected_genres')
            chapter_start=request.form['chapter_start']
            chapter_end=request.form['chapter_end']
            year_start=request.form['year_start']
            year_end=request.form['year_end']
            title_types=request.form.getlist('selected_type')
            if not title_types:
                title_types=['манга']
            if not chapter_start:
                chapter_start=1
            if not chapter_end:
                chapter_end=10000000
            if not year_start:
                year_start=1900
            if not year_end:
                year_end=2024
            if int(chapter_start)>int(chapter_end):
                chapter_start,chapter_end=chapter_end,chapter_start
            if int(year_start)>int(year_end):
                year_start,year_end=year_end,year_start
            titles=dbase.get_titles_with_genres(selected_items,chapter_start,chapter_end,year_start,year_end,title_types)
            if titles:
                numerized=dbase.get_numerized(titles)
                uniq_genres=dbase.get_uniq_genres()
                return render_template('poisk.html',title='Поиск',titles=titles,amount_of_views=numerized,uniq_genres=uniq_genres)
    return render_template('poisk.html',title='Поиск',titles=vse,amount_of_views=numerized,uniq_genres=uniq_genres)
@app.route('/add_to_favorite/<title_name>', methods=['POST'])
def add_to_favorite(title_name):
    if request.method == 'POST':
        dbase.add_to_favorites(current_user.get_id(), title_name)
        return redirect(request.referrer)
@app.route('/toggle_favorite/<int:title_id>', methods=['POST'])
def toggle_favorite(title_id):
    action = request.form.get('action')
    if action == 'add':
        dbase.add_to_favorites(current_user.get_id(), title_id)
    elif action == 'remove':
        dbase.remove_from_favorites(current_user.get_id(), title_id)
    return redirect(request.referrer)
@app.route('/admin', methods=['GET', 'POST'])
@login_required
def admin():
    if current_user.get_status()=='Админ':
        if request.method == 'POST':
            name_on_rus=request.form['name_on_rus']
            name_on_eng=request.form['name_on_eng']
            href=request.form['href']
            with open('titli.txt', "a",encoding='utf-8') as myfile:
                myfile.write(f"\n{name_on_eng};{href};{name_on_rus}")
            python_executable = r'C:\Users\kuten\AppData\Local\Programs\Python\Python311\python.exe' 
            file_to_execute = r'C:\Users\kuten\OneDrive\Рабочий стол\kutenchikLib\noviy_parser.py'
            try:
                subprocess.run([python_executable, file_to_execute], check=True, capture_output=True, text=True)
            except subprocess.CalledProcessError as e:
                print("Произошла ошибка:", e)
                print("Вывод:", e.output)
        users=dbase.get_all_users(current_user.get_id())
        return render_template('admin.html',users=users)
    return abort(404)
@app.route('/random_manga')
def random_manga():
    return redirect(url_for('showTitle',nazvanie=dbase.random_manga()))
@app.route('/test')
def testit():
    return render_template('testit.html')
@app.route('/changeStatus', methods=['POST'])
def change_status():
    selected_user = request.form.get('selectedUser')
    selected_status = request.form.get('selectedStatus')
    dbase.change_status(selected_user,selected_status)
    return redirect(request.referrer)
@app.route('/delete_comment', methods=['POST'])
def delete_comment():
    if request.method == 'POST':
        data = request.json
        comment_id = data.get('comment_id')
        dbase.delete_comment(comment_id)
        return redirect(request.referrer)
if __name__=='__main__':
    app.run(debug=True)