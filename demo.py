import pandas as pd 
import requests 
from bs4 import BeautifulSoup
from datetime import datetime

url = 'https://web.archive.org/web/20230908091635 /https://en.wikipedia.org/wiki/List_of_largest_banks'

def extract(url):
    web_page = requests.get(url).text
    data = BeautifulSoup(web_page , 'html.parser')
    count = 0
    tables = data.find_all('table')

    if len(tables) >= 2:
        table = tables[1]
        tbody = table.find('tbody')
        rows = tbody.find_all('tr')

        df = pd.DataFrame(columns=["Rank" , "Bank Name" , "Total Assests"])

        for row in rows[1:] :
            if count <= 50 :
                colums = row.find_all(['th' , 'td'])
                if len(colums) < 4 :
                 data_dict = {
                        "Rank" : colums[0].text.strip(),
                        "Bank Name" : colums[1].text.strip(),
                        "Total Assests" : colums[2].text.strip()
                    }
                 df2 = pd.DataFrame(data_dict , index=[0])
                 df = pd.concat([df , df2] , ignore_index=True)
                 count = count+1

        return df 
    
df = extract(url)
                

# extract(url)
exchange_rate_path = 'exchange_rate.csv'       

def transform(df , csv_path):
   
   exchange_rates = pd.read_csv(csv_path)
   conveersion_rates = {}
   for index,row in exchange_rates.iterrows():
      conveersion_rates[row['Currency']] = row['Rate']

   for currency , rate in conveersion_rates.items():
      new_column_name = f'Toatl Assets ({currency})'
      df[new_column_name] = df['Total Assests'].apply(lambda x : float(x.replace(',','').replace('$','')) * rate)
   return df
   


df3 = transform(df , exchange_rate_path)
print(df3)
      

