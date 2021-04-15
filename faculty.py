import csv
import operator

import networkx as nx
import matplotlib.pyplot as plt
import numpy
import pandas as pd

from preprocess import fetch_faculty, getHire
from tqdm import tqdm

FACULTY, NAMES = fetch_faculty()

class Year:

    '''
    Builds a Collaboration Network for the individual years
    '''   

    def __init__(self, year):

        global NAMES 
        global FACULTY       
        self.year = year

        self.graph_year = nx.Graph()
        self.graph_previous_years = nx.Graph() 

        self.year_info = {}
        self.previous_year_info = {}

        self.build_graph()
        self.set_information()
        self.add_properties_network()

    def build_graph(self):

        self.graph_year.add_nodes_from(NAMES)
        self.graph_previous_years.add_nodes_from(NAMES)

        for faculty in FACULTY:
            for paper in FACULTY[faculty].papers:               
                if (paper.year <= self.year) and (paper.year > 1999):
                    for author in paper.authors:
                        if (author in NAMES) and (author != FACULTY[faculty].name) and not(self.graph_previous_years.has_edge(FACULTY[faculty].name, author)) and not(self.graph_previous_years.has_edge(author, FACULTY[faculty].name)):
                            self.graph_previous_years.add_edge(FACULTY[faculty].name, author)                           

                            if paper.year == self.year:
                                self.graph_year.add_edge(FACULTY[faculty].name, author)

        return

    def set_information(self):

        def get_info(network, network_dic):
            def get_average_degree(network):
                degrees = [i[1] for i in (network.degree())]
                degrees = sum(degrees)
                avg_degree = degrees/(network.number_of_nodes())
                return round(avg_degree,2)

            def get_average_clustering(network):
                return round(nx.average_clustering(network),2)

            def get_global_clustering(network):
                d = nx.clustering(network)
                temp = dict(sorted(d.items(), key=operator.itemgetter(1),reverse=True))
                return temp

            def get_number_edges(network):
                '''
                Returns the number of edges in the network
                '''
                return network.number_of_edges()

            def get_connected_components(network):
                connected_components = nx.connected_components(network)
                num = 0    
                connected_components_list = []
                for i in connected_components :
                    if len(i) > 1 : 
                        num += 1
                        temp = network.subgraph(list(i)).copy()       
                        connected_components_list.append(temp) 
                return num, connected_components_list

            def get_dist(network):
                average=[]
                for C in (network.subgraph(c).copy() for c in nx.connected_components(network)):
                    average.append(nx.average_shortest_path_length(C))
                dist_connected=[]
                for i in range(len(average)):
                    if average[i] != 0:
                        dist_connected.append(round(average[i],2))
                dist_connected = sorted(dist_connected, reverse=True)
                dist_connected = [str(element) for element in dist_connected]
                dist_connected = ", ".join(dist_connected)
                return dist_connected

            def get_smallworld_sigma(network):
                for C in (network.subgraph(c).copy() for c in nx.connected_components(network)):
                    if len(C)>3:
                        sigma=nx.sigma(C, niter=1, nrand=1, seed=0)
                print(sigma)

            def get_most_edge_faculty(network):
                return sorted(network.degree, key=lambda x: x[1], reverse=True)

            def get_density(network):
                return round(nx.density(network),2)

            def get_degree_correlation_coefficient(network):
                return nx.degree_pearson_correlation_coefficient(network)

            network_dic['average_degree']=get_average_degree(network)
            network_dic['average_clustering_coefficient']=get_average_clustering(network)
            network_dic['number_of_edges'] = get_number_edges(network)
            network_dic['number_of_connected_components'], network_dic['connected_components'] = get_connected_components(network)
            network_dic['avg_dist'] = get_dist(network)
            network_dic['most_edge_faculty'] = get_most_edge_faculty(network)
            network_dic['density'] = get_density(network)
            network_dic['global_clustering'] = get_global_clustering(network)
            network_dic['degree_correlation_coefficient'] = get_degree_correlation_coefficient(network)

        get_info(self.graph_year,self.year_info)
        get_info(self.graph_previous_years,self.previous_year_info)

        return

    def display_networkx(self):
        '''
        Displays the network_x graph
        '''
        plt.figure(figsize=(24, 12))
        nx.draw_random(self.graph_year, with_labels=True, font_weight='bold')
        plt.show()
        return

    def add_properties_network(self):
        def get_graph_properties(network):
            degrees = dict(nx.degree(network))
            betweenness_centrality = nx.betweenness_centrality(network, normalized=True)
            eigenvector_centrality = nx.eigenvector_centrality(network, max_iter=600)
            degree_centrality = nx.degree_centrality(network)
            closeness_centrality = nx.closeness_centrality(network)
            clustering = nx.clustering(network)

            nx.set_node_attributes(network, name='degree', values=degrees)
            nx.set_node_attributes(network, name='betweenness', values=betweenness_centrality)
            nx.set_node_attributes(network, name='degree_centrality', values=degree_centrality)
            nx.set_node_attributes(network, name='eigenvector_centrality', values=eigenvector_centrality)
            nx.set_node_attributes(network, name='closeness_centrality', values=closeness_centrality)
            nx.set_node_attributes(network, name='clustering', values=clustering)

            number_to_adjust_by = 5

            adjusted_node_size = dict([(node, degree+number_to_adjust_by) for node, degree in nx.degree(network)])
            nx.set_node_attributes(network, name='adjusted_node_size', values=adjusted_node_size)

            pos = nx.spring_layout(network, scale = 2)
            for node in network.nodes:
                network.nodes[node]['pos'] = list(pos[node])
            
            return

        get_graph_properties(self.graph_year)
        get_graph_properties(self.graph_previous_years)
        
        return


