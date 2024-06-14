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
**Note:** I don't think we need the insert into ***##tmp_table?***
</details>

<details>
<summary><b>kayak_scrape.py</b></summary>


</details>





