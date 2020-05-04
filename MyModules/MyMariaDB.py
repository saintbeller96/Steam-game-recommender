import pymysql
import re
from pymysql import IntegrityError

Insert_dict = {
    "GAME":"INSERT INTO GAME(id, title, dev, url, released) VALUES (%s, %s, %s, %s, %s)",
    "USER":"INSERT INTO USER(user_id, game_id, play_time) VALUES (%s, %s, %s)",
    "GENRE":"INSERT INTO GAME_GENRE(game_id, genre) VALUES (%s, %s)",
    "TAG":"INSERT INTO GAME_TAG(game_id, tag) VALUES (%s, %s)",

    "game":"INSERT INTO GAME(id, title, dev, url, released) VALUES (%s, %s, %s, %s, %s)",
    "user":"INSERT INTO USER(user_id, game_id, play_time) VALUES (%s, %s, %s)",
    "genre":"INSERT INTO GAME_GENRE(game_id, genre) VALUES (%s, %s)",
    "tag":"INSERT INTO GAME_TAG(game_id, tag) VALUES (%s, %s)",

    "game_empty":"INSERT INTO GAME(id) VALUES (%s)"
}
Update_dict = {
    "GAME":"UPDATE GAME SET title = %s, dev=%s, url=%s, released=%s WHERE id = %s;",
    "USER":"UPDATE USER SET play_time = %s WHERE user_id = %s and game_id = %s;",

    "end":"UPDATE GAME SET isCrawled = %s WHERE id = %s;",

    "game":"UPDATE GAME SET title = %s, dev=%s, url=%s, released=%s WHERE id = %s;",
    "user":"UPDATE USER SET play_time = %s WHERE user_id = %s and game_id = %s;",
}

Exist_dict = {
    "game":"select EXISTS (select * from GAME where id = %s) as success;",
    "user":"select EXISTS (select * from USER where user_id = %s) as success;",

    "GAME":"select EXISTS (select * from GAME where id = %s) as success;",
    "USER":"select EXISTS (select * from USER where user_id = %s) as success;",

    "isCrawled":"select EXISTS (select * from GAME where id = %s and isCrawled = 1) as success;"
}
Search_dict = {
    "game":"select EXISTS (select * from GAME where id = %s) as success;",
    "user":"select EXISTS (select * from USER where user_id = %s) as success;",
}

class MyDBController(object):
    def __init__(self, host, id, pw, db_name):
        self.conn = pymysql.connect(host=host, user=id, password=pw, db=db_name, charset='utf8')
        self.curs = self.conn.cursor()
    
    def checkExist(self, par, id):#있으면 1, 없으면 0 반환
        self.curs.execute(Exist_dict[par], id)
        ret = self.curs.fetchone()[0]
        self.conn.commit()
        return ret
    
    def update_game(self, values):
        try:           
            sql = 'UPDATE GAME SET title = %s, dev=%s, url=%s, released=%s WHERE id = %s;'
            self.curs.execute(sql, (values[1], values[2], values[3], values[4], values[0]))
            self.conn.commit()           
            return True         
        except Exception as e:
            return False
    
    def endprocess(self, id_):
        try:           
            self.curs.execute(Update_dict["end"], (1, id_))
            self.conn.commit()           
            return True         
        except Exception as e:
            print(e)
            return False
    def insert(self, par, values):
        try:
            self.curs.execute(Insert_dict[par], values)
            self.conn.commit()
            return True
        except IntegrityError as e:
            if(par.lower() == 'game'):              
                if(self.update_game(values)):
                    return True
            return False              

    def getUserList(self):
        try:
            sql = "SELECT user_id FROM user GROUP BY user_id;"
            self.curs.execute(sql)
            return [l[0] for l in self.curs.fetchall()]
        except Exception as e:
            return None

    def getGameList(self):
        game_dict = dict()
        try:
            sql = "SELECT * FROM game WHERE 1;"
            self.curs.execute(sql)
            for row in self.curs.fetchall():
                game_dict[row[0]] = row[1:-1]
            #self.conn.close()
            return game_dict           
        except Exception as e:
            return None
    
    def getUserInfo(self, user_id):
        try:
            sql = "SELECT game_id, play_time FROM user WHERE user_id = %s;"
            self.curs.execute(sql, user_id)
            return [l[:2] for l in self.curs.fetchall()]
            self.conn.close()
        except Exception as e:
            return None

    def getTitles(self):
        try:
            sql = "SELECT title FROM game WHERE 1;"
            self.curs.execute(sql)
            return [l[0] for l in self.curs.fetchall() if l[0] is not None]
        except Exception as e:
            return None
    
    def getGameInfo(self, id):
        try:
            sql = "SELECT id, title, dev, url, released FROM game WHERE id = %s;"
            self.curs.execute(sql, id)
            return self.curs.fetchall()[0]
        except Exception as e:
            return None

    def getGameIdByTitle(self, title):
        try:
            sql = "SELECT id FROM game WHERE title = %s;"
            self.curs.execute(sql, title)
            #print(self.curs.fetchone())
            ret = self.curs.fetchone()[0]
            return ret
        except Exception as e:
            return None
            
    def getTags(self, game_id):
        try:
            sql = "SELECT tag FROM game_tag WHERE game_id = %s;"
            self.curs.execute(sql, game_id)
            return [l[:2][0] for l in self.curs.fetchall()]
        except Exception as e:
            
            return None
    def getGenre(self, game_id):
        try:
            sql = "SELECT genre FROM game_genre WHERE game_id = %s;"
            self.curs.execute(sql, game_id)
            return [l[:2][0] for l in self.curs.fetchall()]
        except Exception as e:
            return None

    def getAvgPlayTime(self, game_id):
        try:
            sql = "SELECT avg(play_time) FROM user WHERE game_id = %s AND play_time < 1000;"
            self.curs.execute(sql, game_id)
            ret = self.curs.fetchone()[0]
            return ret
        except Exception as e:
            return None
    def getTotalPlayTime(self, game_id):
        try:
            sql = "SELECT sum(play_time) FROM user WHERE game_id = %s AND play_time < 1000;"
            self.curs.execute(sql, game_id)
            ret = self.curs.fetchone()[0]
            return ret
        except Exception as e:
            return None
    def getDate(self, game_id):
        try:
            sql = "SELECT released FROM game WHERE id = %s;"
            self.curs.execute(sql, game_id)
            ret = self.curs.fetchone()[0]
            return ret
        except Exception as e:
            return None


import pymysql

if __name__ == "__main__":
    my_dbcon = MyDBController('127.0.0.1', 'guest', '0000', 'steam_db')
    #my_dbcon.insert('GAME', (2, "King of the god", "GOD", "www.kinggod.com", "2020-03-21"))
