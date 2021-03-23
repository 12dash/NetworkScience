import xml.etree.ElementTree as ET
import os
import pandas as pd

FACULTY_DF = pd.read_csv("Faculty.csv")

class PublishedPaper:

    def __init__(self, xml_raw):
        self.xml_raw = xml_raw 

        self.authors = []
        self.title = None
        self.year = None
        self.paper_type = None        

        self.fetch_info() 
        
    def fetch_info(self):
        for x in self.xml_raw.iter():
            if x.tag == "article":
                self.paper_type = "journal"
            elif x.tag == "inproceedings":
                self.paper_type = "conference"            
            if x.tag == "author":
                self.authors.append(x.text)
            elif x.tag == "year":
                self.year = (int)(x.text)
            elif x.tag == "title":
                self.title = x.text   
       

class Faculty:

    name = None
    xml_path = None
    position = None
    gender = None
    managment = None
    xml = None
    area = None

    papers = []

    def __init__(self,name):

        self.name = name
        self.xml_path = f"./Data/{name}.xml"

        self.get_data_df()
        self.load_xml()
        self.parse_xml()
        
    
    def get_data_df(self):

        row = FACULTY_DF[FACULTY_DF["Faculty"]==self.name]

        self.gender = row.Gender.to_list()[0]
        self.position = row.Position.to_list()[0]
        self.managment = row.Management.to_list()[0]
        self.area = row.Area.to_list()[0]

        return

    def load_xml(self):
        self.xml = ET.parse(self.xml_path)
        return
    
    def parse_xml(self):
        root = self.xml.getroot()
        for x in root:            
            if(x.tag == 'r'):
                self.papers.append(PublishedPaper(x))
        return

    def printFaculty(self):
        print(f"{self.name}\t\t{self.gender}\t\t{self.position}\t\t{self.managment}\t\t{self.area}")
        return

def fetch_faculty():
    faculty_names = (os.listdir("./Data"))
    faculty_names = [i[:i.rfind(".")] for i in faculty_names]
    faculty = {}
    for i in faculty_names:
        faculty[i] = Faculty(i)
    return faculty, faculty_names


if __name__=="__main__":
    faculty_names = (os.listdir("./Data"))
    faculty_names = [i[:i.rfind(".")] for i in faculty_names]
    faculty = {}
    for i in faculty_names:
        faculty[i] = Faculty(i)
    
        

