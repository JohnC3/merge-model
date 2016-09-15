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

## Returns the table names from a connection in order.
def give_names(connection):
    df_tables = pd.read_sql_query('SELECT name FROM sqlite_master WHERE (type == "table")',connection)

    if 'date_names' in df_tables['name'].values:
        dates = pd.read_sql_query('SELECT date FROM date_names',connection)['date']

        dates = [i for i in dates]
         

    else:

        df_tables = df_tables[df_tables['name'].str.contains('Node') == True]

        dates = [i.replace('Node','') for i in df_tables['name']]

    return dates

## I decided to test if I could load everything into memory useing pandas. Yes.
def load_all_node_data():
    many_dfs = []
    for nodeTable in [i for i in df_tables['name']]:
        edgeTable = nodeTable.replace('Node','Eset')
        many_dfs.append([pd.read_sql_query('SELECT * FROM %s' % nodeTable,E2016),pd.read_sql_query('SELECT * FROM %s' % edgeTable,E2016)])
        print('%s: %s, %s' % (nodeTable,len(many_dfs[-1][0]),len(many_dfs[-1][1])))
    return many_dfs

## Follow a Id's node attributes through time.
def follow_Id(Id = '5428161003960189953',connection = Connery2016):
    Id_data = []
    dates = give_names(connection)
    print(dates[0])
    firstFact = pd.read_sql_query('SELECT * FROM %s WHERE Id = %s' % (dates[0]+'Node',Id),connection)
    for tab in dates[1:]:
        facts = pd.read_sql_query('SELECT * FROM %s WHERE Id = %s' % (tab+'Node',Id),connection)
        facts = pd.concat((firstFact,facts),axis = 0)
        
        fl = pd.read_sql_query('SELECT * FROM %s WHERE Source = %s OR Target = %s' % (tab+'Eset',Id,Id),connection)

        print(fl.Source[fl.Target == Id])
        print(fl.Target[fl.Source == Id])
        
        

            
        
        ##Id_data.append(pd.concat((facts,friends),axis = 1))
        firstFact = facts
    return facts

## Follow a Id's edges through time.
def follow_Id_EdgeVersion(Id = '5428161003960189953',connection = Connery2016):
    Id_data = []
    dates = give_names(connection)


##    firstfl = pd.read_sql_query('SELECT * FROM %s WHERE Source = %s OR Target = %s' % (dates[0]+'Eset',Id,Id),connection)
##    ## Get rid of the needless repitition of Id and make all edges go one direction.
##    firstfl.Source[firstfl.Source == Id] = firstfl.Target
##    firstfl.Target = Id
##    firstfl = firstfl.loc[:,['Source','Status']]
##
##    ## Rename the columns so we can append them together into one dataframe if we want.
##
##    firstfl.columns = [dates[0][-8:]+'friends','Status']
##
##    Id_data.append(firstfl)
    for tab in dates:

        ## Try Eset and e since its different depending on database ...
        try:
            fl = pd.read_sql_query('SELECT * FROM %s WHERE Source = %s OR Target = %s' % (tab+'Eset',Id,Id),connection)
        except:
            fl = pd.read_sql_query('SELECT * FROM %s WHERE Source = %s OR Target = %s' % (tab+'e',Id,Id),connection)
        
        ## Get rid of the needless repitition of Id and make all edges go one direction.
        fl.Source[fl.Source == Id] = fl.Target
        fl.Target = Id
        fl = fl.loc[:,['Source','Status']]
        fl2 = fl.drop_duplicates(['Source'], keep='last')

        print('%s: %s %s' % (tab[-8:],len(fl),len(fl2)))

        ## Rename the columns so we can append them together into one dataframe if we want.

        fl2.columns = [tab[-8:]+'friends','Status']
##        fl = pd.concat((fl,firstfl))
##        firstfl = fl
##        print(fl)
        Id_data.append(fl2)
     
    return Id_data

