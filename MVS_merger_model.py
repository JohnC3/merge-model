
from Merger_analysis_with_Pandas import *
from modularity import *
import networkx as nx
import random as rand
import math

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

class MVS:
    ## The seed graph is taken to iterate on.
    def __init__(self,r,e,l,faction = '1',seed_graph = None):
        '''
        The MVS model works by modifying the edges of a randomly selected node i and has three parameters:
        1) r the probability that we add a edge between i and a randomly selected node
        2) e the probability that we select a randomly chosen freind of a randomly chosen friend of i and add a edge to it.
        3) l the probability that we select a random tie and delete it.

        This version uses the VS on the 30th of June as its seed network.
        
        '''
        self.r = r
        self.e = e
        self.l = l
        if seed_graph == None:
            self.G = initial_state(faction = '1')
        else:
            self.G = seed_graph
        
        self.N = self.G.nodes()
        
        self.edges_added = 0
        self.removed_edges = 0

    ## Run through the algorithm once.
    def go(self):
        G = self.G
        ## Pick a node i at random.
        i = rand.sample(self.N,1)[0]

        ## With proability r choose another random node and add a edge
        if(rand.random() <= self.r):
            G.add_edge(i,rand.sample(self.N,1)[0])
            self.edges_added += 1

        ## With probability e choose a random friend of i and choose another friend of that friend if no edge exists between i and this friend of a friend add one.
        if(rand.random() <= self.e):

            neighI = nx.neighbors(G,i)
            
            if(len(neighI) > 1):
                ## Pick the friend of i
                F = rand.sample(neighI,1)[0]

                ## Find its neighbourhood and remove i from it.                
                friendsOfF = list(G[F].keys())
               
                if(len(friendsOfF) > 1):
                    friendsOfF.remove(i)
                    FOAF = rand.sample(friendsOfF,1)[0]
                    
                    if(FOAF not in neighI):
                        G.add_edge(i,FOAF)
                        self.edges_added += 1

        ## With probability l remove a random edge.
        if(rand.random() <= self.l):
            toDel = rand.sample(G.edges(),1)[0]
            
            G.remove_edge(toDel[0],toDel[1])
            self.removed_edges += 1
        self.G = G

    ## Run through the function
    

    
    ## Run the program and record results as you go,
    ## If stopping condition is true run the program the program and record results as you but stop only after 200000 nodes have been removed,
        
    def run(self,stopping = False):
        folder = 'MVS r=%s e=%s l=%s (1)' % (self.r,self.e,self.l)
        directory = 'C:\\Users\\jscle\\merger analysis\\MVS\\'+folder


        while(os.path.exists(directory)):
            directory = directory[:-3] + '('+str(int(directory[-2])+1)+')'
        if not os.path.exists(directory):
            os.makedirs(directory)


        ## Open a file to record assortivity in
        f = open(directory+'\\assortivity and modularity results.txt','a')
        
        f.write('Total nodes,%s \n total edges,%s \n' % (len(self.G.nodes()),len(self.G.edges())))

        f.write('repititions,Assortivity,Modularity,edges added,edges removed,average degree, average clustering coefficent \n')

        ## Initialize the assortivity and modularity.
        Assor = [nx.assortativity.attribute_assortativity_coefficient(self.G,'origin')]
        Mod = [modularity(nx.get_node_attributes(self.G,'origin'),self.G)]

        ## when i == interval record stuff, while j is less then repititions repeat.
        i = 0
        j = 0

        if(stopping):
            ## The expected number of itterations needed.
            Expected = 200000/(0.5 * self.r)
            repititions = math.floor(Expected)
            ## Get around 30 data points
            interval = math.floor(repititions / 100)
            print('repititions = %s' % repititions)
            print('interval = %s' % interval)
            
        else:
            repititions = 30000
            interval = 1000

        f.close()

            
        while(j <= repititions and self.edges_added < 100000):
            f = open(directory+'\\assortivity and modularity results.txt','a')
            ## Run the function once
            self.go()

            if(i == interval):
                i = 0
                M = modularity(nx.get_node_attributes(self.G,'origin'),self.G)
                A = nx.assortativity.attribute_assortativity_coefficient(self.G,'origin')

                ## Average degree
                AD = 2*(len(self.G.edges()))/len(self.G.nodes())
                ## Average clustering coefficent
                ACC = nx.average_clustering(self.G)
                
                Assor.append(A)
                Mod.append(M)
                
                nx.write_graphml(self.G,directory+'\\MVS reps = %s interval = %s.graphml' % (i,j))

                f.write('%s, %s, %s ,%s ,%s ,%s ,%s\n'% (j,A,M,self.edges_added,self.removed_edges,AD,ACC))

                print('%s, %s, %s ,%s ,%s ,%s ,%s'% (j,A,M,self.edges_added,self.removed_edges,AD,ACC))


                f.close()
            i += 1
            j += 1
                
            
        f.close()
                
        return Assor,Mod


##y = MVS(0.5,0.5,0.5)
##y.run()

##y = MVS(0.25,0.25,0.5)
##y.run()

##y = MVS(0.125,0.125,0.25)
##y.run()

##y = MVS(1,0.5,0.5)
##y.run(stopping = True)

y = MVS(0.4,0.4,1)
y.run(stopping = True)
