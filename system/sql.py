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

def gene_report(begin_time, end_time, report):
    res = {}
    res['end_time'] =  end_time
    res.update(worker_auditing(begin_time, end_time))
    res.update(order_log(begin_time, end_time))
    res.update(order_report(begin_time, end_time, report.report_type))
    res.update(user_report(begin_time, end_time))
    res.update(draw_cash_report(begin_time, end_time))
    
    try:
        report.totle_order = res['totle_order_true']
        report.totle_order_price = res['totle_amount']
        report.totle_new_user = res['totle_user']
        report.totle_order_tracery = res['tracery']['totle_order']
        report.totle_order_clotheshorse = res['clotheshorse']['totle_order']
        report.totle_order_bathroom = res['bathroom']['totle_order']
        report.totle_order_doorsandwindows = res['doorsandwindows']['totle_order']
        report.save()
        res['totle_order_true_compare'] = int((report.totle_order - report.ex_report.totle_order) * 100 / report.totle_order)
        res['totle_amount_compare'] = int((report.totle_order_price - report.ex_report.totle_order_price) * 100 / report.totle_order_price)
        res['totle_totle_user_compare'] = int((report.totle_new_user - report.ex_report.totle_new_user) * 100 / report.totle_new_user)
        res['totle_order_tracery_compare'] = int((report.totle_order_tracery - report.ex_report.totle_order_tracery) * 100 / report.totle_order_tracery)
        res['totle_order_clotheshorse_compare'] = int((report.totle_order_clotheshorse - report.ex_report.totle_order_clotheshorse) * 100 / report.totle_order_clotheshorse)
        res['totle_order_bathroom_compare'] = int((report.totle_order_bathroom - report.ex_report.totle_order_bathroom) * 100 / report.totle_order_bathroom)
        res['totle_order_doorsandwindows_compare'] = int((report.totle_order_doorsandwindows - report.ex_report.totle_order_doorsandwindows) * 100 / report.totle_order_doorsandwindows)
    except:
        #without ex report
        pass
    return res

def order_report(begin_time, end_time, report_type):
    conn = connect_sql()
    sql_text = "SELECT o.id,o.state,o.amount,o.category,c.name,o.role,o.createTime"
    sql_text +=" FROM `zzplatform`.`t_order` as o "
    sql_text +="LEFT JOIN `zzplatform`.`t_md_city` as c on o.cityId = c.id "
    sql_text += "WHERE o.createTime>'%s' and o.createTime<'%s';" % (begin_time, end_time)
    try:
        df = pd.io.sql.read_sql(sql_text, con=conn)
        file_name = "log/order_%s.xls" % begin_time
        df.to_excel(file_name,index=None, na_rep='None')
    finally:
        conn.close()

    res = {}
    res["totle_order"] =   df['id'].count()

    if report_type == 'W':
        res['report_type'] = u'周报告'
        order_state_filter = ['cancel']
    elif report_type == 'M':
        res['report_type'] = u'月报告'
        order_state_filter = ['cancel', 'none', 'securitydays','waitconfirm']
    elif report_type == 'Y':
        res['report_type'] = u'年报告'
        order_state_filter = ['cancel', 'none', 'securitydays','waitconfirm','securitydays']

    #filter the true order
    df = df[~df['state'].isin(order_state_filter)]
    res['totle_order_true'] =df['id'].count()
    res["totle_order_cancel"] = res["totle_order"] - res["totle_order_true"]
    res["totle_amount"] =  df['amount'].sum()
    res["tab_category"] = df.groupby(['category']).size().sort_values(ascending=False)
    res["tab_role"] = df.groupby(['role']).size()
    #order by category order by city
    res['tab_category_city'] = []
    for i in range(0, len(res["tab_category"])):
        #chose the order by category
        temp_tab = df[df['category'].isin([res["tab_category"].index[i]])]
        #only for compaire the pre_week/month report 
        category_name = res["tab_category"].index[i]
        res[category_name] ={
            'totle_order' : res["tab_category"][i],
            'totle_amount' : temp_tab['amount'].sum(),
        }
        res['tab_category_city'].append({
            'category' : res["tab_category"].index[i],
            'totle_order' : res["tab_category"][i],
            'totle_amount' : res[category_name]['totle_amount'],
            'price_pre_order': int(res[category_name]['totle_amount']/res["tab_category"][i]),
            "citys" : display_loop(temp_tab, groupby_name="name", number=5)[0]
        })

    #order by city order by category
    res['tab_city_category'] = []
    res["tab_city"] = df.groupby(['name']).size().sort_values(ascending=False)[:5]
    for i in range(0, len(res["tab_city"])):
        temp_tab = df[df['name'].isin([res["tab_city"].index[i]])]
        temp_amount = temp_tab['amount'].sum(),
        res['tab_city_category'].append({
            'city' : res["tab_city"].index[i],
            'totle_order' : res["tab_city"][i],
            'totle_amount' : temp_amount,
            'price_pre_order' : int(temp_amount/res["tab_city"][i]),
            "categorys" : display_loop(temp_tab, groupby_name="category")[0]
        })

    #order createTime is which weekday
    res['weekdays'] = [0]*7
    for item in df['createTime']:
        i = item.weekday()
        res['weekdays'][i] = res['weekdays'][i]+1

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
    temp_user_role_tab = df_user.groupby(['role']).size().sort_values(ascending=False)
    try:
        res['totle_user'] = temp_user_role_tab['person']
        res['tab_user_role'] = []
        temp_sum = 0
        for i in range(1, len(temp_user_role_tab)):
            temp_sum = temp_sum+temp_user_role_tab[i]
            res['tab_user_role'].append({
                'role' : temp_user_role_tab.index[i],
                'totle_user' : temp_user_role_tab[i],
                "percent" : str(int(float(temp_user_role_tab[i])/res['totle_user']*100)) + '%'
            })
        res['tab_user_role'].append({
                'role' : temp_user_role_tab.index[0],
                'totle_user' : res['totle_user'] - temp_sum,
                "percent" : str(int(float(res['totle_user'] - temp_sum)/res['totle_user']*100)) + '%'
            })
    except:
        #without new person
        res['totle_user'] = 0
    temp_user_source = df_user.groupby(['sourcePlatform']).size()
    temp_user_source_sum = df_user.groupby(['sourcePlatform']).sum()
    res["tab_user_source"] = display_loop(df_user, groupby_name="sourcePlatform")[0]
    tab_user_worker = df_user[df_user['role'].isin(['worker'])]
    res['tab_worker_state'] = tab_user_worker.groupby(['state']).size()
    res['user_city'] = display_loop(df_user, groupby_name="name", number=5)[0]
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
            res[i]['wait'] =  "%d天" % (arr[CREATE] - res[i]['w_date']).days
            res[i]['state'] = arr[NEW]
        elif arr[NEW] == 'sign':
            i = item.index(arr[ORDER_ID])
            res[i]['state'] = arr[NEW]
            res[i]['sign_date'] = arr[CREATE]
            if type(arr[PLAN]) == type(arr[CREATE]):
                res[i]['sign_rdv'] = "%d天" % (arr[CREATE] - arr[PLAN]).days
        elif arr[NEW] == 'waitconfirm':
            i = item.index(arr[ORDER_ID])
            res[i]['state'] = arr[NEW]
            res[i]['fini_sign'] = "%d天" % (arr[CREATE] - res[i]['sign_date']).days

    res_df = pd.DataFrame(res)
    file_name = "log/order_log_%s.csv" % begin_time
    res_df.to_csv(file_name,index=None, na_rep='None')
    res = {}
    res['wait_day'] = display_loop(res_df, groupby_name='wait')[0]
    res['sign_rdv'] = display_loop(res_df, groupby_name='sign_rdv')[0]
    res['fini_sign'] = display_loop(res_df, groupby_name='fini_sign')[0]
    return res