class Faculty:
    def __init__(self, name, faculty_list):

        self.name = name
        self.faculty_list = faculty_list

        self.graph_years_scse = {}
        self.graph_years_all = {}        

        self.info = {}

        self.generate_graph_years()
        self.set_information()
   
    def generate_graph_years(self):
        def build_graph(year):
            def set_color_nodes(g):
                for i in g.nodes():
                    if i == self.name:
                        g.nodes[i]['color'] = "#0033cc"
                    elif i in self.faculty_list:
                        g.nodes[i]['color'] = "#99d6ff"
                    else:
                        g.nodes[i]['color'] = "#666666"
                return 

            graph = nx.Graph()
            graph_all = nx.Graph()      

            graph.add_nodes_from(pd.read_csv("Faculty.csv")['Faculty'].to_list())      

            for paper in FACULTY[self.name].papers:
                if paper.year == year:
                    for author in paper.authors:
                        if (author != FACULTY[self.name].name) and not(graph.has_edge(FACULTY[self.name].name, author)) and not(graph.has_edge(author, FACULTY[self.name].name)):
                            graph_all.add_edge(FACULTY[self.name].name, author)
                            if (author in NAMES):
                                graph.add_edge( FACULTY[self.name].name, author)

            
            set_color_nodes(graph)
            set_color_nodes(graph_all)

            self.graph_years_scse[year] = graph 
            self.graph_years_all[year] = graph_all        

            return
        
        for i in range(2000,2022):
            build_graph(i)
        return
    
    def set_information(self):
        def getYear(year):
            info = {}

            #Number of collaborations within scse
            info['scse_collaboration'] = self.graph_years_scse[year].number_of_edges()

            #Number of collaborations in total 
            info['all_collaboration'] = self.graph_years_all[year].number_of_edges()

            return info
        
        for i in range(2000,2022):
            self.info[i] = getYear(i)
        
        return



