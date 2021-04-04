from bokeh.io import output_notebook, show, save
from bokeh.models import Range1d, Circle, ColumnDataSource, MultiLine, EdgesAndLinkedNodes, NodesAndLinkedEdges, LabelSet, Div, CustomJS, TextInput, RadioButtonGroup
from bokeh.plotting import figure, from_networkx
from bokeh.palettes import Blues8, Reds8, Purples8, Oranges8, Viridis8, Spectral8
from bokeh.transform import linear_cmap
from bokeh.models.widgets import Tabs, Panel
from bokeh.layouts import row, layout

from collections import Counter

import networkx as nx

def get_degree_distribution(network, title):
    degree = [i[1] for i in nx.degree(network)]
    values = sorted(degree)
    hist = Counter(values)
    l1 = []
    l2 = []
    for i in hist:
        l1.append(i)
        l2.append(hist[i])

    p = figure(title=title, plot_width=400, plot_height=400,
               y_axis_type="log", x_axis_type="log", toolbar_location = None)
    p.line(l1, l2, line_width=2)
    return p


def generate_year_graph(network, title="Years"):

    size_by_this_attribute = 'adjusted_node_size'
    color_by_this_attribute = 'adjusted_node_size'

    color_palette = Viridis8

    HOVER_TOOLTIPS = [("Faculty", "@index"), ("Degree", "@degree"),
                      ("Betweenness Centrality", "@betweenness"),
                      ("Clustering Coefficient", "@clustering")]

    plot = figure(tooltips=HOVER_TOOLTIPS, tools="pan,wheel_zoom,save,reset", active_scroll='wheel_zoom',toolbar_location = None,
                  x_range=Range1d(-11.1, 11.1), y_range=Range1d(-11.1, 11.1), title=str(title), plot_width=400, plot_height=400)

    network_graph = from_networkx(
        network, nx.spring_layout, scale=10, center=(0, 0))
    minimum_value_color = min(
        network_graph.node_renderer.data_source.data[color_by_this_attribute])
    maximum_value_color = max(
        network_graph.node_renderer.data_source.data[color_by_this_attribute])
    network_graph.node_renderer.glyph = Circle(size=size_by_this_attribute, fill_color=linear_cmap(
        color_by_this_attribute, color_palette, minimum_value_color, maximum_value_color))
    network_graph.edge_renderer.glyph = MultiLine(line_alpha=0.5, line_width=1)
    plot.renderers.append(network_graph)

    return plot

def generate_giant_componnet(network, title = "Giant Components"):
    HOVER_TOOLTIPS = [("Faculty", "@index")]
    plot = figure(tooltips = HOVER_TOOLTIPS, toolbar_location = None, x_range=Range1d(-11.1, 11.1), y_range=Range1d(-11.1, 11.1), title=str(title), plot_width=400, plot_height=400)
    network_graph = from_networkx(network, nx.spring_layout, scale=10, center=(0, 0))
    network_graph.node_renderer.glyph = Circle()
    network_graph.edge_renderer.glyph = MultiLine(line_alpha=0.5, line_width=1)
    plot.renderers.append(network_graph)
    return plot

def generate_tab_year(graphs): 
    def get_div():
            text = f"""
            <div>
            <h4>Network Properties</h4>
            <ul>
                <li>Number of Edges: {temp.year_info['number_of_edges']}</li>
                <li>Average Clustering Coefficient : {temp.year_info['average_clustering_coefficient']}</li>
                <li>Average Degree : {temp.year_info['average_degree']}</li>    
                <li>Number of Connected Components: {temp.year_info['number_of_connected_components']}</li>                
            </ul>
            </div>
            """
            div = Div(text=text, width=500, height=100)
            return div

    def get_first_row(temp):       

        year_collab = generate_year_graph(
            temp.graph_year, f"Collaborations in {i}")
        degree_distribution = get_degree_distribution(
            temp.graph_year, "Degree Distribution")
        return row([year_collab, degree_distribution])

    text = """<h3>Collaboration over years</h3><hr/>"""
    div = Div(text=text, width=500, height=100)
    tabs = []

    def connect_tabs(temp):
        components = []
        for i in temp.year_info['connected_components']:
            components.append(generate_giant_componnet(i) )
        lay = []
        temp = []
        for i in range(len(components)):   
            temp.append(components[i])         
            if (i+1)%3 == 0:
                lay.append(temp)
                temp = []           
        giant_component = layout(lay)
        return giant_component


    for i in range(2000, 2021):
        temp = graphs[i]
        stuff = []
        year_tab = Panel(child = get_first_row(temp), title = "Year Analysis")
        info_tab = Panel(child = get_div(), title = "Information")
        connected_component_tab = Panel(child = connect_tabs(temp), title = "Connected Componnents")    
        till_now  = Panel(child =  generate_year_graph(temp.graph_previous_years, f"Collaborations from 2000 to {i}"), title = "Cummalative Collaboration")  
        grid = Tabs(tabs=[year_tab, info_tab, connected_component_tab])
        tabs.append(Panel(child=grid, title=str(i)))

    tab = Tabs(tabs=tabs)
    disp = layout([div, tab])

    return disp