def draw_cash_report(begin_time, end_time):
    conn = connect_sql()
    sql_text = "SELECT id,bankname,accountname,amount,cityname "
    sql_text +="FROM `zzplatform`.`t_user_drawcash` "
    sql_text += "WHERE createdate>'%s' and createdate<'%s' " % (begin_time, end_time)
    sql_text +="and loan='debit' and role='worker' and type='drawcash'; "
    try:
        df = pd.io.sql.read_sql(sql_text, con=conn)
    finally:
        conn.close()
    res = {}
    res['draw_cash_sum'] =  df['amount'].sum()
    res['worker_bank'] = display_loop(df, groupby_name='bankname', number=5)[0]
    return res  

def worker_auditing(begin_time, end_time):
    conn = connect_sql()
    sql_text = "SELECT count(createdate),userid,createdate,state FROM `zzplatform`.`t_user_data` "
    sql_text +="WHERE createdate>'%s' and createdate<'%s' " % (begin_time, end_time)
    sql_text += "GROUP BY createdate;"
    print sql_text
    try:
        df = pd.io.sql.read_sql(sql_text, con=conn)
    finally:
        conn.close() 
   
    res = {}
    totle = 0
    for num in df['count(createdate)']:
        totle =  1 + totle
    res['auditing_num'] = totle
    if totle ==0:
        res['auditing_disabled'] = 0
    else:
        res['auditing_disabled'] = df.groupby('state').size()[0]
    return res

"""
dic-big is the table,
groupby_name is the categeory which you want to group,
number which you want to show the number of row in the result
"""
def display_loop(dic_big, groupby_name, number=0):
    res = []
    dic_small = dic_big.groupby([groupby_name]).count().sort_values(by=['id'], ascending=False)
    if number != 0:
        dic_small = dic_small[:number]
    temp_sum = dic_small['id'].sum()
    for i in range(0, len(dic_small)):
        res.append({
            'name' : dic_small.index[i],
            'totle' : dic_small.ix[i]['id'],
            "percent" : str(dic_small.ix[i]['id']*100/temp_sum) + '%'
        })
    return res, temp_sum
    