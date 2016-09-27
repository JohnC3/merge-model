#ND1 Algorithm is very simple

#Pick a node choose two neighbours of that node at random and add an edge between them
    #If the node has only one neighbour add a edge to another random node
#With probability p remove all edges from a randomly selected node (delete it)
    #Add a new node with a single edge to a random node.

from buildGraphDec27 import *
import networkx as nx
import random as rand

O = outputGraph(Connery,'Jan18Node','ConneryJan18Eset')
O.pickNodes('WHERE faction = "VS"')
O.pickEdges()
Default_seed = O.build()


class ND1:
    #Take a seed graph too iterate on.
    def __init__(self,seed_graph,p):
        self.G = seed_graph
        self.p = p
        self.N = self.G.nodes()
        self.totalReps = 0

    def likelyhoodFun(self,num):
        l = float(len(self.N))
        if num != 0:
            return 1/(num/l)
        else:
            return 0.0
        

    def deathAttribute(self):
        
        for index,n in enumerate(self.N):
            self.G.node[n]['p']=self.likelyhoodFun(index)

            
            

    def go(self):
        G = self.G
        #Pick a node at random.
        n = rand.sample(self.N,1)[0]

        #Get neighbours of that node
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

        #Pick a node to mabey delete
        doomed = rand.sample(self.N,1)[0]
        try:
            prob = rand.uniform(0,1) < 1/self.G.degree(doomed)
        except:
            prob = 0
        if rand.uniform(0,1) < self.G.node[doomed]['p']:
            G.remove_node(doomed)

            
            v = rand.sample(self.N,6)
            for sv in v:
            
                G.add_edge(sv,doomed)

        self.G = G

    def run(self,rep):
        self.totalReps += rep
        for i in range(rep):
            self.go()

        deg = (2*len(self.G.edges())/len(self.G.nodes()))
        print('report:')
        print('|E(G)| = '+str(len(self.G.edges()))+'   |N(G)| = '+str(len(self.G.nodes())))
        print('Max Degree '+str(max([self.G.degree(i) for i in self.G.nodes()])))
        print('Average Degree: '+str(deg))
        print('Average Clustering: '+str(nx.transitivity(self.G)))
        print('Components: '+str(nx.number_connected_components(self.G)))
        nx.write_graphml(self.G,'C:\\Users\\John\\Desktop\\'+str(self.totalReps)+'.graphml')
    
        
            
s = nx.grid_graph([50,50])
m = ND1(s,0.5)
nx.write_graphml(m.G,'C:\\Users\\John\\Desktop\\Start.graphml')