def generate_faculty(Faculty, name):
    def get_network_plot(network, title):

        HOVER_TOOLTIPS = [("Faculty", "@index")]
        
        plot = figure(tooltips=HOVER_TOOLTIPS,tools="pan,wheel_zoom,save,reset", active_scroll='wheel_zoom', toolbar_location = None,
                      x_range=Range1d(-11.1, 11.1), y_range=Range1d(-11.1, 11.1), title=str(title), plot_width=400, plot_height=400)
           
        network_graph = from_networkx(
            network, nx.spring_layout, scale=10, center=(0, 0))
        network_graph.node_renderer.glyph = Circle()
        network_graph.edge_renderer.glyph = MultiLine(
            line_alpha=0.5, line_width=1)
        plot.renderers.append(network_graph)
        return plot

    tabs = []

    for i in range(2000, 2021):
        grid = row([get_network_plot(Faculty.graph_years[i], f"Collaborations in {i} from SCSE"), get_network_plot(
            Faculty.graph_years_all[i], f"Collaborations in {i} from all the papers")])
        tabs.append(Panel(child=grid, title=str(i)))

    text = f"""<h3>Collaboration for {name}</h3><hr/>"""
    div = Div(text=text, width=500, height=100)

    tab = Tabs(tabs=tabs)
    disp = layout([div, tab])

    return disp


def startingHtml():
    text = """<h1>Network Science</h1>
    <div>
    In an attempt to understand the collaboration between the different professors.
    This page contains : 
    <ul>
        <li>Network Graph for collaboration between different professors in SCSE from 2000</li>  
        <li>Graph and information regarding a particular professor</li>  
    <ul/>  
    </div>"""
    div = Div(text=text, width=500, height=100)
    return div

def overall_information_graphs(Year_Graph ):
    def get_average_degree_plot(title = "Average Degree"):
        l1 = []
        l2 = []
        for i in range(2000,2021):
            l1.append(i)
            l2.append(Year_Graph[i].year_info['average_degree'])
        p = figure(title=title, plot_width=400, plot_height=400,
               y_axis_type="log", x_axis_type="log", toolbar_location = None)
        p.vbar(x = l1, top = l2, line_width=2)
        return p

    def get_average_clustering_plot(title = "Average Clustering Coefficient"):
        l1 = []
        l2 = []
        for i in range(2000,2021):
            l1.append(i)
            l2.append(Year_Graph[i].year_info['average_clustering_coefficient'])
        p = figure(title=title, plot_width=400, plot_height=400,
               y_axis_type="log", x_axis_type="log", toolbar_location = None)
        p.vbar(x = l1, top = l2, line_width=2)
        return p

    t1 = get_average_degree_plot()
    t2 = get_average_clustering_plot()
    return layout([t1,t2])
    

def show_html(Year_Graph, name=None, Faculty=None):
    years_scse = generate_tab_year(Year_Graph)
    faculty = generate_faculty(Faculty, name)
    properties = overall_information_graphs(Year_Graph)
    panel_list = []
    panel_list.append(Panel(child = years_scse, title = "Year Wise Analysis"))
    panel_list.append(Panel(child = faculty, title = "Faculty Collaborations"))
    panel_list.append(Panel(child = properties, title = "Analysis"))
    tab = Tabs(tabs = panel_list)
    l = [startingHtml(), tab]
    disp = layout(l)
    show(disp)
