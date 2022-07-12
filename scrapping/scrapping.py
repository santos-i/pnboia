from datetime import date, datetime, timedelta
import bs4
import urllib.request
import pandas as pd
from io import StringIO
from re import search 
from constants import BUOYS,URL,FILE_URL
from sqlalchemy import create_engine
# import psycopg2


db = create_engine('postgresql://postgres:Senha.123@localhost:5432/pnboia')
conn = db.connect()

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


    df_temp.columns = [x.lower() for x in list(df_temp.columns)]

    """
    12: ['lat', 'lon', 'wspd', 'wdir', 'wtmp', 'wvht', 'dpd', 'mwd', 'spred', 'peak_mwd', 'peak_spred', 'mean_dpd'], 
    11: ['condutividade', 'direcao_vento', 'latitude', 'longitude', 'pressao_atm', 'rad_solar', 'salinidade', 'temp_agua', 'temp_ar', 'umidade', 'velocidade_vento'], 
    27: ['lat', 'lon', 'battery', 'compass', 'wspd', 'gust', 'wdir', 'atmp', 'dewpt', 'rh', 'pres', 'arad', 'sst', 'cspd1', 'cdir1', 'cspd2', 'cdir2', 'cspd3', 'cdir3', 'swvht1', 'tp1', 'mxwvht1', 'wvdir1', 'wvspread1', 'swvht2', 'tp2', 'wvdir2'], 
    23: ['lat', 'lon', 'battery', 'bhead', 'wspd', 'wdir', 'gust', 'atmp', 'pres', 'dewp', 'humi', 'wtmp', 'cvel1', 'cdir1', 'cvel2', 'cdir2', 'cvel3', 'cdir3', 'wvht', 'wmax', 'dpd', 'mwd', 'spread']}
    """

    # 1 boia
    df_11_cols = ['condutividade', 'wdir', 'lat', 'lon','pres', 'rad_solar', 'sal', 'wtmp', 'atmp','humi', 'wdir']
    # 8 boias
    df_12_cols = ['lat', 'lon', 'wspd', 'wdir', 'wvtmp', 'wvht', 'dpd', 'wvdir', 'spred','peak_mwd', 'peak_spred', 'mean_dpd']
    # 13 boias
    df_23_cols = ['lat', 'lon', 'battery', 'bhead', 'wspd', 'wdir', 'gust', 'atmp','pres', 'dewp', 'humi', 'wvtmp', 'cvel1', 'cdir1', 'cvel2', 'cdir2','cvel3', 'cdir3', 'wvht', 'mxwvht', 'dpd', 'wvdir', 'spread']
    # 3 boias
    df_27_cols = ['lat', 'lon', 'battery', 'compass', 'wspd', 'gust', 'wdir', 'atmp','dewpt', 'rh', 'pres', 'arad', 'wvtmp', 'cspd1', 'cdir1', 'cspd2','cdir2', 'cspd3', 'cdir3', 'wvht', 'dpd', 'mxwvht1', 'wvdir','wvspread', 'swvht2', 'tp2', 'wvdir2']
    
    df_cols_new = ['lat', 'lon', 'wspd', 'wdir', 'wvtmp', 'wvht', 'wvdir', 'dpd']
    
    if len(df_temp.columns) != 11: 

    
        if len(df_temp.columns) == 12:
            df_temp.columns = df_12_cols
            df_temp = df_temp[df_cols_new]
        if len(df_temp.columns) == 23:
            df_temp.columns = df_23_cols
            df_temp = df_temp[df_cols_new]
        if len(df_temp.columns) == 27:
            df_temp.columns = df_27_cols
            df_temp = df_temp[df_cols_new]


        # create df_status
        last_aquisition = df_temp.iloc[[0]].index[0]
        date_of_last_aquisition = datetime.strptime(last_aquisition, '%Y-%m-%d %H:%M:%S').date()
        today = date.today()

        if (today - date_of_last_aquisition).days <= 7:
            status = 'Operacional'
        else: status = 'Manutenção'
        
        if key == '_potter':
            key = 'potter'

        dic= {'buoy':[key], 'status':[status], 'last_aquisition':[last_aquisition]}

        df_fromDic = pd.DataFrame.from_dict(dic)
        df_status = pd.concat([df_status, df_fromDic], ignore_index=True)
        try:
            df_last = pd.read_sql(f'SELECT * FROM {key};',con=conn)
            df_last = df_last.set_index('Datetime')
            df_temp = pd.concat([df_last, df_temp], ignore_index=False)
        except:
            pass

        df_temp = df_temp.drop_duplicates()
        df_temp = df_temp.sort_index(ascending=False)
        
        #limitar em 1 ano de dado
        # df_temp.index = pd.to_datetime(df_temp.index)
        # df_temp = df_temp[df_temp.index >= df_temp.index[0]- timedelta(days=365)]
        
        df_temp.to_sql(name=key, con=conn, if_exists='replace')
        print(key, 'ok')


df_status = df_status.sort_values('last_aquisition', ascending=False, ignore_index=True)
df_status.to_sql(name='buoyStatus', con=conn, if_exists='replace')
print('dfstatus ok')
