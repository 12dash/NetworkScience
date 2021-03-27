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
               y_axis_type="log", x_axis_type="log")
    p.line(l1, l2, line_width=2)
    return p


def generate_year_graph(network, title="Years"):

    size_by_this_attribute = 'adjusted_node_size'
    color_by_this_attribute = 'adjusted_node_size'

    color_palette = Viridis8

    HOVER_TOOLTIPS = [("Faculty", "@index"), ("Degree", "@degree"),
                      ("Betweenness Centrality", "@betweenness"),
                      ("Clustering Coefficient", "@clustering")]

    plot = figure(tooltips=HOVER_TOOLTIPS, tools="pan,wheel_zoom,save,reset", active_scroll='wheel_zoom',
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


def generate_tab_year(graphs):
    def get_first_row(temp):
        def get_div():
            text = f"""
            <div>
            <h4>Network Properties</h4>
            <ul>
                <li>Average Clustering Coefficient : {temp.year_info['average_clustering_coefficient']}</li>
                <li>Average Degree : {temp.year_info['average_degree']}</li>                
            </ul>
            </div>
            """
            div = Div(text=text, width=500, height=100)
            return div

        year_collab = generate_year_graph(
            temp.graph_year, f"Collaborations in {i}")
        degree_distribution = get_degree_distribution(
            temp.graph_year, "Degree Distribution")
        return row([year_collab, degree_distribution, get_div()])

    text = """<h3>Collaboration over years</h3><hr/>"""
    div = Div(text=text, width=500, height=100)
    tabs = []

    for i in range(2000, 2021):
        temp = graphs[i]
        row_1 = get_first_row(temp)

        grid = layout([row_1, generate_year_graph(
            temp.graph_previous_years, f"Collaborations from 2000 to {i}")])
        tabs.append(Panel(child=grid, title=str(i)))

    tab = Tabs(tabs=tabs)
    disp = layout([div, tab])

    return disp


def generate_faculty(Faculty, name):
    def get_network_plot(network, title):

        HOVER_TOOLTIPS = [("Faculty", "@index")]

        plot = figure(tooltips=HOVER_TOOLTIPS,tools="pan,wheel_zoom,save,reset", active_scroll='wheel_zoom',
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
            Faculty.graph_years_all[i], f"Collaborations in {i}")])
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


def show_html(Year_Graph, name=None, Faculty=None):
    years_scse = generate_tab_year(Year_Graph)
    faculty = generate_faculty(Faculty, name)
    l = [startingHtml(), years_scse, faculty]
    disp = layout(l)
    show(disp)
