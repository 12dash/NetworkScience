import dash
import dash_bootstrap_components as dbc
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output
import dash_cytoscape as cyto
import plotly.express as px

from collections import Counter

import networkx as nx
import pandas as pd

app = dash.Dash(external_stylesheets=[dbc.themes.BOOTSTRAP], suppress_callback_exceptions=True)
cyto.load_extra_layouts()

YEAR_GRAPH = None
# the style arguments for the sidebar. We use position:fixed and a fixed width
SIDEBAR_STYLE = {
    "position": "fixed",
    "top": 0,
    "left": 0,
    "bottom": 0,
    "width": "18rem",
    "padding": "2rem 1rem",
    "background-color": "#f8f9fa",
}

# the styles for the main content position it to the right of the sidebar and
# add some padding.
CONTENT_STYLE = {
    "margin-left": "18rem",
    "margin-right": "2rem",
    "padding": "2rem 1rem",
}

YEAR_GRAPH_STYLESHEET = [
    {
        'selector': 'node',
        'style': {            
            'width': "data(size)",
            'height': "data(size)",
            
        }
    }
]

def createContent():
    content = html.Div(id="page-content", style=CONTENT_STYLE)
    return content

def applyLayout(app):
    sidebar = createSidebar()
    content = createContent()
    app.layout = html.Div([dcc.Location(id="url"), sidebar, content])

def contentHomePage():
    return html.P("This is the content of the home page!")

def generateConnectedComponent(Year):
    l = []
    for i in Year.year_info['connected_components']:
        l.append(generateGraphConnected(i))
    
    div_list = []
    div_l = []
    for i in range(len(l)):
        if (i+1)%3==0:
            div_l.append(l[i])
            div_list.append(div_l)
            div_l = []
        else:
            div_l.append(dbc.Col(l[i]))
    if div_l != []:
        div_list.append(div_l)
    div_list = [dbc.Row(i) for i in div_list]
    return html.Div(div_list)    

def generateGraphConnected(G):
    def getNodes():
        nodes = []
        for node in G.nodes():
            temp = {}
            temp['data'] = {'id':node,'label':node}
            nodes.append(temp)
        return nodes
    
    def getEdges():
        edges = []
        for edge in G.edges():            
            temp = {}
            temp['data'] = {'source':edge[0],'target':edge[1]}
            edges.append(temp)
        return edges

    nodes = getNodes()
    edges = getEdges()
  
    graph = cyto.Cytoscape(
            id='cytoscape-connected',
            style={'width': '300px', 'height': '300px'},
            layout={'name': 'circle'},
            elements=edges+nodes,
            stylesheet=YEAR_GRAPH_STYLESHEET
        )
    return graph

def generateGraph(Year):
    G = Year.graph_year
    def getNodes():
        nodes = []
        for node in G.nodes():
            x, y = G.nodes[node]['pos']
            temp = {}
            temp['data'] = {'id':node,'label':node, 'size' : f"{G.nodes[node]['degree']*5+5}%", 'betweenness':G.nodes[node]['betweenness'], 'degree':G.nodes[node]['degree'], 'clustering':G.nodes[node]['clustering']}
            nodes.append(temp)
        return nodes
    
    def getEdges():
        edges = []
        for edge in G.edges():            
            temp = {}
            temp['data'] = {'source':edge[0],'target':edge[1]}
            edges.append(temp)
        return edges

    nodes = getNodes()
    edges = getEdges()
  
    graph = cyto.Cytoscape(
            id='cytoscape-events',
            layout={'name': 'cose-bilkent'},
            elements=edges+nodes,
            stylesheet=YEAR_GRAPH_STYLESHEET
        )
    return graph

@app.callback(Output('cytoscape-mouseoverNodeData-output', 'children'),
                  Input('cytoscape-events', 'mouseoverNodeData'))
def displayTapNodeData(data):
    if data:
        temp = html.Div([
            html.H3(data['label']),
            html.Ul([
            html.Li(f"Betweeness : { data['betweenness']}"),
            html.Li(f"Degree : { data['degree']}"),
            html.Li(f"Clustering Coefficient : { data['clustering']}")])
        ])
        return temp

