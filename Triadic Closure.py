
#Test for triadic colosure effect.

from AACoreSqlManagment import *

ind = 4

class nlistTooSmall(Exception):

    def __init__(self, value):
        print('That list of nodes is of the wrong length')



def singleCol(conn,query):
    return [i[0] for i in conn.execute(query).fetchall()]

def doubleCol(conn,query):
    return [i for i in conn.execute(query).fetchall()]


def mutualNeig(Graph,pair):
    A = list(Graph[pair[0]])
    B = list(Graph[pair[1]])
    return list(set(A).intersection(set(B)))  

t = singleCol(CW,'SELECT date from date_names')

A = set(singleCol(CW,'SELECT Id FROM '+t[ind]+' WHERE degree > "0"'))

B = set(singleCol(CW,'SELECT Id FROM '+t[ind + 1]+' WHERE degree > "0"'))

Keep = A.intersection(B)

GA = nx.from_edgelist(doubleCol(CW,'SELECT Source,Target From '+t[ind]+'e'))
# Going to need this later to test for triadic closure
saveGA = GA

GB = nx.from_edgelist(doubleCol(CW,'SELECT Source,Target From '+t[ind+1]+'e'))

print(len(GA))
print(len(GB))

GA = nx.Graph(GA.subgraph(list(Keep)))

GB = nx.Graph(GB.subgraph(list(Keep)))

print(len(GA.nodes()))
print(len(GB.nodes()))

store = {}

sig = []

#new edges should be out[1] and removed edges out[0]
for i,n in enumerate(Keep):
    A = set(GA[n].keys())
    B = set(GB[n].keys())
    out = (list(A - B),list(B-A))
    if out[0] != [] or out[1] != []:
        sig.append(i)
    store[n] = out
    
print('In the time from '+t[ind]+' to '+t[ind+1])
print('Number of nodes who had changes')
print(str(len(sig)))

newEdges = []
for i in list(store.keys()):
    if len(store[i][1]) > 0:
        for v in store[i][1]:
            newEdges.append([i,v])

print('The number of new edges formed was')
print(len(newEdges))

lostEdges = []
for i in list(store.keys()):
    if len(store[i][0]) > 0:
        for v in store[i][0]:
            lostEdges.append([i,v])

print('The number of edges lost was')
print(len(lostEdges))

triads_closed = []
for k in newEdges:
    triads_closed.append(len(mutualNeig(saveGA,k)))

print('resulting the the closure of this many triads')
print(sum(triads_closed))

        
# What edges were removed?
oldEdges = []
for i in list(store.keys()):
    if len(store[i][0]) > 0:
        for v in store[i][1]:
            oldEdges.append([i,v])
print('The number of edges removed was')
print(len(oldEdges))
triads_opened = []
for k in oldEdges:
    triads_opened.append(len(mutualNeig(saveGA,k)))


print('Which opened this many triads')
print(sum(triads_opened))



#How many triads were opened by this process?

