## Find how many avatars are removed/added every week.
## Find how many edges are removed/added every week
## and catagorize by newcomer edge vs returning avatar edge

from Merger_analysis_with_Pandas import *
import networkx as nx
import time


EmeraldEngine = create_engine('sqlite:///E:\\Dropbox\\PS2Research\\SQL database\\Emerald.db')

## Every table in the Emerald database (I think)

'watersonJune15'

'watersonMay18'

'matthersonJune23'

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

def build_list_of_MandW_edges():
    start_time = time.time()
    mEdges = set()
    for name in ['matthersonJune23e','matthersonJune15e','matthersonMay18e']:
        df = pd.read_sql_query('SELECT Source,Target FROM %s' %name,EmeraldEngine)
        for i,j in zip(df.Source,df.Target):
            mEdges.add(','.join(sorted([i,j])))

    wEdges = set()
    for name in ['watersonJune23e','watersonJune15e','watersonMay18e']:
        df = pd.read_sql_query('SELECT Source,Target FROM %s' %name,EmeraldEngine)
        for i,j in zip(df.Source,df.Target):
            wEdges.add(','.join(sorted([i,j])))
    
    print("--- %s seconds --- to M and W" % (time.time() - start_time))
    return mEdges,wEdges

## Build or load a graph from each snapshot of the merger.
def makeGraphs():
    graphs = []
    
    for date in real:

        G = getGraph(date)

        graphs.append([date,G])

    return graphs

def getGraph(date,runtime=False,lite = False):
    if lite:
        if date in ['Apr2_16','Mar26_16']:
            edges = pd.read_sql_query('SELECT Source,Target FROM %se where Status = "normal"' % date,EmeraldEngine)
        else:
            edges = pd.read_sql_query('SELECT Source,Target FROM %se' % date,EmeraldEngine)
        G = nx.from_pandas_dataframe(edges,'Source','Target')

    else:
        try:
            start_time = time.time()
            G = nx.read_graphml('C:\\Users\\jscle\\merger analysis\\merge-model\\graphs\\%s.gramphml'% date)

            if(runtime == True):
                print("--- %0.4f seconds --- to load %s" % ((time.time() - start_time),date))
            
        except:
            
            mNodes,wNodes = build_list_of_MandW_nodes()
            
            print('building %s' % date)
            start_time = time.time()
            if date in ['Apr2_16','Mar26_16']:
                edges = pd.read_sql_query('SELECT Source,Target FROM %se where Status = "normal"' % date,EmeraldEngine)
            else:
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
        


from modularity import *

## 
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


## Explore the change in the node set over time first by finding the everyone who leaves and everyone who joins

def node_dynamics():
    L = getGraph(real[0])

    ## Store all nodes removed so far.
    
    removal_record = set()
    
    ## All the old mattherson and waterson nodes.

    m,w = build_list_of_MandW_nodes()

    removal_record = set(m).union(set(w)) - set(L.nodes())      

    ## Values for spreadsheet CP = current population, R = Leavers, PC = potentially cutoff
    CP = len(list(set(L.nodes())))
    R = 0
    PC = 0
    ## more values N = Joiners, B returned from inactivity'
    N = 0
    B = 0
    
    print('Date, Current population, Leavers, potentially cutoff, Joiners, returned from inactivity')

    print('%s,%s,%s,%s,%s,%s' % (real[0],CP,R,PC,N,B))
   
    for name in real[1:]:
     
        G = getGraph(name,lite=True);

        L_ids = set(L.nodes())

        G_ids = set(G.nodes())

        CP = len(G_ids)

        ## The symetric difference returns all Ids in G but not in L and all Ids in L but not in G
        difference = L_ids.symmetric_difference(G_ids)

        removed = difference.intersection(L_ids)

        added = difference.intersection(G_ids)

        R = len(removed)

        ## to look at PC we need to examine every removed node and check if they are
        ## removed because they quit or removed because they have no neighbours left
        ## If any neighbour in the current graph still exists they don't get set as PC

        PC = 0
      
        for n in removed:
            ## cutoff_flag starts true but returns False if it is in fact cut off.

            cutoff_flag = True
            
            neig = set(L[n].keys())

            for node in neig:
                if node in G_ids:
                    cutoff_flag = False
                    break

            if cutoff_flag:
                PC+=1
                       
        N = len(added)

        B = len(added.intersection(removal_record))

        ## Update the removal record with all removed nodes.
        removal_record = removal_record.union(removed)

        ## Print the results.
        print('%s,%s,%s,%s,%s,%s' % (name,CP,R,PC,N,B))

        ## Set the new L to be G so the process can continue
        
        L = G

## Get new dead and new_dead

def other_node_dynamics():

    print('Date,new,dead,new_dead')

    new = 0
    dead = 0
    new_dead = 0

    print('%s,%s,%s,%s' %(real[0],new,dead,new_dead))
    
    for name in real[1:]:
        try:
            new = len(set([i for i in pd.read_sql_query('SELECT Id FROM %s where status3 = "new"' % name,EmeraldEngine).Id]))
            
            dead = len(set([i for i in pd.read_sql_query('SELECT Id FROM %s where status3 = "dead" ' % name,EmeraldEngine).Id]))

            new_dead = len(set([i for i in pd.read_sql_query('SELECT Id FROM %s where status3 = "new_dead" ' % name,EmeraldEngine).Id]))

            
        except:
            new,dead,new_dead = 0,0,0

        print('%s,%s,%s,%s' %(name,new,dead,new_dead))
        
##other_node_dynamics()

## Edge dynamics:

