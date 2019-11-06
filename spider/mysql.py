import pymysql
from pymysql.cursors import DictCursor

"""
fix ModuleNotFoundError: No module named 'spider'
"""
import sys, os
sys.path.append(os.getcwd())

from spider.config import MYSQL_HOST, MYSQL_PORT, MYSQL_USER, MYSQL_PASS, MYSQL_DATABASE

"""
[pymysql doc](https://pymysql.readthedocs.io/en/latest/user/examples.html)
"""
class MySQL():
    def __init__(self, host=MYSQL_HOST, port=MYSQL_PORT, user=MYSQL_USER, password=MYSQL_PASS, database=MYSQL_DATABASE):
        try:
            """
            arguments:
            :param host: Host where the database server is located
            :param user: Username to log in as
            :param password: Password to use.
            :param database: Database to use, None to not use a particular one.
            :param port: MySQL port to use, default is usually OK. (default: 3306)
            :param charset: Charset you want to use.
            ......
            ......
            ......
            """
            self.connection = pymysql.connect(host, user, password, database, port, charset='utf8')
        except pymysql.MySQLError as e:
            print(e.args)
        # finally:
            # self.db.close()

    """INSERT
    arguments:
    :param table: mysql table name
    :param data: use dict data, dict.keys() corresponds to column and dict.values() corresponds to column's value
    """
    def insert(self, table, data):
        keys = ', '.join(data.keys())
        values = ', '.join(['%s'] * len(data))
        sql = 'insert into %s (%s) values (%s)' % (table, keys, values)
        try:
            with self.connection.cursor() as cursor:
                """
                :return: Number of affected rows
                """
                cursor.execute(sql, tuple(data.values()))
                self.connection.commit()
        except pymysql.MySQLError as e:
            print(e.args)

    """SELECT ALL
    """
    def select_all(self, table):
        try:
            """
            use param DictCursor make return dict data
            """
            with self.connection.cursor(DictCursor) as cursor:
                """
                :return: Number of affected rows
                """
                cursor.execute('select * from %s' % (table))
                return cursor.fetchall()
        except pymysql.MySQLError as e:
            print(e.args)

"""TEST SQL
CREATE DATABASE `spider-samples` CHARACTER SET 'utf8' COLLATE 'utf8_general_ci';

CREATE TABLE `users` (
    `id` int(11) NOT NULL AUTO_INCREMENT,
    `email` varchar(255) COLLATE utf8_bin NOT NULL,
    `password` varchar(255) COLLATE utf8_bin NOT NULL,
    PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8 COLLATE=utf8_bin
AUTO_INCREMENT=1 ;
"""
if __name__ == "__main__":
    mysql = MySQL()

    dict_data = {
        'email': 'gkd@gkd.net',
        'password': 'gkd'
    }

    mysql.insert('users', dict_data)

    rows = mysql.select_all('users')
    print(len(rows))