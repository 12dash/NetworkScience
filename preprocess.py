import pandas as pd
import networkx as nx
import matplotlib.pyplot as plt
from pyvis.network import Network
import ast
import os

def initialize():
    try:
        os.mkdir("./Graph")
    except Exception as e:
        pass
    

class YearNetwork:

    df = pd.DataFrame()
    faculty = []
    nx_G = None
    
    def __init__(self, year):

        self.nx_G = nx.Graph()

        self.df = pd.read_csv("SCSENodes.csv")
        self.df = self.df.drop([self.df.columns[0]], axis = 1)      

        self.faculty = self.df.Faculty.to_list()

        self.year = year
        self.generate_networkx()
    
    def generate_networkx(self):
        for i in self.faculty:
            if i != '':
                
                self.nx_G.add_node(i)
        collabs = self.df[self.year].to_list()
        collabs = [ast.literal_eval(x)  for x in collabs]
        for i in range(len(collabs)):
            for j in collabs[i]:
                if j != '':
                    #j = j.replace("'","")
                    self.nx_G.add_edge(self.faculty[i],j)
    
    def display_networkx_graph(self):
        '''
        Shows the network_x graph
        '''
        plt.figure(figsize = (24,12))
        pos =  nx.spring_layout(self.nx_G)
        nx.draw(self.nx_G, pos = pos,with_labels = True, font_weight = 'bold')
        plt.show()

class FacultyNetwork:    
    graph = {}
    
    def __init__(self):
        self.generate_networks()
    
    def generate_networks(self):
        for i in range(2000,2022):
            self.graph[i] =  YearNetwork(str(i))  

    def display_year(self, year):
        self.graph[year].display_networkx_graph()
        

if __name__ == "__main__":
    initialize()
    facultyNetwork = FacultyNetwork()
    year = (int)(input())
    while(year != -1):
        facultyNetwork.display_year(year)
        year = (int)(input())
