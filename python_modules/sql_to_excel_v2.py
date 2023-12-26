import pandas as pd
from sqlalchemy import text
import re

def sql_excel(conn):

    # Upload expedia table to Excel
    sql = "SELECT date_scrape, airline, ticket_type, ticket_class, origin, destination,\
        going_stops, going_date, going_time, going_arrive_time, going_travel_time, return_date, price\
        FROM expedia;"
    df = pd.read_sql(sql, conn)
    
    col_website = ['expedia']*len(df['price'])
    df.insert(0, 'website', col_website, allow_duplicates=True)
    
    price_index_expedia = df.columns.get_loc('price')
    for i in range(len(df['price'])):
        if df['price'][i] != None:
            x = re.findall('\$.*', df['price'][i])[0][1:]
            y = int(re.sub(',','',x))
            df.iloc[i, price_index_expedia] = y
        else:
            pass

    try:
        existing_df = pd.read_excel('airfare_tables.xlsx', sheet_name='tickets')
        existing_df = existing_df.drop(columns=(['id']))
        df = pd.concat([existing_df, df], ignore_index=True)

        df['going_date'] = pd.to_datetime(df['going_date']).dt.date
        df['return_date'] = pd.to_datetime(df['return_date']).dt.date

        with pd.ExcelWriter('airfare_tables.xlsx', 
                        mode='a',
                        if_sheet_exists='replace',
        ) as writer:
            df.to_excel(writer, sheet_name='tickets', index=True, index_label='id')
    except:
        with pd.ExcelWriter('airfare_tables.xlsx', 
                        mode='w',
        ) as writer:
            df.to_excel(writer, sheet_name='tickets', index=True, index_label='id')

    
    # Upload kayak table to Excel
    sql = "SELECT date_scrape, airline, ticket_type, ticket_class, origin, destination,\
        going_stops, going_date, going_time, going_arrive_time, going_travel_time,\
        return_stops, return_date, return_time, return_arrive_time, return_travel_time, price\
        FROM kayak;"
    df = pd.read_sql(sql, conn)

    col_website = ['kayak']*len(df['price'])
    df.insert(0, 'website', col_website, allow_duplicates=True)
    
    price_index_kayak = df.columns.get_loc('price')
    for i in range(len(df['price'])):
        if df['price'][i] != None:
            x = re.findall('\$.*', df['price'][i])[0][1:]
            y = int(re.sub(',','',x))
            df.iloc[i, price_index_kayak] = y
        else:
            pass

    try:
        existing_df = pd.read_excel('airfare_tables.xlsx', sheet_name='tickets')
        existing_df = existing_df.drop(columns=(['id']))
        df = pd.concat([existing_df, df], ignore_index=True)

        df['going_date'] = pd.to_datetime(df['going_date']).dt.date
        df['return_date'] = pd.to_datetime(df['return_date']).dt.date

        with pd.ExcelWriter('airfare_tables.xlsx', 
                        mode='a',
                        if_sheet_exists='replace',
        ) as writer:
            df.to_excel(writer, sheet_name='tickets', index=True, index_label='id')
    except:
        with pd.ExcelWriter('airfare_tables.xlsx', 
                        mode='w',
        ) as writer:
            df.to_excel(writer, sheet_name='tickets', index=True, index_label='id')
