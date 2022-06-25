import bs4
import urllib.request
import pandas as pd
from io import StringIO
from sqlalchemy import create_engine
from re import search 
from constants import BUOYS,URL,FILE_URL


def return_soup(link):
    page = urllib.request.urlopen(link).read()
    return bs4.BeautifulSoup(page, 'html.parser')    


soup = return_soup(URL)
all_a = soup.find_all('a', href=True)

files_urls = [x for x in [a['href'] for a in all_a if FILE_URL in a['href']]]

data_urls_dict = {}
for buoy in BUOYS:
    data_urls_dict[buoy] = [x for x in [y for y in files_urls if search(buoy, y)]][0]


for key, value in data_urls_dict.items():
    dataSoup = return_soup(value)
    data = dataSoup.get_text()
    ioData = StringIO(data)

    df_temp = pd.read_csv(ioData, sep=",")
    
    if df_temp.columns[0]=='Unnamed: 0':
        df_temp = df_temp.drop(['Unnamed: 0'], axis=1)
    
    try:
        df_temp = df_temp.set_index('Datetime')
    except:
        df_temp = df_temp.rename(columns={'# Datetime':'Datetime'})
        df_temp = df_temp.set_index('Datetime')
    
    

    engine = create_engine('sqlite:///database.db')
    conn = engine.connect()

    try:
        df = pd.read_sql(key,con=conn)
        df = df.set_index('Datetime')
        df = pd.concat([df,df_temp]).drop_duplicates()
        df_temp.to_sql(key, con=conn, if_exists='replace')
        print(key, 'inserida no db')
    except:
        df_temp.to_sql(key, con=conn, if_exists='replace')