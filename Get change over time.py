## Find how many avatars are removed/added every week.
## Find how many edges are removed/added every week
## and catagorize by newcomer edge vs returning avatar edge

from Merger_analysis_with_Pandas import *
import networkx as nx
import time


EmeraldEngine = create_engine('sqlite:///E:\\Dropbox\\PS2Research\\SQL database\\Emerald.db')

## Every table in the Emerald database (I think)
real = ['June30',
        'July14', 'July22', 'July29',
        'Aug4','Aug11', 'Aug18', 'Aug25',
        'Sept1', 'Sept9','Sept15', 'Sept22',
        'Oct1', 'Oct7', 'Oct13','Oct20','Oct27',
        'Nov3', 'Nov12', 'Nov17', 'Nov26', 
        'Dec1', 'Dec17','Dec28',
        'Jan2', 'Jan10', 'Jan18', 'Jan26', 'Jan31',
        'Feb8', 'Feb15', 'Feb23',
        'Mar1',
        'Mar26_16', 'Apr2_16']

'watersonJune15'

'watersonMay18'

def build_list_of_MandW_nodes():
    start_time = time.time()
    mNodes = [i for i in pd.read_sql_query('SELECT Id FROM matthersonJune23',EmeraldEngine).Id]
    mNodes = mNodes + [i for i in pd.read_sql_query('SELECT Id FROM matthersonJune15',EmeraldEngine).Id]
    mNodes = mNodes + [i for i in pd.read_sql_query('SELECT Id FROM matthersonMay18',EmeraldEngine).Id]

    mNodes = list(set(mNodes))
    
    wNodes = [i for i in pd.read_sql_query('SELECT Id FROM watersonJune23',EmeraldEngine).Id]
    wNodes = wNodes + [i for i in pd.read_sql_query('SELECT Id FROM watersonJune15',EmeraldEngine).Id]
    wNodes = wNodes + [i for i in pd.read_sql_query('SELECT Id FROM watersonMay18',EmeraldEngine).Id]

    wNodes = list(set(wNodes))
    print("--- %s seconds --- to M and W" % (time.time() - start_time))
    return mNodes,wNodes



## Build or load a graph from each snapshot of the merger.
def makeGraphs():
    graphs = []
    
    for date in real:

        G = getGraph(date)

        graphs.append([date,G])

    return graphs

def getGraph(date,runtime=False):
    try:
        start_time = time.time()
        G = nx.read_graphml('C:\\Users\\jscle\\merger analysis\\merge-model\\graphs\\%s.gramphml'% date)

        if(runtime == True):
            print("--- %0.4f seconds --- to load %s" % ((time.time() - start_time),date))
        
    except:
        
        mNodes,wNodes = build_list_of_MandW_nodes()
        
        print('building %s' % date)
        start_time = time.time()
        edges = pd.read_sql_query('SELECT Source,Target FROM %se' % date,EmeraldEngine)

        G = nx.from_pandas_dataframe(edges,'Source','Target')

        ##Set each nodes faction to the value found in the database        

        faction = pd.read_sql_query('SELECT Id,Faction FROM %s' %date,EmeraldEngine)

        F = dict(zip(faction.Id,faction.faction))

        faction_errors = 0
        for n in G.nodes():
            try:
                G.node[n]['faction'] = F[n]
            except:
                faction_errors += 1
                G.node[n]['faction'] = 'Err'
                
        print('Faction errors %s' % faction_errors)

        ## Set each nodes origin based on the server it came from
                    
        nx.set_node_attributes(G,'WorM','N')
        
        for n in mNodes:
            if n in G:
                G.node[n]['WorM'] = 'M'
        for n in wNodes:
            if n in G:
                G.node[n]['WorM'] = 'W'

        for n in G.nodes():
            G.node[n]['origin'] = G.node[n]['WorM'] + G.node[n]['faction']

        nx.write_graphml(G,'C:\\Users\\jscle\\merger analysis\\merge-model\\graphs\\%s.gramphml'% date)
        print("--- %s seconds --- to build" % (time.time() - start_time))
    return G



## Break the graphs up into subgraphs.
def break_to_subgraphs(G):
    ' returns G,nc,tr,vs,original_only subgraphs and noFaction'
    faction_breakdown = {'TR':[],'VS':[],'NC':[],'original':[]}

    ## Count nodes missing a faction       
    noFaction = [];
    
    for n in G.nodes():
        if (G.node[n]['WorM'] in ['M','W']):
            faction_breakdown['original'].append(n)
        try:
            faction_breakdown[G.node[n]['faction']].append(n)
        except KeyError:
            noFaction.append(n)

    ## Remove the faction less nodes.
    G.remove_nodes_from(noFaction)

    original_only = nx.Graph(G.subgraph(faction_breakdown['original']))

    nc,tr,vs = nx.Graph(G.subgraph(faction_breakdown['NC'])),nx.Graph(G.subgraph(faction_breakdown['TR'])),nx.Graph(G.subgraph(faction_breakdown['VS']))

    nc_O = nx.Graph(nc.subgraph([i for i in nc.nodes() if nc.node[i]['origin'] in ['WNC','MNC']]))

    tr_O = nx.Graph(tr.subgraph([i for i in tr.nodes() if tr.node[i]['origin'] in ['WTR','MTR']]))

    vs_O = nx.Graph(vs.subgraph([i for i in vs.nodes() if vs.node[i]['origin'] in ['WVS','MVS']]))

    return G,original_only,nc,tr,vs,nc_O,tr_O,vs_O,noFaction



