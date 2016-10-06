
from Merger_analysis_with_Pandas import *
from BA_algorithm import BA_evoloution,BA_evoloution_With_removal
import networkx as nx

## Simplist possiable model would be running BA model on both original networks


## Version one will simply start from the real networks.

EmeraldEngine = create_engine('sqlite:///E:\\Dropbox\\PS2Research\\SQL database\\Emerald.db')


def create_originals():
    ## Load the data

    matthersonEdges = pd.read_sql_query('SELECT Source,Target FROM matthersonJune23e',EmeraldEngine)

    mNodes = pd.read_sql_query('SELECT * FROM matthersonJune23',EmeraldEngine)

    watersonEdges = pd.read_sql_query('SELECT source,target FROM watersonJune23e',EmeraldEngine)

    wNodes = pd.read_sql_query('SELECT * FROM watersonJune23',EmeraldEngine)

    mF = dict(zip(mNodes.Id,mNodes.faction))

    wF = dict(zip(wNodes.Id,wNodes.faction))

    ## Create the graphs.

    M = nx.from_pandas_dataframe(matthersonEdges,'Source','Target')

    W = nx.from_pandas_dataframe(watersonEdges,'Source','Target')

    ## Set the faction and origin attribute
    nx.set_node_attributes(M,'faction',mF)

    nx.set_node_attributes(M,'origin','M')

    nx.set_node_attributes(W,'faction',wF)

    nx.set_node_attributes(W,'origin','W')

    return M,W

## Creates the inital state which the model will run on.
def initial_state(faction = '1'):
    ## Brings in the original separate networks.
    M,W = create_originals()
    ## The new combined network.
    G = nx.compose(M,W)

    if faction in ['1','2','3']:
        keep = []
        for n in G.nodes():
            try:
##                print(G.node[n])
                if G.node[n].get('faction') == faction:
                    keep.append(n)
            except KeyError:
                print(n)
        G = nx.Graph(G.subgraph(keep))
    return G

## MODULARITY NOW
from modularity import *

## This version simply applies the BA process to the network returning the graph after adding interval nodes.
def run_model_1_modularity(faction = '1',interval = 1000,repititions = 10,m = 6):
    folder = 'inteval = %s repititions = %s faction = %s, method is naive BA m = %s' %(interval,repititions,faction,m)
    directory = 'C:\\Users\\jscle\\Desktop\\itteration\\modularity\\'+folder


    
    if not os.path.exists(directory):
        os.makedirs(directory)
    else:
        directory = directory + '(1)'
        os.makedirs(directory)

    ## Open a file to record assortivity in
    f = open(directory+'\\modularity.txt','a')

    G = initial_state(faction)
    i = 0
    output = [modularity(nx.get_node_attributes(G,'origin'),G)]
    while(i < repititions):
        nx.write_graphml(G,directory+'\\BA model %s with N = %s and m = %s.graphml' % (i,len(G.nodes()),m))
        i = i+1
        G = BA_evoloution(G,len(G.nodes())+ interval,m,i)
        
        A = modularity(nx.get_node_attributes(G,'origin'),G)
        output.append(A)
        f.write('%s \n'%A)

    f.close()
                
    return output


## This version also applies the BA process to the network but also removes r nodes uniformly at random after each itteration.
def run_model_2_modularity(faction = '1',interval = 1000,repititions = 10,m = 6 , remove = 1000):
    folder = 'inteval = %s repititions = %s faction = %s, method is naive BA with m = %s and removal = %s' %(interval,repititions,faction,m,remove)
    directory = 'C:\\Users\\jscle\\Desktop\\itteration\\modularity\\'+folder


    while(os.path.exists(directory)):
        directory = directory + '(1)'
    if not os.path.exists(directory):
        os.makedirs(directory)


    ## Open a file to record assortivity in
    f = open(directory+'\\modularity.txt','a')

    G = initial_state(faction)

    N = len(G.nodes())
    iterSymbol = 'abcdefghijklmnopqrstuvwxyz1234567890!@#$%^&*()-_=+'
    i = 0
    output = [modularity(nx.get_node_attributes(G,'origin'),G)]
    while(i < repititions):
        nx.write_graphml(G,directory+'\\BA model %s with N = %s and m = %s.graphml' % (i,len(G.nodes()),m))
        i = i+1
        G = BA_evoloution_With_removal(G,N + 1000, m,remove,seed = i,iteration_symbol = iterSymbol[i])

        A = modularity(nx.get_node_attributes(G,'origin'),G)

        output.append(A)
        f.write('%s \n'%A)

    f.close()
                
    return output
##
##print('Model 1')
##print(run_model_1_modularity('1',1000,30,2))
##print(run_model_1_modularity('1',1000,30,3))
##print(run_model_1_modularity('1',1000,30,4))
##print(run_model_1_modularity('1',1000,30,5))
##print(run_model_1_modularity('1',1000,30,6))

print('Model 2 with removal') 
print(run_model_2_modularity(m = 2,repititions = 30))
print(run_model_2_modularity(m = 3,repititions = 30))
print(run_model_2_modularity(m = 4,repititions = 30))
print(run_model_2_modularity(m = 5,repititions = 30))
print(run_model_2_modularity(m = 6,repititions = 30))









