#-*- coding: utf-8 -*-
import pymysql
from pandas.io.sql import read_sql
import pandas as pd
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

def gene_report(begin_time, end_time):
    conn = connect_sql()
    sql_text = "SELECT o.id,o.state,o.amount,o.category"
    sql_text +=" FROM `zzplatform`.`t_order` as o "
    sql_text += "WHERE o.createTime>'%s' and o.createTime<'%s';" % (begin_time, end_time)
    sql_text2 = "SELECT o.id, o.category,c.name"
    sql_text2 +=" FROM `zzplatform`.`t_order` as o "
    sql_text2 +="LEFT JOIN `zzplatform`.`t_md_city` as c on o.cityId = c.id "
    sql_text2 += "WHERE o.createTime>'%s' and o.createTime<'%s';" % (begin_time, end_time)

    try:
        df = pd.io.sql.read_sql(sql_text, con=conn)
        df_city = pd.io.sql.read_sql(sql_text2, con=conn)
    finally:
        conn.close()
    alist = ['complete','waitconfirm']
    res = {}
    res["end_time"] =end_time
    res["totle_order"] =   df['id'].count()
    res["totle_amount"] =   df['amount'].sum()
    res["tab_category"] = df.groupby(['category']).size()
    #order by category order by city 
    tab_tracery = df_city[df['category'].isin(['tracery'])]
    tab_tracery = tab_tracery.groupby(['name']).count().sort_values(by=['id'], ascending=False)[:5]
    res['tab_tracery'] = []
    for i in range(0, len(tab_tracery)):
        res['tab_tracery'].append({
            'city' : tab_tracery.index[i],
            'totle_order' : tab_tracery.ix[i]['id']
        })

    tab_bathroom = df_city[df['category'].isin(['bathroom'])]
    tab_bathroom = tab_bathroom.groupby(['name']).count().sort_values(by=['id'], ascending=False)[:5]
    res['tab_bathroom'] = []
    for i in range(0, len(tab_bathroom)):
        res['tab_bathroom'].append({
            'city' : tab_bathroom.index[i],
            'totle_order' : tab_bathroom.ix[i]['id']
        })

    tab_clotheshorse = df_city[df['category'].isin(['clotheshorse'])]
    tab_clotheshorse = tab_clotheshorse.groupby(['name']).count().sort_values(by=['id'], ascending=False)[:5]
    res['tab_clotheshorse'] = []
    for i in range(0, len(tab_clotheshorse)):
        res['tab_clotheshorse'].append({
            'city' : tab_clotheshorse.index[i],
            'totle_order' : tab_clotheshorse.ix[i]['id']
        })

    tab_doorsandwindows = df_city[df['category'].isin(['doorsandwindows'])]
    tab_doorsandwindows = tab_doorsandwindows.groupby(['name']).count().sort_values(by=['id'], ascending=False)[:5]
    res['tab_doorsandwindows'] = []
    for i in range(0, len(tab_doorsandwindows)):
        res['tab_doorsandwindows'].append({
            'city' : tab_doorsandwindows.index[i],
            'totle_order' : tab_doorsandwindows.ix[i]['id']
        })
    #that is for user 
    return res