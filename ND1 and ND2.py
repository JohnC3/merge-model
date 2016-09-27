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
        if rand.uniform(0,1) < self.p:
            G.remove_node(doomed)
            v = rand.sample(self.N,1)[0]

            G.add_edge(v,doomed)

        self.G = G

    def run(self,rep):

        for i in range(rep):
            self.go()

        deg = (2*len(self.G.edges())/len(self.G.nodes()))
        print('report:')
        print('Average Degree: '+str(deg))
        print('Average Clustering: '+str(nx.transitivity(self.G)))
        print('Components: '+str(nx.number_connected_components(self.G)))
    
        
def justGO():           
    s = nx.grid_graph([50,50])
    m = ND1(s,0.05)
    nx.write_graphml(m.G,'C:\\Users\\John\\Desktop\\Start.graphml')
    m.run(100)
    nx.write_graphml(m.G,'C:\\Users\\John\\Desktop\\100.graphml')
    m.run(100)
    nx.write_graphml(m.G,'C:\\Users\\John\\Desktop\\200.graphml')
    return m


from AACoreSqlManagment import *
class lazyV1():
    def __init__(self):
        self.eset = CW.execute('SELECT Source,Target FROM Aug11e').fetchall()
        self.G = self.construct_G(self.eset)
        
    def construct_G(self,eset):
        G = nx.from_edgelist(eset)
        for n in G.nodes():
            G.node[n]['threshold'] = rand.randrange(-1,10)
        return G
    
    
    #Remove nodes incrament thingy
    def remove_Node2(self,node):
        G = self.G
        neighbours = G.neighbors(node)
        G.remove_node(node)
        for friend in neighbours:
            G.node[friend]['threshold'] += -1
        return G

    #Run some sort of edge addition system on the graph.
    def edge_addition_process(self):
        pos = self.G.nodes()
        for i in range(10000):
            self.G.add_edge(rand.sample(pos,2))
            
            
    def go(self):
        G = self.G
        print(str(len(G.nodes())))
        for i in G.nodes():
            if G.node[i]['threshold'] == -1:
                self.remove_Node2(i)
        print(str(len(G.nodes())))    
        
