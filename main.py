from preprocess import fetch_faculty
from faculty import Year, Faculty
from interface import getApp as gp

import argparse

if __name__ == "__main__":  
    year_graph = {}

    print("Building Year Dataset")
    for i in range(2000,2022):
        year_graph[i] = Year(i)

    app = gp(year_graph)
    app.run_server(debug=True)




