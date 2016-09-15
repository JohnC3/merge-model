
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


G = initial_state()

G2 = BA_evoloution(G,len(G.nodes())+ 1000,5,1111)