class FacultySubset:
    def __init__(self, names):
        self.names = names

        self.graph_years = {}

        self.faculty = {}

        self.generate_graph_years()
        self.build_faculty()

    def generate_graph_years(self):
        def build_graph(year):
            graph = nx.Graph()
            graph_all = nx.Graph() 
            
            NAMES = pd.read_csv("Faculty.csv")['Faculty'].to_list()
            
            graph.add_nodes_from(NAMES)
            for i in graph.nodes():
                if i in self.names:
                    graph.nodes[i]['color'] = "#0033cc"
                else:
                    graph.nodes[i]['color'] = "#666666"

            for faculty in self.names:
                for paper in FACULTY[faculty].papers:
                    if paper.year == year:
                        for author in paper.authors:
                            if (author != faculty) and not(graph.has_edge(faculty, author)) and not(graph.has_edge(author,faculty)):                                
                                if (author in NAMES):
                                    graph.add_edge(faculty, author)
 
            self.graph_years[year] = graph    

            return
        
        for i in range(2000,2022):
            build_graph(i)
        return
    
    def build_faculty(self):
        for i in self.names:
            self.faculty[i] = Faculty(i, self.names)

class ManageGraph:    
    def __init__(self):
        faculty, names = FACULTY, NAMES
        
        self.nodes=[]
        self.edges=[]
        
        for x in faculty:
            if(faculty[x].managment=='Y'):
                self.nodes.append(x)      
                p=faculty[x].papers
                for y in p:
                    for a in y.authors:
                        if(a in names):
                            self.edges.append((x, a))
    
class PositionGraph:    
    def __init__(self, target):
        faculty, names = FACULTY, NAMES
        
        self.nodes=[]
        self.edges=[]

        
        for x in faculty:
            if(faculty[x].position==target):
                self.nodes.append(x)
                
        for x in self.nodes:
            p=faculty[x].papers
            
            for y in p:
                for a in y.authors:
                    if(a in self.nodes):
                        self.edges.append((x,a))
                        
                        
class ExcellenceGraph:    
    def __init__(self):
        faculty, names = FACULTY, NAMES
        
        self.nodes=[]
        self.edges=[]
        
        for x in faculty:
            if(faculty[x].excellenceNode==True):
                self.nodes.append(x)

class Hire:
    def __init__(self):
        
        self.Hire = getHire()

        self.l = []
        self.graph = nx.Graph() 
        self.degree = None 
        self.generate_graph_years()
        self.set_node_info(self.graph)
        self.get_top()
        self.graph = self.build_graph()

        self.set_degree()
       
   
    def generate_graph_years(self):  
        print("Generating graphs")
        for faculty in tqdm(self.Hire):
            for paper in self.Hire[faculty].papers:               
                if (paper.year < 2021) and (paper.year >= 2018):
                    for author in paper.authors:
                        if (author != self.Hire[faculty].name) and not(self.graph.has_edge(self.Hire[faculty].name, author)) and not(self.graph.has_edge(author, self.Hire[faculty].name)):
                            self.graph.add_edge(self.Hire[faculty].name, author)                            

        
        return  

    def set_node_info(self, network):
        print("Setting node information")
        degrees = dict(nx.degree(network)) 
        nx.set_node_attributes(network, name='degree', values=degrees)
        self.degree = degrees
        return
    
    def get_top(self):
        degrees = dict(nx.degree(self.graph)) 
        temp = sorted(degrees.items() , key=lambda x: x[1] , reverse=True)        
        for i in temp[:100]:
            if i[0] not in NAMES:
                self.l.append(i[0])
        return
    
    def build_graph(self):
        g = nx.Graph()
        for i in self.graph.edges():
            if ((i[0] in  self.l) and (i[1] in self.l)):                
                g.add_edge(i[0],i[1])
        plt.figure(figsize=(24, 12))
        nx.draw_circular(g)
        plt.show()
        print(g.number_of_nodes())
        return g
    
    def set_degree(self):
        self.set_node_info(self.graph)
        for i in self.graph.nodes():
            #self.graph.nodes[i]['degree'] = self.degree[i]
            if self.graph.nodes[i] in NAMES:
                self.graph.nodes[i]['color'] = "#0033cc"
            else:
                self.graph.nodes[i]['color'] = "#666666"
        
        


