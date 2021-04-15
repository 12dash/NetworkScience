# -*- coding: utf-8 -*-
"""
Created on Mon Apr 12 04:46:05 2021

@author: 18moh
"""

from preprocess import fetch_faculty
from faculty import Year, Faculty
from interface import getApp as gp

class ManageGraph:
    
    def __init__(self):
        faculty, names = fetch_faculty()
        
        self.nodes=[]
        self.edges=[]
        
        for x in faculty:
            if(faculty[x].managment==True):
                self.nodes.append(x)
                
                p=faculty[x].papers
                for y in p:
                    for a in y.authors:
                        if(a in names):
                            self.edges.append((x, a))
        
        
        
        
class PositionGraph:
    
    #target='Lecturer'
    
    def __init__(self, target):
        faculty, names = fetch_faculty()
        
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
                        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
