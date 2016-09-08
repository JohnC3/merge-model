import pandas as pd
import numpy as np
import sqlite3
import os
import sklearn.cluster as cl
from sqlalchemy import create_engine # database connection


p = 'E:\\Dropbox\\PS2Research\\SQL database\\'

#The first three databases connect to all nodes active in the last 44 days of nodes. The second three are the subset of nodes active in since the last check.
Connery = sqlite3.connect(p+'Connery.db')
Emerald = sqlite3.connect(p+'Emerald.db')
Miller = sqlite3.connect(p+'Miller.db')

CW = sqlite3.connect(p+'ConneryWeek.db')
MW = sqlite3.connect(p+'MillerWeek.db')
EW = sqlite3.connect(p+'EmeraldWeek.db')

Emerald2016 = sqlite3.connect('E:\\Dropbox\\PS2Research\\2016Data\\Emerald.db')
Connery2016 = sqlite3.connect('E:\\Dropbox\\PS2Research\\2016Data\\Connery.db')
Miller2016 = sqlite3.connect('E:\\Dropbox\\PS2Research\\2016Data\\Miller.db')

C2 = create_engine('sqlite:///'+p+'Connery.db')

E2016 = create_engine('sqlite:///E:\\Dropbox\\PS2Research\\2016Data\\Emerald.db')


df_tables = pd.read_sql_query('SELECT name FROM sqlite_master WHERE (type == "table")',E2016)

df_tables = df_tables[df_tables['name'].str.contains('Node') == True]

dates = [i.replace('Node','') for i in df_tables['name']]


## I decided to test if I could load everything into memory useing pandas. Yes.
def load_all_node_data():
    many_dfs = []
    for nodeTable in [i for i in df_tables['name']]:
        edgeTable = nodeTable.replace('Node','Eset')
        many_dfs.append([pd.read_sql_query('SELECT * FROM %s' % nodeTable,E2016),pd.read_sql_query('SELECT * FROM %s' % edgeTable,E2016)])
        print('%s: %s, %s' % (nodeTable,len(many_dfs[-1][0]),len(many_dfs[-1][1])))
    return many_dfs








