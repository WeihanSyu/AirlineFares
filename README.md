# AirlineFares Project
## Summary
* Create a program that outputs airline ticket information from popular airfare sites based on end user inputs (travel class, location, dates, etc.).
* The outputs will always give the top N cheapest available flights which will be compared visually through Tableau Dashboards.
* The program mainly uses Python language with SQL Server as the backend.

## python_modules
This folder contains the main Python scripts that will web scrape the airfare information from various websites, store them in SQL Server, and upload into excel sheets for Tableau use.
<details>
<summary><b>expedia_scrape.py</b></summary>

**class expedia_flight:**
* Using BeautifulSoup and Selenium with Google Chrome as the browser of choice, this *class* will scrape expedia.ca for their airfare information.
* **Method** ***get_ticket_info*** is our web scraper and comes with default parameters that an airfare site might use to get ticket information. The end user will be able to put in their own arguments during runtime.
* Dictionary *flight_inputs* stores a couple of key words and actions that seem to be common across multiple airfare sites and will be called upon during scraping.
* Next, we handle any invalid end user inputs as each airfare site can only take certain inputs. This is done before we even request the webpage just so we are not opening the page and closing everytime
we have an invalid input. Of course this means we checked out the websites beforehand and hopefully, they don't change too often.
* Now request the webpage.
* For the scraping, we are just going section to section, mainly using XPATH in conjunction with our inputs to fill in the categories before clicking "search".
* After searching and checking if there are any available flights, we use a *css_selector* to find and separate each group of individual tickets and then use RegEx to get the info that we want and place them into lists.
* <details>
  <summary>Code snippet</summary>

  ```python
  ticket_css_selector = '.uitk-card-has-primary-theme .uitk-card-content-section-padded .uitk-card-link'
  content = browser.find_elements_by_css_selector(ticket_css_selector)
  for e in content:
      start = e.get_attribute('innerHTML')
      soup = bs(start, features='lxml')
      raw = soup.get_text().strip()

      x = re.sub("[a-zA-Z ]*information for ", "", raw) 
      m = re.search("flight", x)
      airline.append( x[:m.start()].strip() )
  ```
  </details>

* Note that everytime an error happens during runtime, we close the browser *browser.quit()* and exit our function *sys.exit()* so we can start blank again.
* **Method** ***info_to_sql(self, ticket):*** is called upon to place our scraped ticket info into SQL Server. 
* We first clean up the raw outputs and make sure they match the data type for their corresponding columns in our SQL tables.
* Then we use *cursor.executemany* from *pyodbc* module to bulk insert our ticket info into SQL table.
* Commit the code to end.
* **Note:** I don't think we need the insert into ***##tmp_table?***
</details>

<details>
<summary><b>kayak_scrape.py</b></summary>

**class kayak_flight:**
* Pretty much the same methods as with our expedia scraper above. Only some small differences in how we find the elements and deal with the page.
</details>

<details>
<summary><b>sql_to_excel_v2.py</b></summary>

* This module will upload our airfare tables in SQL to an Excel sheet.
* We use pandas dataframes to modify our data a bit, make them easier to use in a visualization.
* TO avoid overwriting existing data in our Excel sheets, we first check if there is already data and if there is, we drop the *id* column and *concat* the new table data onto the old table.
* Use *pd.ExcelWriter* with *mode = a* and *if_sheet_exists='replace'*, then add a new *id* column restarting from 0.
* <details>
  <summary>Code snippet</summary>

  ```python
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
  ```
  </details>

</details>

## sql_scripts
This folder contains all the SQL side setup.
<details>
<summary><b>ticket_info_v2.sql</b></summary>

* Beyond the table set up, we also created triggers for each airfare table which checks after every new insert if the row_id is greater than 1000.
* If it is, then we reset the auto incremented id to start back from 0.
* We do this because auto incremented id's won't reset on it's own and will just keep getting larger and I don't want gigantic numbers stuck in the table.
* Obviously this means we are also periodically deleting older entries otherwise we will go over 1000 actual entries and run into trouble with this trigger.
</details>

<details>
<summary><b>job_delete_old_ticket.sql</b></summary>

* As the filename suggests, this script creates a *SQL Job Agent* that will automatically delete entries older than a given timeframe (set by user - currently 1 week)
* The script can be set to run starting at any future date and time chosen. As long as **SQL Server and SQL Server Agent** Services are running on the PC.
</details>

## jupyter_scripts
We use jupyter notebooks for convenience and did most of the testing here so only *ticket_to_sql_to_excel_v2* is actually used in the program.
<details>
<summary><b>ticket_to_sql_to_excel_v2.ipynb</b></summary>

* This file is the one that puts everything together and calls the scraper functions, stores it into SQL, and places the data into Excel sheets for Tableau use. Just make sure the other files are either on the same path, or have been added to path like we did.
* ***args*** is where all the user inputs go and is the only thing that may be changed between runs besides ***ChromeOptions*** on rare occasions.
* ***ChromeOptions*** is where we add the path to our *chromedriver* as well as set up any methods that can help with avoiding bot detection.