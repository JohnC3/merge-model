#BA source code
import networkx as nx
import random
import itertools
import matplotlib.pyplot as plt


def BA_evoloution(G, n, m, seed=None):
    """Return random graph using Barabási-Albert preferential attachment model.
        
    A graph of n nodes is grown by attaching new nodes each with m
    edges that are preferentially attached to existing nodes with high
    degree.
    
    Parameters
    ----------
    n : int
        Number of nodes
    m : int
        Number of edges to attach from a new node to existing nodes
    seed : int, optional
        Seed for random number generator (default=None).   

    Returns
    -------
    G : Graph
        
    Notes
    -----
    The initialization is a graph with with m nodes and no edges.

    References
    ----------
    .. [1] A. L. Barabási and R. Albert "Emergence of scaling in
       random networks", Science 286, pp 509-512, 1999.
    """
        
    if m < 1 or  m >=n:
        raise nx.NetworkXError(
              "Barabási-Albert network must have m>=1 and m<n, m=%d,n=%d"%(m,n))
    if seed is not None:
        random.seed(seed)    

    # Add m initial nodes (m0 in barabasi-speak) 
    
    
    
    # List of existing nodes, with nodes repeated once for each adjacent edge 
    repeated_nodes=list(set([i for i,j in G.edges()])) + list(set([j for i,j in G.edges()]))

    # Target nodes for new edges
    targets = random.sample(repeated_nodes,m)
    # Start adding the other n-m nodes. The first node is m.
    source=len(G.nodes())
    print('BA model with N = '+str(n)+' and m = '+str(m))
    print('N , Triangle count')
    while source<n:
        # Add edges to m nodes from the source.
        G.add_edges_from(zip([source]*m,targets))
        # Add new to origin
        G.node[source]['origin'] = 'N'      
        # Add one node to the list for each new edge just created.
        repeated_nodes.extend(targets)
        # And the new node "source" has m edges to add to the list.
        repeated_nodes.extend([source]*m) 
        # Now choose m unique nodes from the existing nodes 
        # Pick uniformly from repeated_nodes (preferential attachement) 
        targets = random.sample(repeated_nodes,m)
        source += 1
    return G


def BA_evoloution_With_removal(G, n, m, r, seed=None,iteration_symbol = 'a'):
    print(n)
    """Same as before except this time remove r nodes
    """
        
    if m < 1 or  m >=n:
        raise nx.NetworkXError(
              "Barabási-Albert network must have m>=1 and m<n, m=%d,n=%d"%(m,n))
    if seed is not None:
        random.seed(seed)    
    
    # List of existing nodes, with nodes repeated once for each adjacent edge 
    repeated_nodes=list(set([i for i,j in G.edges()])) + list(set([j for i,j in G.edges()]))

    # Target nodes for new edges
    targets = random.sample(repeated_nodes,m)
    # Start adding the other n-m nodes. The first node is m.
    source=len(G.nodes())
    print('BA model with N = '+str(n)+' and m = '+str(m))
    while source<n:
        # Node name depends on iteration symbol
        nodeName = '%s%s' %(iteration_symbol,source)
        
        # Add edges to m nodes from the source.
        G.add_edges_from(zip([nodeName]*m,targets))
        # Add new to origin
        G.node[nodeName]['origin'] = 'N'      
        # Add one node to the list for each new edge just created.
        repeated_nodes.extend(targets)
        # And the new node "source" has m edges to add to the list.
        repeated_nodes.extend([nodeName]*m) 
        # Now choose m unique nodes from the existing nodes 
        # Pick uniformly from repeated_nodes (preferential attachement) 
        targets = random.sample(repeated_nodes,m)
        source += 1

    

    # Remove r nodes before returning
    removal = random.sample(G.nodes(),r)
    print(len(G.nodes()))
    G.remove_nodes_from(removal)
    print(len(G.nodes()))
    
    return G



















def barabasi_albert_graph(n, m, seed=None):



    """Return random graph using Barabási-Albert preferential attachment model.
        
    A graph of n nodes is grown by attaching new nodes each with m
    edges that are preferentially attached to existing nodes with high
    degree.
    
    Parameters
    ----------
    n : int
        Number of nodes
    m : int
        Number of edges to attach from a new node to existing nodes
    seed : int, optional
        Seed for random number generator (default=None).   

    Returns
    -------
    G : Graph
        
    Notes
    -----
    The initialization is a graph with with m nodes and no edges.

    References
    ----------
    .. [1] A. L. Barabási and R. Albert "Emergence of scaling in
       random networks", Science 286, pp 509-512, 1999.
    """
        
    if m < 1 or  m >=n:
        raise nx.NetworkXError(
              "Barabási-Albert network must have m>=1 and m<n, m=%d,n=%d"%(m,n))
    if seed is not None:
        random.seed(seed)    

    # Add m initial nodes (m0 in barabasi-speak) 
    G=nx.empty_graph(m)
    G.name="barabasi_albert_graph(%s,%s)"%(n,m)
    # Target nodes for new edges
    targets=list(range(m))
    # List of existing nodes, with nodes repeated once for each adjacent edge 
    repeated_nodes=[]     
    # Start adding the other n-m nodes. The first node is m.
    source=m
    print('BA model with N = '+str(n)+' and m = '+str(m))
    print('N , Triangle count')
    while source<n:
        if source % 100 == 0:
            tri = sum(list(nx.triangles(G).values()))/3
            print(str(len(G.nodes()))+','+str(tri))
        # Add edges to m nodes from the source.
        G.add_edges_from(zip([source]*m,targets)) 
        # Add one node to the list for each new edge just created.
        repeated_nodes.extend(targets)
        # And the new node "source" has m edges to add to the list.
        repeated_nodes.extend([source]*m) 
        # Now choose m unique nodes from the existing nodes 
        # Pick uniformly from repeated_nodes (preferential attachement) 
        targets = random.sample(repeated_nodes,m)
        source += 1
    return G









