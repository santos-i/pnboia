from datetime import date, datetime
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

# select only buoys urls
files_urls = [x for x in [a['href'] for a in all_a if FILE_URL in a['href']]]

# create a dict with key = name of buoy, value = direct link
data_urls_dict = {}
for buoy in BUOYS:
    data_urls_dict[buoy] = [x for x in [y for y in files_urls if search(buoy, y)]][0]


df_status = pd.DataFrame()

for key, value in data_urls_dict.items():
    dataSoup = return_soup(value)
    data = dataSoup.get_text()
    ioData = StringIO(data)

    df_temp = pd.read_csv(ioData, sep=",")
    
    if df_temp.columns[0]=='Unnamed: 0':
        df_temp = df_temp.drop(['Unnamed: 0'], axis=1)
    
    try:
        df_temp = df_temp.set_index('Datetime').sort_index(ascending=False)
    except:
        df_temp = df_temp.rename(columns={'# Datetime':'Datetime'})
        df_temp = df_temp.set_index('Datetime').sort_index(ascending=False)

    # create df_status
    last_aquisition = df_temp.iloc[[0]].index[0]
    date_of_last_aquisition = datetime.strptime(last_aquisition, '%Y-%m-%d %H:%M:%S').date()
    today = date.today()

    if (today - date_of_last_aquisition).days <= 7:
        status = 'Operacional'
    else: status = 'Manutenção'
    
    dic= {'buoy':[key], 'status':[status], 'last_aquisition':[last_aquisition]}
    df_fromDic = pd.DataFrame.from_dict(dic)
    df_status = pd.concat([df_status, df_fromDic], ignore_index=True)

    # create connection sql
    engine = create_engine('sqlite:///database.db')
    conn = engine.connect()

    df_temp.to_sql(key, con=conn, if_exists='replace')
    print(key, 'inserido no db')
        
df_status = df_status.sort_values('last_aquisition', ascending=False, ignore_index=True)
df_status.to_sql('buoyStatus', con=conn, if_exists='replace')
print('status inserido no db')