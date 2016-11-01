#-*- coding: utf-8 -*-
import pymysql
#from pandas.io.sql import read_sql
#import pandas as pd
import settings
def connect_sql():
    conn= pymysql.connect(
        host=settings.HOST,
        port=3306,
        user=settings.USER,
        passwd=settings.PASSWORD,
        db=settings.DB,
        charset="UTF8")
    return conn

"""
try:
    sql = "SELECT * FROM t_md_city"
    df = read_sql(sql, con=conn)
    writer = pd.ExcelWriter('/home/louis/python/output.xlsx')
    df.to_excel(writer,'Sheet1')
    writer.save()
finally:
    conn.close()

    with conn.cursor() as cursor:
        cursor.execute("SELECT * FROM t_md_city")
        res = cursor.fetchone()
        print (res)
"""