def barabasi_albert_graph_c4_count(n, m, seed=None):
    
    if m < 1 or  m >=n:
        raise nx.NetworkXError(
              "Barabási-Albert network must have m>=1 and m<n, m=%d,n=%d"%(m,n))
    if seed is not None:
        random.seed(seed)    

    # Add m initial nodes (m0 in barabasi-speak) 
    G=nx.empty_graph(m)
    G.name="barabasi_albert_graph(%s,%s)"%(n,m)
    # Target nodes for new edges
    targets=list(range(m))
    # List of existing nodes, with nodes repeated once for each adjacent edge 
    repeated_nodes=[]     
    # Start adding the other n-m nodes. The first node is m.
    source=m
    c4_count = []
    while source<n:
        #print(source)
        # Add edges to m nodes from the source.
        G.add_edges_from(zip([source]*m,targets)) 
        # Add one node to the list for each new edge just created.
        repeated_nodes.extend(targets)
        # And the new node "source" has m edges to add to the list.
        repeated_nodes.extend([source]*m) 
        # Now choose m unique nodes from the existing nodes 
        # Pick uniformly from repeated_nodes (preferential attachement) 
        targets = random.sample(repeated_nodes,m)
        c4_added = 0
        for u,v in itertools.combinations(targets,2):
            
            u_neigh = list(G[u].keys())
            v_neigh = []
            if v not in u_neigh:
                v_neigh = list(G[v].keys())
            mutual = set(u_neigh).intersection(set(v_neigh))-set(targets)
            
            c4 = [i for i in mutual if i not in targets+[source]]
            #print(str(u)+','+str(v)+':'+str(c4))
            c4_added= c4_added+ len(c4)
         
        c4_count.append(c4_added)
        source += 1
    
    return c4_count

#A switching algorithm for edges, used for generating random graphs, takes a graph and the number of switching operations
def switching_algorithm(G,reps):
    
    for i in range(reps):
        e1,e2 = random.sample(G.edges(),2)

        if len(set(list(e1)+list(e2)))==4:
               
            
            G.remove_edges_from([e1,e2])
            G.add_edges_from([(e1[0],e2[0]),(e1[1],e2[1])])
    return G

#Take a random pair of vertices are they connected?
def probability_of_edge(G,reps):
    yes = 0
    no = 0
    E = G.edges()
    for i in range(reps):
        n1,n2 = random.sample(G.nodes(),2)
        if (n1,n2) in E:
            yes+=1
        else:
            no+=1
    return yes/no

#Sampleing.
def temp(G,reps,x):
    outcomes = []
    for i in range(x):
        outcomes.append(probability_of_edge(G,reps))
    return outcomes
        
        
def directed_barabasi_albert_graph(n, m, seed=None):

    """Return random graph using Barabási-Albert preferential attachment model.
        
    A graph of n nodes is grown by attaching new nodes each with m
    edges that are preferentially attached to existing nodes with high
    degree.
    
    Parameters
    ----------
    n : int
        Number of nodes
    m : int
        Number of edges to attach from a new node to existing nodes
    seed : int, optional
        Seed for random number generator (default=None).   

    Returns
    -------
    G : Graph
        
    Notes
    -----
    The initialization is a graph with with m nodes and no edges.

    References
    ----------
    .. [1] A. L. Barabási and R. Albert "Emergence of scaling in
       random networks", Science 286, pp 509-512, 1999.
    """
        
    if m < 1 or  m >=n:
        raise nx.NetworkXError(
              "Barabási-Albert network must have m>=1 and m<n, m=%d,n=%d"%(m,n))
    if seed is not None:
        random.seed(seed)    

    # Add m initial nodes (m0 in barabasi-speak) 
    G=nx.empty_graph(m,create_using=nx.DiGraph())
    G.name="barabasi_albert_graph(%s,%s)"%(n,m)
    # Target nodes for new edges
    targets=list(range(m))
    # List of existing nodes, with nodes repeated once for each adjacent edge 
    repeated_nodes=[]     
    # Start adding the other n-m nodes. The first node is m.
    source=m
    while source<n:
        # Add edges to m nodes from the source.
        G.add_edges_from(zip([source]*m,targets)) 
        # Add one node to the list for each new edge just created.
        repeated_nodes.extend(targets)
        # And the new node "source" has m edges to add to the list.
        repeated_nodes.extend([source]*m) 
        # Now choose m unique nodes from the existing nodes 
        # Pick uniformly from repeated_nodes (preferential attachement) 
        targets = random.sample(repeated_nodes,m)
        source += 1
    return G

