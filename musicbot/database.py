from . import metaclasses
from . import exceptions
import pymysql.cursors
import pymysql
import random
import datetime

class DatabaseConnection(metaclass=metaclasses.Singleton):
    def __init__(self):
        self.connection = pymysql.connect(host='localhost', user='discord', password='skaianetlives', db='discord_bot', charset='utf8mb4', cursorclass=pymysql.cursors.DictCursor)
    def __del__(self):
        self.connection.close()
#    def test(self):
#        with self.connection.cursor() as cursor:
#            sql = "INSERT INTO `users` (`uid`, `coins`) VALUES (%s, %s)"
#            cursor.execute(sql, ('1239213123', str(30)))
#            self.connection.commit()
    def add_user(self, author):
        try:
            with self.connection.cursor() as cursor:
                sql = "INSERT INTO `users` (`uid`, `name`, `discriminator`, `coins`) VALUES (%s, %s, %s, %s) ON DUPLICATE KEY UPDATE `uid` = `uid`"
                cursor.execute(sql, (author.id, author.name, str(author.discriminator), str(0)))
                self.connection.commit()
        except Exception as e:
            raise exceptions.CommandError("An error occurred while accessing the database: %s" %e, expire_in=20)
        return

    def get_coins(self, author):
        try:
            with self.connection.cursor() as cursor:
                sql = "SELECT `coins` FROM `users` WHERE `uid` = %s"
                cursor.execute(sql, (author.id))
                result = cursor.fetchone()
                if result == None:
                    self.add_user(author)
                    return 0
                return result['coins']
        except Exception as e:
            raise exceptions.CommandError("An error occurred while accessing the database: %s" %e, expire_in=20)
        return -1

    def add_coins(self, author, amount):
        try:
            val = 0 if amount < 0 else amount
            with self.connection.cursor() as cursor:
                sql = "INSERT INTO `users` (`uid`, `name`, `discriminator`, `coins`) VALUES (%s, %s, %s, %s) ON DUPLICATE KEY UPDATE `coins` = `coins` + %s"
                cursor.execute(sql, (author.id, author.name, str(author.discriminator), str(val), str(amount)))
                self.connection.commit()
        except Exception as e:
            raise exceptions.CommandError("An error occurred while accessing the database: %s" %e, expire_in=20)
        return amount

    def payday(self, author):
        try:
            with self.connection.cursor() as cursor:
                sql = "SELECT `lastpayday` FROM `users` WHERE `uid` = %s"
                cursor.execute(sql, (author.id))
                result = cursor.fetchone()
                f = '%Y-%m-%d %H:%M:%S'
                if result['lastpayday'] == None:
                    amount = self.add_coins(author, random.randint(30, 100))
                    sql = "UPDATE `users` SET `lastpayday` = %s WHERE `uid` = %s"
                    cursor.execute(sql, (datetime.datetime.now().strftime(f), author.id))
                    self.connection.commit()
                    return amount
                else:
                    lastpd = result['lastpayday']
                    current = datetime.datetime.now()
                    difference = current - lastpd
                    if difference.days >= 1:
                        amount = self.add_coins(author, random.randint(30, 100))
                        sql = "UPDATE `users` SET `lastpayday` = %s WHERE `uid` = %s"
                        cursor.execute(sql, (current.strftime(f), author.id))
                        self.connection.commit()
                        return amount
                    else:
                        return -1
        except Exception as e:
            raise exceptions.CommandError("An error occurred while accessing the database: %s" %e, expire_in=20)
        return -1
