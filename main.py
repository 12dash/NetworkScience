from preprocess import fetch_faculty
from faculty import Year, Faculty
from interface import show_html
from interface_new import getApp

import argparse

if __name__ == "__main__":

    FACULTY, NAMES = fetch_faculty()    

    year_graph = {}

    for i in range(2000,2021):
        year_graph[i] = Year(i, NAMES, FACULTY)

    #name = args.name
    name = "Bo An"
    if name != None:
        faculty = Faculty(name)

    #show_html(year_graph,name, faculty)
    app = getApp(year_graph)
    app.run_server(debug=True)




