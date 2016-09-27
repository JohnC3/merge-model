# Make a node modle allready! Just to see what happens.

#Today we will model node dedication! The idea being friends who have longer sessions
#are more likely to be online around the same time thus reinforceing eachother.

from buildGraphJan20 import *

'''
Take a graph assign each a dedication mesure ie min_played/login_count.
At each timestep t select a random sample without replacement (RS).
for each character c in RS take the sum of the dedication all N(c) in G.
If the sum is greater then the current dedication of c: 
A) to the new sum or reduce it
B) add the delta
If dedication hits zero then remove the node. Take dedication as the inverse
probablity of node death

Count how many nodes died and add that many more nodes with preferential attachment
to dedication.
'''

'''
Extra credit: Make node age a attribute as well that dampens the probablity of
any change. Involve node age in some meaningful way. eg nodes are added to the graph
are likely to have an edge to an older node.
Age damps the effect of death or increasses it.
'''

class dedicationModel():

    def __init__(self,connect,size,ss,condition='faction = "VS"'):
        self.initialG(connect,size,ss,condition)
        self.initialDedication()

        self.currentNodes = self.initG
        #makePlot().quickFrequencyPlot(self.overview,'minplayed/loggins',100)

        self.G = self.initG
        self.loop =0
        for i in range(2000):
            if i % 200 == 0:
                nx.write_graphml(self.G,'C:\\Users\\-John\\Dropbox\\IterationTst\\loopNumber'+str(self.loop)+'.graphml')
            self.myloop()
    #Pick a database a sample size a ss (the snapshot to fetch from the db)
    #and a condition on the portion to get from 
    def initialG(self,connect,size,ss,condition):
        
        self.nTableName = ordered(connect).nTables[ss]
        self.eTableName = ordered(connect).eTables[ss]

        #Make a graph builder name it G

        GB = outputGraph(connect,self.nTableName,self.eTableName,col='Id,login_count,minutes_played')

        GB.pickNodes(' WHERE '+condition)

        #print(str(len(GB.Id)))

        GB.Id = random.sample(GB.Id,size)

        GB.pickEdges()

        GB.getAttributes()

        out = GB.build()

        self.initG = out
        


    #Take a graph G and find the dedication

    def initialDedication(self):
        overview =[]
        aList = []
        for n in self.initG.nodes():
            aList.append(float(self.initG.node[n]['minutes_played'])/float(self.initG.node[n]['login_count']))
        mean = sum(aList)/len(aList)
        SD = (sum([(i-mean)**2 for i in aList])/float(len(aList)))**0.5
        largist = max(aList)
        smalles = min(aList) 
        for n in self.initG.nodes():
            dedi = float(self.initG.node[n]['minutes_played'])/float(self.initG.node[n]['login_count'])
            self.initG.node[n]['dedication'] = dedi/largist
            overview.append(dedi)
        self.overview = overview

    #Take a node get its friends and find the dedication!
    def operateOnNode(self,Id):

        
        
        
        #k is a adjusting constant
        k=1
        Nid = self.G.neighbors(Id)

        
        if len(Nid) > 0:
            dedi = []
            oldDedi = self.G.node[Id]['dedication']
            for i in Nid:
                dedi.append(k*self.G.node[i]['dedication'])
            
            newDedi = sum(dedi)/len(dedi)
            if newDedi >1:
                newDedi = 1
                
            
            self.G.node[Id]['dedication'] = (oldDedi + (oldDedi-newDedi))/2
        #Delete edgeless nodes
        else:
            self.G.remove_node(Id)
            #print(Id+' had no edges')
    #Do the calculation once!
    def myloop(self):
        
        randSample = random.sample(self.G.nodes(),100)
        
        for r in randSample:
            self.operateOnNode(r)

        self.loop +=1
