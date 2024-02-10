import pandas as pd 
import requests 
from bs4 import BeautifulSoup
from datetime import datetime
import sqlite3

url = 'https://web.archive.org/web/20230908091635 /https://en.wikipedia.org/wiki/List_of_largest_banks'
final_path = 'transformed_path.csv'
log_file = 'Activity.text'
def extract(url):
    web_page = requests.get(url).text
    data = BeautifulSoup(web_page , 'html.parser')
    count = 0
    tables = data.find_all('table')

    if len(tables) >= 2:
        table = tables[1]
        tbody = table.find('tbody')
        rows = tbody.find_all('tr')

        df = pd.DataFrame(columns=["Rank" , "Bank_Name" , "Total_Assests"])

        for row in rows[1:] :
            if count <= 10 :
                colums = row.find_all(['th' , 'td'])
                if len(colums) < 4 :
                 data_dict = {
                        "Rank" : colums[0].text.strip(),
                        "Bank_Name" : colums[1].text.strip(),
                        "Total_Assests" : colums[2].text.strip()
                    }
                 df2 = pd.DataFrame(data_dict , index=[0])
                 df = pd.concat([df , df2] , ignore_index=True)
                 count = count+1

        return df 
    
# df = extract(url)
                

# extract(url)
exchange_rate_path = 'exchange_rate.csv'       

def transform(df , csv_path):
   exchange_rate = pd.read_csv(csv_path)
   conversion_rates = {}
   for index , row in exchange_rate.iterrows() :
      conversion_rates[row['Currency']]=row['Rate']

   for Currency , rate in conversion_rates.items():
      new_column_name = f"MC_{Currency}_Billion"
      df[new_column_name]= round(df['Total_Assests'].apply(lambda x : float(x.replace(",","").replace("$","") )* rate))
   return df


# df3 = transform(df , exchange_rate_path)
# print(df3)
      
def load_to_csv(df , output_path ):
   df.to_csv(output_path)

# load_to_csv(df , final_path)

tabel_name = 'World_largest_bank'
sql_connection = sqlite3.connect('world_bank.db')
def load_to_db(df , sql_connection , tabel_name):
   Attribute = ["Rank" , "Bank_Name" , "Total_Assests" ,"MC_EUR_Billion" , "MC_GBP_Billion","MC_INR_Billion"]
   df2 = pd.read_csv(df , names=Attribute)
   df2.to_sql( tabel_name , sql_connection , if_exists='replace' , index=False )

# load_to_db(final_path,sql_connection,tabel_name)


# query_statemrnt = f'select Rank from {tabel_name}'
def run_query(query_statement , sql_connection):
   query_exexction = pd.read_sql(query_statement , sql_connection ) 
   print(query_exexction)


# run_query(query_statemrnt, sql_connection)

def log_progress(message):
   timestamp_format  = '%Y-%h-%d-%H:%M:%S'
   now = datetime.now()
   time_stamp = now.strftime(timestamp_format)
   with open (log_file , 'a') as f :
      f.write(time_stamp + "," + message + "\n")

log_progress("ETL Job Started")
log_progress("Extract phase Started")
extracted_data =  extract(url)
log_progress("Extract phase Ended") 
log_progress("Transform phase Started") 
transformed_data = transform(extracted_data , exchange_rate_path)
print("Transformed Data") 
print(transformed_data) 
log_progress("Transform phase Ended") 
log_progress("Load phase Started") 
load_to_csv(extracted_data , final_path)
log_progress("Load phase Ended") 
log_progress("Load To DataBase phase Started") 
load_to_db(final_path,sql_connection,tabel_name)
log_progress("Load TO DataBase phase Ended") 
log_progress("Extract from  DataBase phase Started") 
run_query(f'SELECT * FROM {tabel_name}', sql_connection)
run_query(f'SELECT AVG(MC_GBP_Billion) FROM {tabel_name}', sql_connection)
run_query(f'SELECT Bank_Name from {tabel_name} LIMIT 5', sql_connection)
log_progress("Extract from  DataBase phase Ended") 
log_progress("ETL Job Ended") 
  
