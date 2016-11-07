#-*- coding: utf-8 -*-
import pymysql
from pandas.io.sql import read_sql
import pandas as pd
import datetime
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
    res = {}
    #res.update(order_log(begin_time, end_time))
    res.update(order_report(begin_time, end_time))
    #res.update(user_report(begin_time, end_time))
    return res

def order_report(begin_time, end_time):
    conn = connect_sql()
    sql_text = "SELECT o.id,o.state,o.amount,o.category,c.name"
    sql_text +=" FROM `zzplatform`.`t_order` as o "
    sql_text +="LEFT JOIN `zzplatform`.`t_md_city` as c on o.cityId = c.id "
    sql_text += "WHERE o.createTime>'%s' and o.createTime<'%s';" % (begin_time, end_time)
    try:
        df = pd.io.sql.read_sql(sql_text, con=conn)
        #file_name = "log/order_%s.xls" % begin_time
        #df.to_excel(file_name,index=None, na_rep='None')
    finally:
        conn.close()

    res = {}
    res["totle_order"] =   df['id'].count()
    res["totle_order_cancel"] =   df[df['state'].isin(['cancel'])].count()['id']
    res["totle_amount"] =  df['amount'].sum() - df[df['state'].isin(['cancel'])]['amount'].sum()
    res["tab_category"] = df.groupby(['category']).size()
    #order by category order by city 
    tab_tracery = df[df['category'].isin(['tracery'])]
    tab_tracery = tab_tracery.groupby(['name']).count().sort_values(by=['id'], ascending=False)[:5]
    res['tab_tracery'] = []
    for i in range(0, len(tab_tracery)):
        res['tab_tracery'].append({
            'city' : tab_tracery.index[i],
            'totle_order' : tab_tracery.ix[i]['id']
        })

    tab_bathroom = df[df['category'].isin(['bathroom'])]
    tab_bathroom = tab_bathroom.groupby(['name']).count().sort_values(by=['id'], ascending=False)[:5]
    res['tab_bathroom'] = []
    for i in range(0, len(tab_bathroom)):
        res['tab_bathroom'].append({
            'city' : tab_bathroom.index[i],
            'totle_order' : tab_bathroom.ix[i]['id']
        })

    tab_clotheshorse = df[df['category'].isin(['clotheshorse'])]
    tab_clotheshorse = tab_clotheshorse.groupby(['name']).count().sort_values(by=['id'], ascending=False)[:5]
    res['tab_clotheshorse'] = []
    for i in range(0, len(tab_clotheshorse)):
        res['tab_clotheshorse'].append({
            'city' : tab_clotheshorse.index[i],
            'totle_order' : tab_clotheshorse.ix[i]['id']
        })

    tab_doorsandwindows = df[df['category'].isin(['doorsandwindows'])]
    tab_doorsandwindows = tab_doorsandwindows.groupby(['name']).count().sort_values(by=['id'], ascending=False)[:5]
    res['tab_doorsandwindows'] = []
    for i in range(0, len(tab_doorsandwindows)):
        res['tab_doorsandwindows'].append({
            'city' : tab_doorsandwindows.index[i],
            'totle_order' : tab_doorsandwindows.ix[i]['id']
        })

    return res

def user_report(begin_time, end_time):
    conn = connect_sql()
    sql_user = "SELECT tu.id,tu.state,tu.sourcePlatform,tc.name,tur.role"
    sql_user +=" FROM `zzplatform`.`t_user` as tu "
    sql_user +="LEFT JOIN `zzplatform`.`t_md_city` as tc on tc.id=tu.cityId "
    sql_user +="LEFT JOIN `zzplatform`.`t_user_role` as tur on tur.userid = tu.id "
    sql_user += "WHERE tu.regtime>'%s' and tu.regtime<'%s';" % (begin_time, end_time)

    try:
        df_user = pd.io.sql.read_sql(sql_user, con=conn)
        file_name = "log/user_%s.xls" % begin_time
        df_user.to_excel(file_name,index=None, na_rep='None')
    finally:
        conn.close()

    #that is for user
    res = {}
    res["new_user"] = df_user['id'].count()
    res["tab_user_role"] = df_user.groupby(['role']).size()
    res["tab_user_source"] = df_user.groupby(['sourcePlatform']).size()
    tab_user_worker = df_user[df_user['role'].isin(['worker'])]
    res['tab_worker_state'] = tab_user_worker.groupby(['state']).size()
    tab_user_city = df_user.groupby(['name']).count().sort_values(by=['id'], ascending=False)[:5]
    res['user_city'] = []
    for i in range(0, len(tab_user_city)):
        res['user_city'].append({
            'city' : tab_user_city.index[i],
            'totle_user' : tab_user_city.ix[i]['id']
        })
    return res

def order_log(begin_time, end_time):
    conn = connect_sql()
    sql_text = "SELECT ol.orderid,ol.oldstate,ol.newstate,ol.createdate,o.plandodate"
    sql_text +=" FROM `zzplatform`.`t_order_log` as ol "
    sql_text +="LEFT JOIN `zzplatform`.`t_order` as o on o.id=ol.orderid "
    sql_text += "WHERE o.createTime>'%s' and o.createTime<'%s';" % (begin_time, end_time)
    try:
        df = pd.io.sql.read_sql(sql_text, con=conn)
    finally:
        conn.close()
    
    ORDER_ID = 0
    OLD = 1
    NEW = 2
    CREATE = 3
    PLAN = 4
    res = []
    item = []
    for arr in df.values:
        if arr[ORDER_ID] not in item:
            if arr[OLD] == 'draft' and arr[NEW] == 'none':
                item.append(arr[ORDER_ID])
                res.append({
                    'id': arr[ORDER_ID],
                    'w_date':arr[CREATE],
                    'state': arr[NEW],
                    "wait":0,
                    "sign_rdv":0,
                    'fini_sign':0,
                })
        elif arr[NEW] =='running':
            i = item.index(arr[ORDER_ID])
            res[i]['wait'] =  (arr[CREATE] - res[i]['w_date']).days
            res[i]['state'] = arr[NEW]
        elif arr[NEW] == 'sign':
            i = item.index(arr[ORDER_ID])
            res[i]['state'] = arr[NEW]
            res[i]['sign_date'] = arr[CREATE]
            if type(arr[PLAN]) == type(arr[CREATE]):
                res[i]['sign_rdv'] = (arr[CREATE] - arr[PLAN]).days
        elif arr[NEW] == 'waitconfirm':
            i = item.index(arr[ORDER_ID])
            res[i]['state'] = arr[NEW]
            res[i]['fini_sign'] = (arr[CREATE] - res[i]['sign_date']).days

    res_df = pd.DataFrame(res)
    file_name = "log/order_log_%s.csv" % begin_time
    res_df.to_csv(file_name,index=None, na_rep='None')
    res = {}
    res['wait_day'] = []
    res['sign_rdv'] = []
    res['fini_sign'] = []
    res_wait = res_df.groupby('wait').size()
    res_sign_rdv = res_df.groupby('sign_rdv').size()
    res_fini_sign = res_df.groupby('fini_sign').size()
    for (key , value) in res_wait.iteritems():
        res['wait_day'].append({
            'day' : key,
            'count' : value,
            })
    for (key , value) in res_sign_rdv.iteritems():
        res['sign_rdv'].append({
            'day' : key,
            'count' : value,
            })
    for (key , value) in res_fini_sign.iteritems():
        res['fini_sign'].append({
            'day' : key,
            'count' : value,
            })
    return res