from numerize import numerize
class FDATABASE:
    def __init__(self,db):
        self.__db=db
        self.__cur=db.cursor()
    def add_user(self,username,password,email):
        try:
            self.__cur.execute(f"SELECT COUNT(*) FROM USERS WHERE EMAIL='{email}' OR USERNAME='{username}'")
            res=self.__cur.fetchone()
            if res[0]>0:
                return False
            self.__cur.execute(f"INSERT INTO USERS(username,password,email) VALUES('{username}','{password}','{email}')")
            self.__db.commit()
            return True
        except:
            print('oshibka')
        return []
    def getTitle(self,title_name_on_english):
        try:
            title_type=self.get_type(str(self.get_title_id_by_name(title_name_on_english)))
            if title_type=='манга':
                self.__cur.execute(f"""SELECT DISTINCT title_id,name_on_english,NAME_ON_RUSSIAN, description,year,cover, genres, amount_of_views, glava_count, AVG(rating) OVER(PARTITION BY user_ratings.title_id) 
        FROM TITLES
        INNER JOIN (
            SELECT TITLE_ID, COUNT(*) AS GLAVA_COUNT
            FROM GLAVA
            GROUP BY TITLE_ID
        ) AS HZ USING (TITLE_ID) 
        LEFT JOIN user_ratings USING (TITLE_ID) WHERE NAME_ON_ENGLISH='{title_name_on_english}' LIMIT 1""")
                res=self.__cur.fetchone()
                if res:
                    return res
            elif title_type=='ранобе':
                self.__cur.execute(f"""SELECT DISTINCT title_id,name_on_english,NAME_ON_RUSSIAN, description,year,cover, genres, amount_of_views, glava_count, AVG(rating) OVER(PARTITION BY user_ratings.title_id) 
            FROM TITLES
            INNER JOIN (
                SELECT TITLE_ID, COUNT(*) AS GLAVA_COUNT
                FROM RANOBE_GLAVI
                GROUP BY TITLE_ID
            ) AS HZ USING (TITLE_ID) 
            LEFT JOIN user_ratings USING (TITLE_ID) WHERE NAME_ON_ENGLISH='{title_name_on_english}' LIMIT 1""")
                res=self.__cur.fetchone()
                if res:
                    return res
            elif title_type=='аниме':
                self.__cur.execute(f"""SELECT DISTINCT title_id,name_on_english,NAME_ON_RUSSIAN, description,year,cover, genres, amount_of_views, glava_count, AVG(rating) OVER(PARTITION BY user_ratings.title_id) 
            FROM TITLES
            INNER JOIN (
                SELECT TITLE_ID, COUNT(*) AS GLAVA_COUNT
                FROM ANIME_SERII
                GROUP BY TITLE_ID
            ) AS HZ USING (TITLE_ID) 
            LEFT JOIN user_ratings USING (TITLE_ID) WHERE NAME_ON_ENGLISH='{title_name_on_english}' LIMIT 1""")
                res=self.__cur.fetchone()
                if res:
                    return res
        # except:
        #     print('oshibka')
        except Exception as e:
            print(e)
        return (False,False,False,False,False,False,False,False)
    def add_title(self,title_name_on_russian,title_name_on_english,description,year,cover_url,genres,type):
        try:
            self.__cur.execute(f"INSERT INTO TITLES(NAME_ON_RUSSIAN,NAME_ON_english,DESCRIPTION,year,cover,genres,type) VALUES('{title_name_on_russian}','{title_name_on_english}','{description}',{year},'{cover_url}','{genres}','{type}')")
            self.__db.commit()
        except:
            print('oshibka')
    def add_glava(self,title_id,nomer_glavi,glava,images):
        try:
            self.__cur.execute("INSERT INTO glava(title_id, nomer_glavi, glava, images) VALUES (%s, %s, %s, %s)",(title_id, nomer_glavi, glava, images))
            self.__db.commit()
        except Exception as e:
            print(e)
    def add_ranobe_glava(self,title_id,nomer_glavi,glava,content_glavi):
        try:
            self.__cur.execute('INSERT INTO RANOBE_GLAVI(TITLE_ID,nomer_glavi,glava,content_glavi) VALUES(%s,%s,%s,%s)',(title_id,nomer_glavi,glava,content_glavi))
            self.__db.commit()
        except Exception as e:
            print(e)
    def add_seriya(self,title_id,nomer_serii,seriya,nu_tip_text):
        try:
            self.__cur.execute('INSERT INTO ANIME_SERII(TITLE_ID,nomer_glavi,glava,html_code) VALUES(%s,%s,%s,%s)',(title_id,nomer_serii,seriya,nu_tip_text))
            self.__db.commit()
        except Exception as e:
            print(e)
    def getGlavi(self,title_id):
        try:
            title_type=self.get_type(title_id)
            if title_type=='манга':
                self.__cur.execute(f'SELECT NOMER_GLAVI,GLAVA FROM GLAVA INNER JOIN TITLES USING(TITLE_ID) WHERE TITLE_ID={title_id} ORDER BY NOMER_GLAVI DESC')
                res=self.__cur.fetchall()
                if res:return res
            elif title_type=='ранобе':
                self.__cur.execute(f'SELECT NOMER_GLAVI,GLAVA FROM RANOBE_GLAVI INNER JOIN TITLES USING(TITLE_ID) WHERE TITLE_ID={title_id} ORDER BY NOMER_GLAVI DESC')
                res=self.__cur.fetchall()
                if res:return res
            elif title_type=='аниме':
                self.__cur.execute(f'SELECT NOMER_GLAVI,GLAVA FROM ANIME_SERII INNER JOIN TITLES USING(TITLE_ID) WHERE TITLE_ID={title_id} ORDER BY NOMER_GLAVI DESC')
                res=self.__cur.fetchall()
                if res:return res
        except Exception as e:
            print(e)
        return []
    def showGlava(self,title_name,glava_number):
        try:
            title_type=self.get_type(str(self.get_title_id_by_name(title_name)))
            if title_type=='манга':
                self.__cur.execute(f"select images,title_id,name_on_russian,glava from glava inner join titles using(title_id) where nomer_glavi={glava_number} and name_on_english='{title_name}' limit 1")
            elif title_type=='ранобе':
                self.__cur.execute(f"select CONTENT_GLAVI,title_id,name_on_russian,glava from ranobe_glavi inner join titles using(title_id) where nomer_glavi={glava_number} and name_on_english='{title_name}' limit 1")
            elif title_type=='аниме':
                self.__cur.execute(f"select html_code,title_id,name_on_russian,glava from ANIME_SERII inner join titles using(title_id) where nomer_glavi={glava_number} and name_on_english='{title_name}' limit 1")
            res=self.__cur.fetchone()
            if res:return res
        except Exception as e:
            print(e)
        return(False,False,False,False)
    def getLastGlava(self,nazvanie):
        try:
            title_type=self.get_type(self.get_title_id_by_name(nazvanie))
            if title_type=='манга':
                self.__cur.execute(f"select max(nomer_glavi) from glava inner join titles using(title_id) where name_on_english='{nazvanie}' limit 1")
            elif title_type=='ранобе':
                self.__cur.execute(f"select max(nomer_glavi) from RANOBE_GLAVI inner join titles using(title_id) where name_on_english='{nazvanie}' limit 1")
            elif title_type=='аниме':
                self.__cur.execute(f"select max(nomer_glavi) from ANIME_SERII inner join titles using(title_id) where name_on_english='{nazvanie}' limit 1")
            res=self.__cur.fetchone()
            if res:return res
        except Exception as e:
            print(e)
        return(False)
    def get_numerized(self,massiv):
        numerized=[]
        for i in massiv:
            numerized.append(f'{i[0]};{numerize.numerize(int(i[4]))}')
        return numerized
    def getAllTitles(self):
        try:
            self.__cur.execute(f"""SELECT * from titles_for_zapros order by amount_of_views desc""")
            res=self.__cur.fetchall()
            if res:return res
        except Exception as e:
            print(e)
        return[]
    def getMostPopularTitles(self):
        try:
            self.__cur.execute(f"""SELECT * from titles_for_zapros order by amount_of_views desc limit 10""")
            res=self.__cur.fetchall()
            if res:return res
        except Exception as e:
            print(e)
        return[]
    def getComments(self,title_name,glava_number):
        try:
            self.__cur.execute(f"select username,profile_pic,comment_text,comment_date,comment_id from comments inner join users on users.id=comments.user_id where title_name='{title_name}' and nomer_glavi={glava_number}")
            res=self.__cur.fetchall()
            if res:return res
        except Exception as e:
            print(e)
        return(False)
    def addComment(self, title_name, glava_number, user_id, comment_text, comment_date):
        try:
            query = """INSERT INTO COMMENTS(TITLE_NAME, NOMER_GLAVI, USER_ID, COMMENT_TEXT, COMMENT_DATE) 
                    VALUES (%s, %s, %s, %s, %s)"""
            values = (title_name, glava_number, user_id, comment_text, comment_date)
            self.__cur.execute(query, values)
            self.__db.commit()
            self.com_achievement(user_id)
            self.add_exp(user_id,10)
        except Exception as e:
            print(e)

    def getUser(self,user_id):
        try:
            self.__cur.execute(f"select * from users where id={user_id} limit 1")
            res=self.__cur.fetchone()
            if not res:
                return False
            return res
        except Exception as e:
            print(e)
    def getUserByEmailOrUsername(self,emailOrUsername):
        try:
            self.__cur.execute(f"SELECT * FROM USERS WHERE EMAIL='{emailOrUsername}' OR USERNAME='{emailOrUsername}' LIMIT 1")
            res=self.__cur.fetchone()
            if not res:
                return False
            return res
        except Exception as e:
            print(e)
    def add_view(self,title_name_on_english):
        self.__cur.execute(f"SELECT * FROM TITLES WHERE NAME_ON_ENGLISH='{title_name_on_english}' LIMIT 1")
        res=self.__cur.fetchone()
        if res:
            self.__cur.execute(f"UPDATE TITLES SET amount_of_views={res[7]+1} where title_id={res[0]}")
            self.__db.commit()
            return res[7]+1
    def add_profile_pic(self,user_id,img):
        try:
            self.__cur.execute(f"UPDATE USERS SET profile_pic='{img}' where id={user_id}")
            self.__db.commit()
        except Exception as e:
            print(e)
    def poisk(self,nazvanie):
        try:
            self.__cur.execute(f"""SELECT * from titles_for_zapros where lower(name_on_russian) like lower('%{nazvanie}%')""")
            res=self.__cur.fetchall()
            if res:return res
        except Exception as e:
            print(e)
        return []
    def get_another_user(self,username):
        try:
            self.__cur.execute(f"select id,username,profile_pic,description,status,exp from users where username='{username}' limit 1")
            res=self.__cur.fetchone()
            if res:return res
        except Exception as e:
            print(e)
        return (False,False,False,False)
    def add_description(self, user_id, description):
        try:
            query = "UPDATE USERS SET DESCRIPTION = %s WHERE ID = %s"
            self.__cur.execute(query, (description, user_id))
            self.__db.commit()
        except Exception as e:
            print(e)
    # def add_to_favorites(self, user_id, title_name_on_english):
    #         try:
    #             self.__cur.execute("SELECT TITLE_ID FROM TITLES WHERE NAME_ON_ENGLISH = %s LIMIT 1", (title_name_on_english,))
    #             title_id_result = self.__cur.fetchone()
    #             if title_id_result:
    #                 title_id = title_id_result[0]
    #                 self.__cur.execute("INSERT INTO favourites(user_id, title_id) VALUES (%s, %s)", (user_id, title_id))
    #                 self.__db.commit()
    #                 return True
    #             else:
    #                 return False
    #         except Exception as e:
    #             print(e)
    #             return False
    def add_to_favorites(self, user_id, title_id):
        try:
            self.__cur.execute("INSERT INTO favourites(user_id, title_id) VALUES (%s, %s)", (user_id, title_id))
            self.__db.commit()
            return True
        except Exception as e:
            print(e)
            return False
    def remove_from_favorites(self, user_id, title_id):
        try:
            self.__cur.execute("DELETE FROM favourites WHERE user_id = %s AND title_id = %s", (user_id, title_id))
            self.__db.commit()
            return True
        except Exception as e:
            print(e)
            return False
    def title_in_favorites(self, user_id, title_id):
        try:
            self.__cur.execute("SELECT COUNT(*) FROM favourites WHERE user_id = %s AND title_id = %s", (user_id, title_id))
            count = self.__cur.fetchone()[0]
            return count > 0
        except Exception as e:
            print(e)
            return False
    def get_user_favorites(self,user_id):
        try:
            self.__cur.execute("SELECT NAME_ON_ENGLISH FROM FAVOURITES INNER JOIN TITLES USING(TITLE_ID) WHERE user_id=%s",(user_id,))
            res=self.__cur.fetchall()
            if res:return res
        except Exception as e:
            print(e)
        return []
    def get_title_id_by_name(self,name):
        try:
            self.__cur.execute("SELECT title_id FROM titles WHERE name_on_english=%s",(name,))
            res=self.__cur.fetchone()    
            if res:return res[0]
        except Exception as e:
            print(e)
        return False
    def add_last_readed_chapter(self,user_id,title_id,nomer_glavi):
        try:
            self.__cur.execute("SELECT COUNT(*) FROM user_reading_history WHERE user_id = %s AND title_id = %s", (user_id, title_id))
            count = self.__cur.fetchone()[0]
            if count>0:
                 self.__cur.execute("SELECT last_chapter_read FROM user_reading_history WHERE user_id = %s AND title_id = %s", (user_id, title_id))
                 if nomer_glavi>self.__cur.fetchone()[0]:
                     self.__cur.execute("UPDATE user_reading_history SET last_chapter_read=%s WHERE user_id = %s AND title_id = %s", (nomer_glavi,user_id, title_id))
            else:
                self.__cur.execute("INSERT INTO user_reading_history(USER_ID,TITLE_ID,last_chapter_read) VALUES(%s,%s,%s)", (user_id, title_id,nomer_glavi))
            self.__db.commit()
        except Exception as e:
            print(e)
    def get_last_readed_chapter(self,user_id,title_id):
        try:
            self.__cur.execute("SELECT last_chapter_read FROM user_reading_history WHERE user_id = %s AND title_id = %s", (user_id, title_id))
            res=self.__cur.fetchone()[0]   
            if res:return res
        except Exception as e:
            print(e)
        return False
    def find_user_recommendations(self, user_id):
        try:
            self.__cur.execute('SELECT COUNT(*) FROM favourites WHERE user_id = %s', (user_id,))
            count=self.__cur.fetchone()[0]
            if count!=0:
                self.__cur.execute(f"""SELECT NAME_ON_RUSSIAN,cover,name_on_english,genres,amount_of_views,glava_count,year,description,average_rating from titles_for_zapros""")
                all_manga = self.__cur.fetchall()
                self.__cur.execute("""SELECT DISTINCT NAME_ON_RUSSIAN,cover,name_on_english,genres,amount_of_views,COALESCE(manga.glava_count, 0) + COALESCE(ranobe.glava_count, 0) + COALESCE(anime.glava_count, 0) AS glava_count,year,description,AVG(rating) OVER(PARTITION BY title_id) AS average_rating,type
FROM FAVOURITES
LEFT JOIN (
    SELECT TITLE_ID, COUNT(*) AS glava_count
    FROM GLAVA
    GROUP BY TITLE_ID
) AS manga USING(TITLE_ID)
LEFT JOIN (
    SELECT TITLE_ID, COUNT(*) AS glava_count
    FROM RANOBE_GLAVI
    GROUP BY TITLE_ID
)AS ranobe USING(TITLE_ID)
LEFT JOIN (
	SELECT TITLE_ID, COUNT(*) AS glava_count
    FROM ANIME_SERII
    GROUP BY TITLE_ID
)AS ANIME USING(TITLE_ID)
LEFT JOIN user_ratings USING(TITLE_ID) INNER JOIN titles USING (title_id) WHERE favourites.user_id = %s""", (user_id,))
                user_favourites = self.__cur.fetchall()
                user_genres = set()
                user_favourite_titles = set(manga[0] for manga in user_favourites)
                for manga in user_favourites:
                    genres = set(manga[3].split(';'))
                    user_genres.update(genres)
                manga_scores = {}
                for manga in all_manga:
                    name_on_russian, cover, name_on_english, genres, amount_of_views,glava_count,year,description,rating = manga
                    if name_on_russian in user_favourite_titles:
                        continue
                    manga_genres = set(genres.split(';'))
                    common_genres = user_genres.intersection(manga_genres)
                    manga_scores[name_on_russian] = len(common_genres)
                sorted_recommendations = sorted(manga_scores, key=manga_scores.get, reverse=True)[:10]
                recommendations = []
                for title in sorted_recommendations:
                    for manga in all_manga:
                        if manga[0] == title:
                            recommendations.append(manga)
                            break
                return recommendations
            return []
        except Exception as e:
            print(e)
            return []
    def find_title_recommendations(self, title_id):
        self.__cur.execute(f"""SELECT NAME_ON_RUSSIAN,cover,name_on_english,genres,amount_of_views,glava_count,year,description,average_rating from titles_for_zapros""")
        titles_data = self.__cur.fetchall()
        title_type=self.get_type(title_id)
        if title_type=='манга':
            self.__cur.execute(f"""SELECT DISTINCT NAME_ON_RUSSIAN, cover, name_on_english, genres, amount_of_views, glava_count, year, description, AVG(rating) OVER(PARTITION BY user_ratings.title_id) 
    FROM TITLES
    INNER JOIN (
        SELECT TITLE_ID, COUNT(*) AS GLAVA_COUNT
        FROM GLAVA
        GROUP BY TITLE_ID
    ) AS HZ USING (TITLE_ID) 
    LEFT JOIN user_ratings USING (TITLE_ID) WHERE title_id=%s""", (title_id,))
        elif title_type=='ранобе':
            self.__cur.execute(f"""SELECT DISTINCT NAME_ON_RUSSIAN, cover, name_on_english, genres, amount_of_views, glava_count, year, description, AVG(rating) OVER(PARTITION BY user_ratings.title_id)
FROM TITLES
INNER JOIN (
    SELECT DISTINCT TITLE_ID, COUNT(*) AS GLAVA_COUNT
    FROM RANOBE_GLAVI
    GROUP BY TITLE_ID
) AS HZ USING (TITLE_ID)
LEFT JOIN user_ratings USING (TITLE_ID) WHERE title_id=%s""", (title_id,))
        elif title_type=='аниме':
            self.__cur.execute(f"""SELECT DISTINCT NAME_ON_RUSSIAN, cover, name_on_english, genres, amount_of_views, glava_count, year, description, AVG(rating) OVER(PARTITION BY user_ratings.title_id)
FROM TITLES
INNER JOIN (
    SELECT DISTINCT TITLE_ID, COUNT(*) AS GLAVA_COUNT
    FROM ANIME_SERII
    GROUP BY TITLE_ID
) AS HZ USING (TITLE_ID)
LEFT JOIN user_ratings USING (TITLE_ID) WHERE title_id=%s""", (title_id,))
        selected_title = self.__cur.fetchone()
        title_name, title_cover, title_english, title_genres, title_views,title_glava_count,title_year,title_description,title_rating = selected_title
        titles = {}
        for title in titles_data:
            name, cover, name_english, genres, amount_of_views,glava_count,year,description,rating = title
            titles[name.strip()] = [cover, name_english, genres.split(';'), amount_of_views,glava_count,year,description,rating]
        similarity_list = []
        for title, details in titles.items():
            if title != title_name and title!=title_name[:-1]:
                common_genres = set(title_genres.split(';')) & set(details[2])
                similarity_list.append((title, len(common_genres), *details))
        similarity_list.sort(key=lambda x: x[1], reverse=True)
        recommendations = similarity_list[:10] if similarity_list else [(title_name, title_cover, title_english, title_genres.split(';'), title_views,title_glava_count,title_year,title_description,title_rating)]
        return recommendations
    def get_uniq_genres(self):
        query = """
            SELECT DISTINCT unnest(string_to_array(genres, ';')) AS unique_genre FROM TITLES;"""
        self.__cur.execute(query)
        unique_genres = self.__cur.fetchall()
        return sorted(unique_genres)
    def get_titles_with_genres(self, selected_genres,chapter_start,chapter_end,year_start,year_end,title_types):
        placeholders=', '.join(['%s' for _ in title_types])
        query = """
                SELECT NAME_ON_RUSSIAN,cover,name_on_english,genres,amount_of_views,glava_count,year,description,average_rating FROM titles_for_zapros
WHERE glava_count BETWEEN %s AND %s AND YEAR BETWEEN %s AND %s AND type IN%s
            """
        self.__cur.execute(query,(chapter_start,chapter_end,year_start,year_end,tuple(title_types)))
        mangas = self.__cur.fetchall()
        selected_mangas = []
        for manga in mangas:
            title_russian, cover, title_english, genres, views, amount_of_chapters,year,description,rating = manga
            manga_genres = genres.split(';')
            if all(selected_genre in manga_genres for selected_genre in selected_genres):
                selected_mangas.append([title_russian, cover, title_english, genres, views,amount_of_chapters,year,description,rating])
        return selected_mangas
    def add_rating_to_title(self,user_id,title_id,rating):
        try:
            self.__cur.execute(f"SELECT count(*) FROM user_ratings WHERE user_id=%s and title_id=%s", (user_id, title_id))
            count=self.__cur.fetchone()[0]
            if count!=0:
                self.__cur.execute(f"UPDATE user_ratings set rating=%s WHERE user_id=%s and title_id=%s", (rating,user_id, title_id))
                self.__db.commit()
            else:
                self.__cur.execute(f"INSERT INTO user_ratings(user_id,title_id,rating) VALUES(%s,%s,%s)", (user_id, title_id,rating))
                self.__db.commit()
                self.add_exp(user_id,100)
            return True
        except Exception as e:
            print(e)
            return False
    def user_chapter_status(self,user_id,title_id,nomer_glavi):
        try:
            self.__cur.execute("SELECT count(*) FROM USER_CHAPTER_STATUS WHERE user_id=%s and title_id=%s and nomer_glavi=%s", (user_id, title_id,nomer_glavi))
            count=self.__cur.fetchone()[0]
            if count==0:
                self.__cur.execute("INSERT INTO USER_CHAPTER_STATUS(user_id,title_id,nomer_glavi,is_read) VALUES(%s,%s,%s,TRUE)",(user_id, title_id,nomer_glavi))
                self.__db.commit()
            self.add_full_read_title(user_id,title_id)
            return True
        except Exception as e:
            print(e)
            return False
    def get_readed_chapters(self,user_id,title_id):
        try:
            self.__cur.execute("SELECT nomer_glavi FROM USER_CHAPTER_STATUS WHERE user_id=%s and title_id=%s", (user_id, title_id))
            res=self.__cur.fetchall()
            if res:return res
            else:return[]
        except Exception as e:
            print(e)
            return False
    def random_manga(self):
        try:
            self.__cur.execute("""SELECT name_on_english FROM titles ORDER BY RANDOM() LIMIT 1""")
            res=self.__cur.fetchone()[0]
            if res:return res
        except Exception as e:
            print(e)
            return False
    def add_full_read_title(self,user_id,title_id):
        self.__cur.execute('SELECT COUNT(*) FROM USERS_FULL_TITLE_READ WHERE USER_ID=%s AND TITLE_ID=%s',(user_id,title_id))
        count=self.__cur.fetchone()[0]
        if count==0:
            self.__cur.execute("""SELECT GLAVA_COUNT FROM(
        SELECT COUNT(GLAVA) AS GLAVA_COUNT
        FROM GLAVA
        WHERE TITLE_ID=%s
    ) AS HZ""",(title_id,))
            glava_count=self.__cur.fetchone()[0]
            self.__cur.execute("""SELECT count(*) FROM USER_CHAPTER_STATUS WHERE USER_ID=%s AND TITLE_ID=%s""",(user_id,title_id))
            kolvo_prochitanih=self.__cur.fetchone()[0]
            if glava_count==kolvo_prochitanih:
                self.__cur.execute("INSERT INTO USERS_FULL_TITLE_READ(title_id,user_id) VALUES(%s,%s)",(title_id,user_id))
                self.__db.commit()
                self.add_exp(user_id,1000)
        self.__cur.execute('SELECT COUNT(title_id) FROM USERS_FULL_TITLE_READ WHERE USER_ID=%s',(user_id,))
        user_full_title_read_count=self.__cur.fetchone()[0]
        if user_full_title_read_count!=0:
            self.__cur.execute('SELECT ACHIEVEMENT_ID FROM USER_ACHIEVEMENTS WHERE USER_ID=%s AND ACHIEVEMENT_ID IN(3,4)',(user_id))
            res=self.__cur.fetchone()
            if res:
                if res[0]==3 and user_full_title_read_count>=5:
                    self.__cur.execute('UPDATE USER_ACHIEVEMENTS SET ACHIEVEMENT_ID=4 WHERE USER_ID=%s and ACHIEVEMENT_ID=3',(user_id))
                    self.__db.commit()
            else:
                self.__cur.execute('INSERT INTO USER_ACHIEVEMENTS(ACHIEVEMENT_ID,user_id) VALUES(3,%s)',(user_id))
                self.__db.commit()
    def show_users_achievements(self,user_id):
        try:
            self.__cur.execute('SELECT ACHIEVEMNT_NAME,ACHIEVEMENT_DESC,achievement_image FROM USER_ACHIEVEMENTS INNER JOIN ACHIEVEMENTS USING(ACHIEVEMENT_ID) WHERE user_id=%s',(user_id))
            res=self.__cur.fetchall()
            if res:
                return res
        except Exception as e:
            print(e)
            return False
    def com_achievement(self,user_id):
        try:
            self.__cur.execute('SELECT COUNT(*) FROM COMMENTS WHERE USER_ID=%s',(user_id,))
            comment_count=self.__cur.fetchone()[0]
            self.__cur.execute('SELECT ACHIEVEMENT_ID FROM USER_ACHIEVEMENTS WHERE USER_ID=%s AND ACHIEVEMENT_ID IN(1,2)',(user_id))
            res=self.__cur.fetchone()
            if res:
                if comment_count>=5:
                    self.__cur.execute('UPDATE USER_ACHIEVEMENTS SET ACHIEVEMENT_ID=2 WHERE USER_ID=%s and ACHIEVEMENT_ID=1',(user_id))
                    self.__db.commit()
            else:
                self.__cur.execute('INSERT INTO USER_ACHIEVEMENTS(ACHIEVEMENT_ID,user_id) VALUES(1,%s)',(user_id))
                self.__db.commit()
        except Exception as e:
            print(e)
            return False
    def glava_achievement(self,user_id):
        try:
            self.__cur.execute('SELECT COUNT(*) FROM USER_READING_HISTORY WHERE USER_ID=%s',(user_id,))
            readed_glava_count=self.__cur.fetchone()[0]
            self.__cur.execute('SELECT ACHIEVEMENT_ID FROM USER_ACHIEVEMENTS WHERE USER_ID=%s AND ACHIEVEMENT_ID IN(5,6,7)',(user_id))
            res=self.__cur.fetchone()
            if res:
                if readed_glava_count>=100 and readed_glava_count<=500:
                    self.__cur.execute('UPDATE USER_ACHIEVEMENTS SET ACHIEVEMENT_ID=6 WHERE USER_ID=%s and ACHIEVEMENT_ID=5',(user_id))
                    self.__db.commit()
                elif readed_glava_count>=500:
                    self.__cur.execute('UPDATE USER_ACHIEVEMENTS SET ACHIEVEMENT_ID=7 WHERE USER_ID=%s and ACHIEVEMENT_ID=6',(user_id))
                    self.__db.commit()
            else:
                if readed_glava_count>=10:
                    self.__cur.execute('INSERT INTO USER_ACHIEVEMENTS(ACHIEVEMENT_ID,user_id) VALUES(5,%s)',(user_id))
                    self.__db.commit()
        except Exception as e:
            print(e)
            return False
    def get_last_updated_titles(self):
        try:
            self.__cur.execute(f"""SELECT DISTINCT NAME_ON_RUSSIAN,cover,name_on_english,genres,amount_of_views,COALESCE(Manga.glava_count, 0) + COALESCE(Ranobe.glava_count, 0) + COALESCE(anime.glava_count, 0) AS glava_count,year,description,AVG(rating) OVER(PARTITION BY title_id) AS average_rating,
 	GREATEST(
        COALESCE((SELECT MAX(LAST_UPDATE) FROM GLAVA WHERE GLAVA.TITLE_ID = Titles.TITLE_ID), '1900-01-01'::timestamp),
        COALESCE((SELECT MAX(LAST_UPDATE) FROM RANOBE_GLAVI WHERE RANOBE_GLAVI.TITLE_ID = Titles.TITLE_ID), '1900-01-01'::timestamp),
		COALESCE((SELECT MAX(LAST_UPDATE) FROM ANIME_SERII WHERE ANIME_SERII.TITLE_ID = Titles.TITLE_ID), '1900-01-01'::timestamp)
    ) AS last_update
FROM TITLES
LEFT JOIN (
    SELECT TITLE_ID, COUNT(*) AS glava_count
    FROM GLAVA
    GROUP BY TITLE_ID
) AS Manga using(title_id)
LEFT JOIN (
    SELECT TITLE_ID, COUNT(*) AS glava_count
    FROM RANOBE_GLAVI
    GROUP BY TITLE_ID
) AS Ranobe using (title_id)
LEFT JOIN (
	SELECT TITLE_ID, COUNT(*) AS glava_count
    FROM ANIME_SERII
    GROUP BY TITLE_ID
)AS ANIME USING(TITLE_ID)
LEFT JOIN user_ratings using(title_Id) ORDER BY last_update DESC LIMIT 5;
""")
            res=self.__cur.fetchall()
            if res:return res
        except Exception as e:
            print(e)
        return[]
    def get_all_users(self,user_id):
        try:
            self.__cur.execute('SELECT * FROM USERS WHERE ID<>%s',(user_id,))
            res=self.__cur.fetchall()
            if res:return res
        except Exception as e:
            print(e)
    def change_status(self,username,status):
        try:
            self.__cur.execute('UPDATE USERS SET STATUS=%s WHERE USERNAME=%s',(status,username))
            self.__db.commit()
        except Exception as e:
            print(e)
    def delete_comment(self,comment_id):
        try:
            self.__cur.execute('DELETE FROM COMMENTS WHERE COMMENT_ID=%s',(comment_id,))
            self.__db.commit()
        except Exception as e:
            print(e)
    def get_level(self,experience):
        try:
            experience_needed = 10
            level = 2 
            if experience<experience_needed:
                return 1,experience,experience_needed
            else:
                while experience >= experience_needed:
                    ostatok = round(experience - experience_needed)
                    experience_needed += round(experience_needed * 0.15) 
                    experience = ostatok
                    level += 1
            return level-1, experience,experience_needed
        except Exception as e:
            print(e)
    def add_exp(self,user_id,amount):
        try:
            self.__cur.execute('UPDATE USERS SET EXP=EXP+%s WHERE ID=%s',(amount,user_id))
            self.__db.commit()
        except Exception as e:
            print(e)
    def get_type(self,title_id):
        try:
            self.__cur.execute('SELECT TYPE FROM TITLES WHERE TITLE_ID=%s', (title_id,))
            res=self.__cur.fetchone()
            if res: return res[0]
        except Exception as e:
            print(e)