
from Merger_analysis_with_Pandas import *
from BA_algorithm import BA_evoloution
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

## This version simply applies the BA process to the network returning the graph after adding interval nodes.
def run_assortivity(faction = '1',interval = 1000,repititions = 10,m = 6):
    folder = 'inteval = %s repititions = %s faction = %s, method is naive BA m = %s' %(interval,repititions,faction,m)
    directory = 'C:\\Users\\jscle\\Desktop\\itteration\\'+folder


    
    if not os.path.exists(directory):
        os.makedirs(directory)
    else:
        directory = directory + '(1)'
        os.makedirs(directory)

    ## Open a file to record assortivity in
    f = open(directory+'\\assortivity.txt','a')

    G = initial_state(faction)
    i = 0
    assor = [nx.assortativity.attribute_assortativity_coefficient(G,'origin')]
    while(i < repititions):
        nx.write_graphml(G,directory+'\\BA model %s with N = %s and m = %s.graphml' % (i,len(G.nodes()),m))
        i = i+1
        G = BA_evoloution(G,len(G.nodes())+ interval,m,i)

        A = nx.assortativity.attribute_assortativity_coefficient(G,'origin')
        assor.append(A)
        f.write('%s \n'%A)

    f.close()
                
    return assor



x = run_assortivity()
