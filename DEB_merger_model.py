
from Merger_analysis_with_Pandas import *
from modularity import *
import networkx as nx
import random as rand

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

## This model is based on the simple network evoloution model presented in:
## "Emergence of a Small World from Local Interactions: Modeling Acquaintance Networks"
## By Jörn Davidsen, Holger Ebel, and Stefan Bornholdt* or DEB for short.

class DEB:
    ## The seed graph is taken to iterate on.
    def __init__(self,p,faction = '1',seed_graph = None):
        if seed_graph == None:
            self.G = initial_state(faction = '1')
        else:
            self.G = seed_graph
        self.p = p
        self.N = self.G.nodes()
        self.removed_nodes = 0
        self.removed_edges = 0
        self.edges_added = 0

    ## Run through the algorithm once.
    def go(self):
        G = self.G
        ## Pick a node at random.
        n = rand.sample(self.N,1)[0]

        ## Get neighbours of that node if possiable choose a pair of friends at random
        ## and add a edge between them
        neig = nx.neighbors(G,n)
        if len(neig) > 1:
            samp = rand.sample(neig,2)
            G.add_edge(samp[0],samp[1])
        # If we have only one friend
        elif len(neig) == 1:
            #Pick another at random and make a triangle out of it
            v = rand.sample(self.N,1)[0]
            G.add_edge(n,v)
            G.add_edge(neig[0],v)
        
        self.edges_added += 1

        #Pick a node and with probability p remove it.
        doomed = rand.sample(self.N,1)[0]
        if rand.uniform(0,1) < self.p:

            self.removed_edges += len(G[doomed])
            
            G.remove_node(doomed)

            ## Randomly reatach the removed node somewhere in the graph.            
            v = rand.sample(self.N,1)[0]

            G.add_edge(v,doomed)
            
            self.edges_added += 1

            ## Set the status of the reatached node to be new

            G.node[doomed]['origin'] = 'N'

            ## Incrament removed nodes count
            self.removed_nodes += 1

        self.G = G

    ## Run through the function
    

    
    ## Run the program and record results as you go,
    ## If stopping condition is true run the program the program and record results as you but stop only after 200000 nodes have been removed,
        
    def run(self,repititions = 30000,interval = 1000,stopping = False):
        folder = 'DEB model with p = %s' % self.p
        directory = 'C:\\Users\\jscle\\Desktop\\itteration\\'+folder


        while(os.path.exists(directory)):
            directory = directory + '(1)'
        if not os.path.exists(directory):
            os.makedirs(directory)


        ## Open a file to record assortivity in
        f = open(directory+'\\assortivity and modularity results.txt','a')
        f.write('repititions,Assortivity,Modularity,removed nodes,edges added,edges removed,new count, M count. W count \n')

        ## Initialize the assortivity and modularity.
        Assor = [nx.assortativity.attribute_assortativity_coefficient(self.G,'origin')]
        Mod = [modularity(nx.get_node_attributes(self.G,'origin'),self.G)]

        ## when i == interval record stuff, while j is less then repititions repeat.
        i = 0
        j = 0

        if stopping:
            while(self.removed_nodes < 200000):
                ## Run the function once
                self.go()

                if(i == interval):
                    i = 0
                    M = modularity(nx.get_node_attributes(self.G,'origin'),self.G)
                    A = nx.assortativity.attribute_assortativity_coefficient(self.G,'origin')

                    Assor.append(A)
                    Mod.append(M)
                    
                    nx.write_graphml(self.G,directory+'\\DEB p = %s itterations = %s stopping true.graphml' % (self.p,j))

                    ## Count up the number of M, W and N nodes currently found in the network.

                    Mn = len([i for i in self.G.nodes() if self.G.node[i]['origin'] == 'M'])
                    Wn = len([i for i in self.G.nodes() if self.G.node[i]['origin'] == 'W'])
                    Nn = len([i for i in self.G.nodes() if self.G.node[i]['origin'] == 'N'])

                    f.write('%s, %s, %s ,%s ,%s ,%s ,%s\n'% (j,A,M,self.removed_nodes,self.edges_added,self.removed_edges,Nn,Mn,Wn))

                    print('%s, %s, %s ,%s ,%s ,%s ,%s'% (j,A,M,self.removed_nodes,self.edges_added,self.removed_edges,Nn,Mn,Wn))


                    
                i += 1
                j += 1
                


        else:
        
            while(j < repititions):
                ## Run the function once
                self.go()

                if(i == interval):
                    i = 0
                    M = modularity(nx.get_node_attributes(self.G,'origin'),self.G)
                    A = nx.assortativity.attribute_assortativity_coefficient(self.G,'origin')

                    Assor.append(A)
                    Mod.append(M)
                    
                    nx.write_graphml(self.G,directory+'\\DEB p = %s itterations = %s.graphml' % (self.p,j))

                    ## Count up the number of M, W and N nodes currently found in the network.

                    Mn = len([i for i in self.G.nodes() if self.G.node[i]['origin'] == 'M'])
                    Wn = len([i for i in self.G.nodes() if self.G.node[i]['origin'] == 'W'])
                    Nn = len([i for i in self.G.nodes() if self.G.node[i]['origin'] == 'N'])

                    f.write('%s, %s, %s ,%s ,%s ,%s ,%s ,%s ,%s\n'% (j,A,M,self.removed_nodes,self.edges_added,self.removed_edges,Nn,Mn,Wn))

                    print('%s, %s, %s ,%s ,%s ,%s ,%s ,%s ,%s'% (j,A,M,self.removed_nodes,self.edges_added,self.removed_edges,Nn,Mn,Wn))


                    
                i += 1
                j += 1
                
            

        f.close()
                
        return Assor,Mod



    

for x in [0.25,0.5,0.75,0.9,1]:
    y = DEB(x)
    y.run()
##y = DEB(0.1)
##y.run(interval,4000,stopping = True)