## Compute the origin assortivity of each faction individually and all factions together
def assortivity():
    
    print('Date,ALL,All Original only,NC,TR,VS,NC originals only,TR originals only,VS originals only,noFaction')
    for name in real:

        G = getGraph(name)

        G,original_only,nc,tr,vs,nc_O,tr_O,vs_O,noFaction = break_to_subgraphs(G)

        All = nx.assortativity.attribute_assortativity_coefficient(G,'origin')

        O = nx.assortativity.attribute_assortativity_coefficient(original_only,'origin')

        NC = nx.assortativity.attribute_assortativity_coefficient(nc,'origin')

        TR = nx.assortativity.attribute_assortativity_coefficient(tr,'origin')

        VS = nx.assortativity.attribute_assortativity_coefficient(vs,'origin')

        


        NC_O = nx.assortativity.attribute_assortativity_coefficient(nc_O,'origin')

        TR_O = nx.assortativity.attribute_assortativity_coefficient(tr_O,'origin')

        VS_O = nx.assortativity.attribute_assortativity_coefficient(vs_O,'origin')

        

        print('%s 2014,%s,%s,%s,%s,%s,%s,%s,%s,%s' % (name,All,O,NC,TR,VS,NC_O,TR_O,VS_O,len(noFaction)))
        




def modularity(partition, graph, weight='weight'):
    """Compute the modularity of a partition of a graph

    Parameters
    ----------
    partition : dict
       the partition of the nodes, i.e a dictionary where keys are their nodes
       and values the communities
    graph : networkx.Graph
       the networkx graph which is decomposed
    weight : str, optional
        the key in graph to use as weight. Default to 'weight'


    Returns
    -------
    modularity : float
       The modularity

    Raises
    ------
    KeyError
       If the partition is not a partition of all graph nodes
    ValueError
        If the graph has no link
    TypeError
        If graph is not a networkx.Graph

    References
    ----------
    .. 1. Newman, M.E.J. & Girvan, M. Finding and evaluating community
    structure in networks. Physical Review E 69, 26113(2004).

    Examples
    --------
    >>> G=nx.erdos_renyi_graph(100, 0.01)
    >>> part = best_partition(G)
    >>> modularity(part, G)
    """
    if type(graph) != nx.Graph:
        raise TypeError("Bad graph type, use only non directed graph")

    inc = dict([])
    deg = dict([])
    links = graph.size(weight=weight)
    if links == 0:
        raise ValueError("A graph without link has an undefined modularity")

    for node in graph:
        com = partition[node]
        deg[com] = deg.get(com, 0.) + graph.degree(node, weight=weight)

        ## Iterate through the edges, attributes of each node.
        for neighbor, datas in graph[node].items():
            edge_weight = datas.get(weight, 1)
            # If the neighbour is in the same community
            if partition[neighbor] == com:
                if neighbor == node:
                    inc[com] = inc.get(com, 0.) + float(edge_weight)
                else:
                    inc[com] = inc.get(com, 0.) + float(edge_weight) / 2.

    res = 0.
    for com in set(partition.values()):
        res += (inc.get(com, 0.) / links) - \
               (deg.get(com, 0.) / (2. * links)) ** 2
    return res






def look_modularity():
    print('Date,ALL,All Original only,NC,TR,VS,NC originals only,TR originals only,VS originals only,noFaction')
    
    for name in real:
        G = getGraph(name);

        G,original_only,nc,tr,vs,nc_O,tr_O,vs_O,noFaction = break_to_subgraphs(G)

        All = modularity(nx.get_node_attributes(G,'origin'),G)

        O = modularity(nx.get_node_attributes(original_only,'origin'),original_only)

        NC = modularity(nx.get_node_attributes(nc,'origin'),nc)

        TR = modularity(nx.get_node_attributes(tr,'origin'),tr)

        VS = modularity(nx.get_node_attributes(vs,'origin'),vs)

        


        NC_O = modularity(nx.get_node_attributes(nc_O,'origin'),nc_O)

        TR_O = modularity(nx.get_node_attributes(tr_O,'origin'),tr_O)

        VS_O = modularity(nx.get_node_attributes(vs_O,'origin'),vs_O)

        print('%s 2014,%s,%s,%s,%s,%s,%s,%s,%s,%s' % (name,All,O,NC,TR,VS,NC_O,TR_O,VS_O,len(noFaction)))

look_modularity()