## Count the number of edges added or removed.

def edge_dynamics():
    L = getGraph(real[0],lite=True);

    ## Store all edges removed so far.

    removal_record = set()

    ## Include the prexisting edges from M and W

    m,w = build_list_of_MandW_edges()

    removal_record = set(m).union(set(w)) - set(L.nodes())   

    ## Values for spreadsheet CP = current population, R = Removed edges, PC = potentially cutoff edges
    CP = len(set([','.join(sorted(x)) for x in L.edges()]))
    R = 0
    PC = 0
    ## more values N = Created edges, B Edges returned from inactivity'
    N = 0
    B = 0
    
    print('Date, Current edge count, Removed edges, potentially cutoff edges, Created edges, Edges returned from inactivity')

    print('%s,%s,%s,%s,%s,%s' % (real[0],CP,R,PC,N,B))
   
    for name in real[1:]:
     
        G = getGraph(name,lite=True);

        ## For the sake of sanity every edge is going to be stored as a string joined by a comma with the Ids in ascending order.

        L_edges = set([','.join(sorted(x)) for x in L.edges()])

        G_edges = set([','.join(sorted(x)) for x in G.edges()])

        ## Current edge count.
        
        CP = len(G_edges)

        ## The symetric difference returns all Ids in G but not in L and all Ids in L but not in G
        difference = L_edges.symmetric_difference(G_edges)

        ## 

        removed = difference.intersection(L_edges)

        added = difference.intersection(G_edges)

        R = len(removed)

        ## to look at PC we need to examine every removed node and check if they are
        ## removed because they quit or removed because they have no neighbours left
        ## If any neighbour of both endpoints of a edge in the current graph still exists they don't get set as PC

        PC = 0

        ## Need G_ids to test for cutoff edges!

        G_ids = set(G.nodes())
        
        for e in removed:

            ## cutoff_flag starts true but returns False if it is in fact cut off.

            cutoff_flag = True

            for n in e.split(','):
            
                neig = set(L[n].keys())

                for node in neig:
                    if node in G_ids:
                        cutoff_flag = False
                        break

            if cutoff_flag:
                PC+=1
                       
        N = len(added)

        B = len(added.intersection(removal_record))

        ## Update the removal record with all removed nodes.
        removal_record = removal_record.union(removed)

        ## Print the results.
        print('%s,%s,%s,%s,%s,%s' % (name,CP,R,PC,N,B))

        ## Set the new L to be G so the process can continue
        
        L = G



## How many nodes have completely stable edge sets?

## How many triads are closed when a edge is added?

## How many triangles does each new node create?

def other_edge_dynamics():
    L = getGraph(real[0],lite=True);

    ## Store all edges removed so far.

    removal_record = set()

    ## Include the prexisting edges from M and W

    m,w = build_list_of_MandW_edges()

    removal_record = set(m).union(set(w)) - set(L.nodes())   

    ## Values for spreadsheet SN = Stable neighbourhood, CP = number of nodes in both L and G
    SN = 0
    CP = 0
    ## TC = Triads closed,TO = Triads openend, NP_TRI = triangles created by a new characters return.current population
    TC = 0
    TO = 0
    NP_TRI = 0
    
    print('Date,Nodes in both, Stable neighbourhood, Triads closed,Triads openend, triangles created by a new')

    print('%s,%s,%s,%s,%s,%s' % (real[0],CP,SN,TC,TO,NP_TRI))
   
    for name in real[1:]:
     
        G = getGraph(name,lite=True);

        ## For the sake of sanity every edge is going to be stored as a string joined by a comma with the Ids in ascending order.

        L_edges = set([','.join(sorted(x)) for x in L.edges()])

        G_edges = set([','.join(sorted(x)) for x in G.edges()])

        ## The symetric difference returns all Ids in G but not in L and all Ids in L but not in G
        difference = L_edges.symmetric_difference(G_edges)

        ## 

        removed = difference.intersection(L_edges)

        added = difference.intersection(G_edges)

        ## Triads closed is the number of mutual neighbours of the pair as they were connected by a new edge.

        TC = 0
        for e in added:
            a,b = e.split(',')
            neigA = set(G[a].keys())

            neigB = set(G[b].keys())

            TC += len(neigA.intersection(neigB))

        ## Triads opened is just the opposite.

        TO = 0
        for e in removed:
            a,b = e.split(',')
            neigA = set(L[a].keys())

            neigB = set(L[b].keys())

            TO += len(neigA.intersection(neigB))
        
        ## Stable neighbourhood is a count of all nodes whoes friendslist did not change.

        SN = 0

        ## The nodes in both G and L are the nodes that can have a stable neighbourhood.

        common_L_G_nodes = set(G.nodes()).intersection(set(L.nodes()))

        CP = len(common_L_G_nodes)

        for n in common_L_G_nodes:
            neigInG = set(G[n].keys())

            neigInL = set(L[n].keys())
            if (len(neigInG.symmetric_difference(neigInL)) == 0):
                SN += 1

        ## NP_TRI the number of triangles created by newcomer nodes
        NP_TRI = 0

        for e in added - removal_record:
            a,b = e.split(',')

            neigA = set(G[a].keys())

            neigB = set(G[b].keys())

            NP_TRI += len(neigA.intersection(neigB))

        ## Update the removal record with all removed nodes.
        removal_record = removal_record.union(removed)
      
        ## Print the results.

        print('%s,%s,%s,%s,%s,%s' % (name,CP,SN,TC,TO,NP_TRI))
        
        ## Set the new L to be G so the process can continue
        
        L = G

##other_edge_dynamics()


