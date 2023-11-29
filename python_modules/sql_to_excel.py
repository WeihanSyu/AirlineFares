import pandas as pd
from sqlalchemy import text
import re

def sql_excel(conn):

    sql = "SELECT * FROM all_ticket;"
    df = pd.read_sql(sql, conn)

    price_index_expedia = df.columns.get_loc('e_price')
    for i in range(len(df['e_price'])):
        if df['e_price'][i] != None:
            x = re.findall('\$.*', df['e_price'][i])[0][1:]
            y = int(re.sub(',','',x))
            df.iloc[i, price_index_expedia] = y
        else:
            pass
        
    price_index_kayak = df.columns.get_loc('k_price')
    for i in range(len(df['k_price'])):
        if df['k_price'][i] != None:
            x = re.findall('\$.*', df['k_price'][i])[0][1:]
            y = int(re.sub(',','',x))
            df.iloc[i, price_index_kayak] = y
        else:
            pass

    try:
        existing_df = pd.read_excel('airfare_tables_2.xlsx', sheet_name='all_ticket')
        existing_df = existing_df.drop(columns=(['id']))
        df = pd.concat([existing_df, df], ignore_index=True)
        
        # I don't why our "date" type columns sometimes change to "datetime" after concatenation
        df['e_going_date'] = pd.to_datetime(df['e_going_date']).dt.date
        df['e_return_date'] = pd.to_datetime(df['e_return_date']).dt.date
        df['k_going_date'] = pd.to_datetime(df['k_going_date']).dt.date
        df['k_return_date'] = pd.to_datetime(df['k_return_date']).dt.date
        
        with pd.ExcelWriter('airfare_tables_2.xlsx', 
                        mode='a',
                        if_sheet_exists='replace',
        ) as writer:
            df.to_excel(writer, sheet_name='all_ticket', index=True, index_label='id')
    except:
        with pd.ExcelWriter('airfare_tables_2.xlsx', 
                        mode='w',
        ) as writer:
            df.to_excel(writer, sheet_name='all_ticket', index=True, index_label='id')
        
    conn.execute(text("DROP TABLE dbo.all_ticket"))


