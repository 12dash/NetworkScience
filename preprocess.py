import ast
import os
import pandas as pd
import networkx as nx
import matplotlib.pyplot as plt

from bokeh.io import output_notebook, show, save
from bokeh.models import Range1d, Circle, ColumnDataSource, MultiLine, EdgesAndLinkedNodes, NodesAndLinkedEdges, LabelSet
from bokeh.plotting import figure, from_networkx
from bokeh.palettes import Blues8, Reds8, Purples8, Oranges8, Viridis8, Spectral8
from bokeh.transform import linear_cmap
from bokeh.models.widgets import Tabs, Panel

def initialize():
    try:
        os.mkdir("./Graph")
    except Exception as e:
        pass
    

class YearNetwork:
    df = pd.DataFrame()
    faculty = []
    nx_G = None
    bokeh_G = None
    
    def __init__(self, year):

        self.nx_G = nx.Graph()

        self.df = pd.read_csv("SCSENodes.csv")
        self.df = self.df.drop([self.df.columns[0]], axis = 1)      

        self.faculty = self.df.Faculty.to_list()

        self.year = year
        self.generate_networkx()
        self.add_properties_network()
    
    def generate_networkx(self):
        '''
        Generates the Networkx graph by adding edges and nodes
        '''
        for i in self.faculty:
            if i != '':
                
                self.nx_G.add_node(i)
        collabs = self.df[self.year].to_list()
        collabs = [ast.literal_eval(x)  for x in collabs]
        for i in range(len(collabs)):
            for j in collabs[i]:
                if j != '':
                    j = j.replace("'","")
                    self.nx_G.add_edge(self.faculty[i],j)

    def add_properties_network(self):

        self.degrees = dict(nx.degree(self.nx_G))
        self.betweenness_centrality = nx.betweenness_centrality(self.nx_G)

        nx.set_node_attributes(self.nx_G, name='degree', values=self.degrees)
        nx.set_node_attributes(self.nx_G, name='betweenness', values=self.betweenness_centrality)

        number_to_adjust_by = 5

        adjusted_node_size = dict([(node, degree+number_to_adjust_by) for node, degree in nx.degree(self.nx_G)])
        nx.set_node_attributes(self.nx_G, name='adjusted_node_size', values=adjusted_node_size)
   
    def draw_bokeh(self): 
        # plot with different sized node degrees + labels           
        size_by_this_attribute = 'adjusted_node_size'
        color_by_this_attribute = 'adjusted_node_size'

        color_palette = Viridis8

        title = 'Network with node sizes according to degree'
        HOVER_TOOLTIPS = [("Faculty", "@index"),("Degree", "@degree"),("Betweenness Centrality", "@betweenness")]

        plot = figure(tooltips = HOVER_TOOLTIPS, tools="pan,wheel_zoom,save,reset", active_scroll='wheel_zoom',
                x_range=Range1d(-11.1, 11.1), y_range=Range1d(-11.1, 11.1), title=title, plot_width = 1000, plot_height = 800)
        
        network_graph = from_networkx(self.nx_G, nx.spring_layout, scale=10, center=(0, 0))

        minimum_value_color = min(network_graph.node_renderer.data_source.data[color_by_this_attribute])
        maximum_value_color = max(network_graph.node_renderer.data_source.data[color_by_this_attribute])
        network_graph.node_renderer.glyph = Circle(size=size_by_this_attribute, fill_color=linear_cmap(color_by_this_attribute, color_palette, minimum_value_color, maximum_value_color))

        network_graph.edge_renderer.glyph = MultiLine(line_alpha=0.5, line_width=1)

        plot.renderers.append(network_graph)
        
        #Add Labels
        #x, y = zip(*network_graph.layout_provider.graph_layout.values())
        #node_labels = list(self.nx_G.nodes())
        #source = ColumnDataSource({'x': x, 'y': y, 'name': [node_labels[i] for i in range(len(x))]})
        #labels = LabelSet(x='x', y='y', text='name', source=source, background_fill_color='white', text_font_size='10px', background_fill_alpha=.7)
        #plot.renderers.append(labels)
        return plot

    def display_networkx_graph(self):
        '''
        Shows the network_x graph
        '''
        plt.figure(figsize = (24,12))
        pos = None
        pos =  nx.spring_layout(self.nx_G)
        nx.draw_random(self.nx_G, with_labels = True, font_weight = 'bold')
        plt.show()

class FacultyNetwork:    
    graph = {}
    plots = {}

    tabs = []
    tab = None
    
    def __init__(self):
        self.generate_networks()        
    
    def generate_networks(self):
        '''
        Generates Networks for each year
        '''
        for i in range(2000,2022):
            self.graph[i] =  YearNetwork(str(i))  
            self.get_plot_year(i)        
        self.build_tab()

    def build_tab(self):
        for i in range(2000,2022):
            self.tabs.append(Panel(child = self.plots[i], title = str(i)))        
        self.tab = Tabs(tabs=self.tabs)

    def get_plot_year(self, year):
        '''
        Displays the networkx network for a particular year
        '''
        self.plots[year] = self.graph[year].draw_bokeh()
    
    def display_years(self):
        show(self.tab)

if __name__ == "__main__":
    initialize()    
    f = FacultyNetwork()
    f.display_years()

    #year = (int)(input())
    #while(year != -1):
        #facultyNetwork.display_year(year)
        #year = (int)(input())
