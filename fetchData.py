import pandas as pd
from tqdm import tqdm
import requests
import threading

def save_file(url,name):
    try:
        response = requests.get(url)
        with open(f'./AdditionalData/{name}.xml', 'wb') as file:
            file.write(response.content)
    except Exception as e:
        print(e)

def fetch(urls, names):
    base_url = "https://dblp.org/pid/"   
    n = 0
    for i in range(len(urls)):
        save_file(base_url+urls[i]+".xml",names[i])   
        if int(i/len(urls)) != n:        
            n = int(i/len(urls))   
            print(n*10)  
          

if __name__ =="__main__":
    
    df = pd.read_csv("Additional.csv")
    print("Number of People : ",len(df))    

    l2 = df.Pid.to_list()
    l1 = df.Name.to_list()

    n, p = [], []

    k = 200
    for i in range(len(l1)//k):
        n.append(l1[(i)*k:(i+1)*k])
        p.append(l2[(i)*k:(i+1)*k])
    
    n.append(l1[(i+1)*k:])
    p.append(l2[(i+1)*k:])

    t = [threading.Thread(target=fetch, args=(p[i],n[i],)) for i in range(len(n))]

    for i in t:
        i.start()
    
    for i in t:
        i.join()

    print("Done Fetching")



 
    