@app.callback(Output("yearContent","children"),Input("year_id","value"))
def displayYearContent(year):   
    Year = YEAR_GRAPH[int(year)] 
    def get_information():
        table_header = [ html.Thead(html.Tr([html.Th("Information"), html.Th("Value")]))]
        row1 = html.Tr([html.Td("No. Edges"), html.Td(Year.year_info["number_of_edges"])])
        row2 = html.Tr([html.Td("Average Degree"), html.Td(Year.year_info["average_degree"])])
        row3 = html.Tr([html.Td("Avg Clustering Coefficient"), html.Td(Year.year_info["average_clustering_coefficient"])])        
        row4 = html.Tr([html.Td("Avg Shortest Path Length"), html.Td(Year.year_info["avg_dist"])])
        row5 = html.Tr([html.Td("Density"), html.Td(Year.year_info["density"])])
        row6 = html.Tr([html.Td("No. of Connected Components"), html.Td(Year.year_info["number_of_connected_components"])])

        table_body = [html.Tbody([row1, row2, row3, row4, row5])]
        table = dbc.Table(
                        # using the same table as in the above example
                        table_header + table_body,
                        bordered=True,
                        dark=True,
                        hover=True,
                        responsive=True,
                        striped=True
                    )
        return table
    
    def getDegreeDistribution():
        network = Year.graph_year
        degree = [i[1] for i in nx.degree(network)]
        values = sorted(degree)
        hist = Counter(values)
        total = network.number_of_nodes()
        l1 = []
        l2 = []
        for i in hist:
            l1.append(i)
            l2.append(hist[i])
        l2 = [i/total for i in l2]
        df = pd.DataFrame()
        df['Degree'] = pd.Series(l1)
        df['Probability'] = pd.Series(l2)
        fig = px.line(df, x="Degree", y="Probability", title='Degree Distribution', log_y=True)
        return dcc.Graph(figure = fig)

    graph = generateGraph(Year)
    table = get_information()
    degreeDistribution = getDegreeDistribution()
    row_1 = dbc.Row([dbc.Col(graph),dbc.Col(html.P(id='cytoscape-mouseoverNodeData-output'))],justify="center",align="center")
    conn_comp = generateConnectedComponent(Year)
    output = html.Div([html.H5("Information", style = {"padding-top" : "2px","padding-bottom" : "2px" }),table,html.H5("Year Graph"), row_1,html.H5("Probability Degree Distribution"),
     degreeDistribution,html.H5("Connected Componentes"), conn_comp])
    return output

def contentYearPage():
    option = []
    for i in range(2000,2021):
        temp = {"label" : i, "value" : i}
        option.append(temp)
    
    temp = html.Div([
        html.Label('Year'),
        dcc.Dropdown(
            id="year_id",
            options=option,
            value='2000'
        ), html.Div(id="yearContent")])
    return temp

def createOverallPage():
    def getAverageDegree():
        l1 = []
        l2 = []
        for i in range(2000,2021):
            l1.append(i)
            l2.append(YEAR_GRAPH[i].year_info['average_degree'])
        df = pd.DataFrame()
        df['Year'] = pd.Series(l1)
        df['Average Degree'] = pd.Series(l2)
        fig = px.line(df, x="Year", y='Average Degree', title='Average Degree Over the years')
        return dcc.Graph(figure = fig)
    
    def getAverageClustering():
        l1 = []
        l2 = []
        for i in range(2000,2021):
            l1.append(i)
            l2.append(YEAR_GRAPH[i].year_info['average_clustering_coefficient'])
        df = pd.DataFrame()
        df['Year'] = pd.Series(l1)
        df['Average Clustering'] = pd.Series(l2)
        fig = px.line(df, x="Year", y="Average Clustering", title='Average Clustering Over the years')
        return dcc.Graph(figure = fig)
    
    avg_degree = getAverageDegree()
    avg_clustering = getAverageClustering()
    body = html.Div([avg_degree, avg_clustering])
    return body

def createSidebar():
    sidebar = html.Div(
        [
            html.H2("Network Science", className="display-5"),
            html.Hr(),
            html.P(
                "Analysis on the collaboration of the SCSE Faculties", className="lead"
            ),
            dbc.Nav(
                [
                    dbc.NavLink("Home", href="/", active="exact"),
                    dbc.NavLink("Yearly Analysis",
                                href="/year", active="exact"),
                    dbc.NavLink("Faculty Analysis",
                                href="/faculty_analysis", active="exact"),
                    dbc.NavLink("Overall Information",
                                href="/overall", active="exact"),
                ],
                vertical=True,
                pills=True,
            ),
        ],
        style=SIDEBAR_STYLE,
    )
    return sidebar

@app.callback(Output("page-content", "children"), [Input("url", "pathname")])
def render_page_content(pathname):
    if pathname == "/":
        body = contentHomePage()
        return body
    elif pathname == "/year":
        return contentYearPage()
    elif pathname == "/faculty_analysis":
        return html.P("Faculty Subset analysis")
    elif pathname == "/overall":
        return createOverallPage()
    # If the user tries to reach a different page, return a 404 message
    return dbc.Jumbotron(
        [
            html.H1("404: Not found", className="text-danger"),
            html.Hr(),
            html.P(f"The pathname {pathname} was not recognised..."),
        ]
    )

def getApp(year_graph):
    global YEAR_GRAPH
    YEAR_GRAPH = year_graph
    applyLayout(app)
    return app
