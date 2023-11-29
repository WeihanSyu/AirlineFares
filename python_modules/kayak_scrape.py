from bs4 import BeautifulSoup as bs
from datetime import date
from datetime import datetime
from datetime import timedelta
import pyodbc
import re
import requests
from selenium import webdriver
from selenium.common.exceptions import NoSuchElementException
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import Select
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import sys
import time

class kayak_flight:
    def __init__(self, chrome_driver, chrome_options, conn):
        self.chrome_driver = chrome_driver
        self.chrome_options = chrome_options
        self.conn = conn


    def get_ticket_info(self, type_='roundtrip', class_='economy', leave="yvr", going="tpe", 
                       depart=date.today(), return_=date.today()+timedelta(days=1), 
                       trav=[1,0,0,0,0,0], bags=[1,1], nonstop=False):

        flight_inputs = {'roundtrip': (Keys.ENTER),
                         'one-way': (Keys.UP, Keys.ENTER),
                         'multi-city': (Keys.DOWN, Keys.ENTER),
                        'economy': 'Economy', 'premium economy': 'Premium Economy',
                        'business class': 'Business', 'first class': 'First'}

        class_action = {'economy': (Keys.ESCAPE), 'premium economy': (Keys.DOWN, Keys.ENTER),
                        'business class': (Keys.DOWN, Keys.DOWN, Keys.ENTER), 
                        'first class': (Keys.DOWN, Keys.DOWN, Keys.DOWN, Keys.ENTER)}
        
        ### Handle out of bound dates ###################################################################################
        if (depart - date.today()).days < 0:
            sys.exit("Depart date cannot be earlier than current date")
        elif (return_ - depart).days < 0:
            sys.exit("Return date cannot be earlier than depart date")
        elif ((depart - date.today()).days > 360) or ((return_ - date.today()).days > 360):
            sys.exit("Selected dates are too far in the future")
        else:
            pass
        
        ### Handle invalid traveller counts #############################################################################
        if (trav[0] < 1) and (trav[1] < 1):
            sys.exit("Must have at least 1 adult selected")
        elif sum(trav) > 16:
            sys.exit("Total travellers can't exceed 16")
        elif sum(trav[0:2]) > 9:
            sys.exit("Searches cannot have more than 9 adults")
        elif sum(trav[2:]) > 7:
            sys.exit("Searches cannot have more than 7 children")
        elif sum(trav[0:2]) < trav[5]:
            sys.exit("Searches cannot have more lap infants than adults")
        else:
            pass
        
        ### Handle invalid baggage counts ###############################################################################
        if bags[0] > 1:
            sys.exit("Cannot take more than one carry-on bag per traveller")
        elif bags[1] > 2:
            sys.exit("cannot take more than two checked bags per traveller")
        else:
            pass
        
        ### Request the webpage #########################################################################################
        url = "https://www.ca.kayak.com/"
        browser = webdriver.Chrome(self.chrome_driver, options=self.chrome_options)
        # Change the property of the navigator value for webdriver to undefined
        browser.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})") 
        browser.get(url)
        
        ### Select "type" of flight #####################################################################################
        type_selector = WebDriverWait(browser, 5).until(EC.presence_of_element_located((By.CSS_SELECTOR, '.Uczr-mod-alignment-left')))
        type_selector.click()
        time.sleep(0.5)
        ActionChains(browser).send_keys(flight_inputs[type_]).perform()
        time.sleep(0.5)
        
        ### Select Travellers ###########################################################################################
        ActionChains(browser).send_keys(Keys.TAB).perform()
        
        trav_add_xpath = {1: '//input[@aria-label="Adults"]/following-sibling::button',
                         2: '//input[@aria-label="Students"]/following-sibling::button',
                         3: '//input[@aria-label="Youths"]/following-sibling::button',
                         4: '//input[@aria-label="Children"]/following-sibling::button',
                         5: '//input[@aria-label="Toddlers in own seat"]/following-sibling::button',
                         6: '//input[@aria-label="Infants on lap"]/following-sibling::button',
                         7: '//input[@aria-label="Adults"]/preceding-sibling::button'}
        
        if trav[0] == 0:
            for i in range(0, trav[1]):
                trav_add_element = WebDriverWait(browser, 5).until(EC.presence_of_element_located((By.XPATH, trav_add_xpath[2])))
                trav_add_element.click()
            trav_add_element = WebDriverWait(browser, 5).until(EC.presence_of_element_located((By.XPATH, trav_add_xpath[7])))
            trav_add_element.click()
            x = 3
            for traveller_type in trav[2:]:
                for j in range(0, traveller_type):
                    trav_add_element = WebDriverWait(browser, 5).until(EC.presence_of_element_located((By.XPATH, trav_add_xpath[x])))
                    trav_add_element.click()
                x += 1
        else:
            for i in range(0, trav[0] - 1):
                trav_add_element = WebDriverWait(browser, 5).until(EC.presence_of_element_located((By.XPATH, trav_add_xpath[1])))
                trav_add_element.click()
            x = 2
            for traveller_type in trav[1:]:
                for j in range(0, traveller_type):
                    trav_add_element = WebDriverWait(browser, 5).until(EC.presence_of_element_located((By.XPATH, trav_add_xpath[x])))
                    trav_add_element.click()
                x += 1
        
        time.sleep(0.5)
        ActionChains(browser).send_keys(Keys.ESCAPE).perform()
        time.sleep(1)
                    
        ### Select ticket "class" #######################################################################################   
        # Somtimes the select elements show up during runtime and sometimes they don't
        try:
            if class_ != 'economy':
                select = Select(browser.find_element_by_xpath('//select[@aria-label="Cabin Class"]'))
                select.select_by_visible_text(flight_inputs[class_])
                time.sleep(1)
            else:
                class_xpath = '//span[contains(@class, "mod-alignment-left") and contains(text(), "Economy")]'
                class_element = WebDriverWait(browser, 5).until(EC.presence_of_element_located((By.XPATH, class_xpath)))
                class_element.click()
                time.sleep(1)
                ActionChains(browser).send_keys(Keys.ESCAPE).perform()
                time.sleep(1)
        except:
            class_xpath = '//span[contains(@class, "mod-alignment-left") and contains(text(), "Economy")]'
            class_element = WebDriverWait(browser, 5).until(EC.presence_of_element_located((By.XPATH, class_xpath)))
            class_element.click()
            time.sleep(1)
            ActionChains(browser).send_keys(class_action[class_]).perform()
            time.sleep(1)
        
        ### Select baggage ##############################################################################################
        ActionChains(browser).send_keys(Keys.TAB).perform()
    
        bag_add_xpath = {1: '//span[contains(text(), "Carry-on")]/../following-sibling::div//button[@aria-label="Increment"]',
                        2: '//span[contains(text(), "Checked")]/../following-sibling::div//button[@aria-label="Increment"]'}
        x = 1
        for bag_type in bags:
            for i in range(0, bag_type):
                bag_add_element = WebDriverWait(browser, 5).until(EC.presence_of_element_located((By.XPATH, bag_add_xpath[x])))
                bag_add_element.click()
            x += 1
            
        time.sleep(0.5)
        ActionChains(browser).send_keys(Keys.ESCAPE).perform()
        
        ### Select Leaving from and Going to locations ##################################################################
        leave_xpath = '//input[@aria-label="Flight origin input"]'
        leave_element = WebDriverWait(browser, 5).until(EC.presence_of_element_located((By.XPATH, leave_xpath)))
        leave_element.click()
        time.sleep(0.5)
        leave_element.send_keys(Keys.BACKSPACE, Keys.BACKSPACE)
        time.sleep(0.5)
        leave_element.send_keys(leave)
        time.sleep(0.5)
        leave_element.send_keys(Keys.DOWN, Keys.ENTER)
        
        going_xpath = '//input[@aria-label="Flight destination input"]'
        going_element = WebDriverWait(browser, 5).until(EC.presence_of_element_located((By.XPATH, going_xpath)))
        going_element.click()
        time.sleep(0.5)
        going_element.send_keys(Keys.BACKSPACE, Keys.BACKSPACE)
        time.sleep(0.5)
        going_element.send_keys(going)
        time.sleep(0.5)
        going_element.send_keys(Keys.DOWN, Keys.ENTER)
        
        ### Select Departure and Return Dates ###########################################################################
        time.sleep(0.5)
        ActionChains(browser).send_keys(Keys.TAB).perform()
        time.sleep(1)
        
        # Scrape the default display date dynamically
        display_ddmm_depart_xpath = '//span[@aria-label="Start date calendar input"]//span[@aria-live="polite"]'
        display_ddmm_depart = browser.find_element_by_xpath(display_ddmm_depart_xpath).text
        display_year_depart = browser.find_element(By.XPATH, '//div[@class="wHSr-monthName"]').text
        
        dd = int(re.findall("[0-9]+/", display_ddmm_depart)[0][:-1])
        mm = int(re.findall("/[0-9]+", display_ddmm_depart)[0][1:])
        yy = int(re.findall("[0-9]+", display_year_depart)[0])
        
        display_date_depart = date(yy, mm, dd)
        
        # Calculate the difference in months from our desired date vs display
        month_diff_depart = (depart.year - display_date_depart.year)*12 + (depart.month - display_date_depart.month)
        month_diff_return = (return_.year - depart.year)*12 + (return_.month - depart.month)
        
        depart_format = depart.strftime("%A %#d %B, %Y")
        return_format = return_.strftime("%A %#d %B, %Y")
        
        if type_=='roundtrip':
            # Find and click the depart date                             
            if month_diff_depart < 0:
                datePrev_xpath = '//button[@aria-label="Previous month"]'
                datePrev_element = WebDriverWait(browser, 5).until(EC.presence_of_element_located((By.XPATH, datePrev_xpath)))
                for i in range(0, abs(month_diff_depart)):
                    time.sleep(1)
                    datePrev_element.click()
                    time.sleep(1)
            elif month_diff_depart > 0:
                dateNext_xpath = '//button[@aria-label="Next month"]'
                dateNext_element = WebDriverWait(browser, 5).until(EC.presence_of_element_located((By.XPATH, dateNext_xpath)))
                for i in range(0, month_diff_depart):
                    time.sleep(1)
                    dateNext_element.click()
                    time.sleep(1)  
            else:
                pass
            pickDepart_xpath = f'//div[@aria-label="{depart_format}"]'
            time.sleep(1)
            browser.find_element_by_xpath(pickDepart_xpath).click()
            time.sleep(1)     
            
            # Find and click the return date
            if display_date_depart == depart:
                return_calendar_xpath = '//span[@aria-label="End date calendar input"]'
                return_calendar_element = WebDriverWait(browser, 5).until\
                    (EC.presence_of_element_located((By.XPATH, return_calendar_xpath)))
                return_calendar_element.click()
            
            if month_diff_return > 0:
                dateNext_xpath = '//button[@aria-label="Next month"]'
                dateNext_element = WebDriverWait(browser, 5).until(EC.presence_of_element_located((By.XPATH, dateNext_xpath)))
                for j in range(0, month_diff_return):
                    time.sleep(1)
                    dateNext_element.click()
                    time.sleep(1)
            else:
                pass
            pickReturn_xpath = f'//div[@aria-label="{return_format}"]'
            time.sleep(1)
            browser.find_element_by_xpath(pickReturn_xpath).click()
            time.sleep(1)   

        elif type_ == 'one-way':
            if month_diff_depart < 0:
                datePrev_xpath = '//button[@aria-label="Previous month"]'
                datePrev_element = WebDriverWait(browser, 5).until(EC.presence_of_element_located((By.XPATH, datePrev_xpath)))
                for i in range(0, abs(month_diff_depart)):
                    time.sleep(1)
                    datePrev_element.click()
                    time.sleep(1)
            elif month_diff_depart > 0:
                dateNext_xpath = '//button[@aria-label="Next month"]'
                dateNext_element = WebDriverWait(browser, 5).until(EC.presence_of_element_located((By.XPATH, dateNext_xpath)))
                for i in range(0, month_diff_depart):
                    time.sleep(1)
                    dateNext_element.click()
                    time.sleep(1)  
            else:
                pass
            pickDepart_xpath = f'//div[@aria-label="{depart_format}"]'
            time.sleep(1)
            browser.find_element_by_xpath(pickDepart_xpath).click()
            time.sleep(1)
        
        ### Click "Search" and wait for results ########################################################################
        try:
            time.sleep(1)
            compare_xpath = '//input[contains(@id, "FlightHub")]'
            browser.find_element_by_xpath(compare_xpath).click()
            time.sleep(1)
        except NoSuchElementException:
            try:
                time.sleep(1)
                compare_xpath = '//input[contains(@id, "AranGrant")]'
                browser.find_element_by_xpath(compare_xpath).click()
                time.sleep(1)
            except NoSuchElementException:
                try:
                    time.sleep(1)
                    compare_xpath = '//input[contains(@id, "SUFDU")]'
                    browser.find_element_by_xpath(compare_xpath).click()
                    time.sleep(1)
                except Exception as error:
                    pass
          
        if nonstop:
            nonstop_xpath = '//input[contains(@id, "direct-flight-toggle")]'
            nonstop_element = WebDriverWait(browser, 5).until(EC.presence_of_element_located((By.XPATH, nonstop_xpath)))
            nonstop_element.click()
            time.sleep(1)
            
        # Kayak opens a new window after hitting the search button. We must direct our webscraper to the new window
        window_original = browser.window_handles[0]

        search_xpath = '//button[@aria-label="Search"]'
        search_element = WebDriverWait(browser, 5).until(EC.presence_of_element_located((By.XPATH, search_xpath)))
        search_element.click()
        time.sleep(2)
        
        window_new = browser.window_handles[1]
        
        browser.switch_to.window(window_new)
        
        # Click on Cheapest Flights first
        cheap_xpath = '//div[@aria-label="Cheapest"]'
        cheap_element = WebDriverWait(browser, 5).until(EC.presence_of_element_located((By.XPATH, cheap_xpath)))
        cheap_element.click()
        time.sleep(13)
        
        ### Getting the Info and placing it in SQL #####################################################################
        date_scrape = []
        airline = []
        ticket_type = [type_]
        ticket_class = [class_]
        adults = [trav[0]]
        students = [trav[1]]
        youths = [trav[2]]
        children = [trav[3]]
        infant_seat = [trav[4]]
        infant_lap = [trav[5]]
        origin = []
        destination = []
        going_stops = []
        going_date = []
        going_time = []
        going_arrive_time = []
        going_travel_time = []
        return_stops = []
        return_date = []
        return_time = []
        return_arrive_time = []
        return_travel_time = []
        price = []
        
        ticket_css_selector = '.nrc6-content-section'
        content = browser.find_elements_by_css_selector(ticket_css_selector) 
        
        price_css_selector = '.f8F1-price-text'
        price_info = browser.find_elements_by_css_selector(price_css_selector)
        
        # Check if there are any available flights
        if len(content) > 0:
            for e in content:
                start = e.get_attribute('innerHTML')
                soup = bs(start, features='lxml')
                raw = soup.get_text().strip()
                
                # Get the time of scrape
                date_scrape.append(datetime.now().strftime('%Y-%m-%d %H:%M:%S'))
                
                # Get the airline                
                if type_ == 'roundtrip': x = re.findall("[0-9]+h [0-9]+m", raw)[1].strip()
                elif type_ == 'one-way': x = re.findall("[0-9]+h [0-9]+m", raw)[0].strip()
                y = re.findall(f"{x}.*", raw)[0].split(",")
                if len(y) > 1:
                    airline.append('multipleAirlines')
                else:
                    try:
                        y = re.sub("[0-9]+h [0-9]+m", "", y[0])
                        airline.append( re.findall("^[a-zA-Z]+ [a-zA-Z]+", y)[0].strip() )
                    except:
                        y = y.split(" ")
                        airline.append(y[0])
                
                # Get the origin/destination
                origin.append(leave)
                destination.append(going)
                
                # Get the stops
                x = re.findall("[0-9]+ stop[s]?|direct", raw)
                going_stops.append(x[0].strip())
                if type_ == 'roundtrip': return_stops.append(x[0].strip())
                else: return_stops.append(None)
                
                # Get the depart/return dates
                going_date.append(depart)
                if type_ == 'roundtrip': return_date.append(return_)
                else: return_date.append(None)
                
                # Get the going/return times as well as the going/return arrival times
                x = re.findall("[0-9]+:[0-9]+ am|[0-9]+:[0-9]+ pm", raw)
                going_time.append(x[0].strip())
                going_arrive_time.append(x[1].strip())
                if type_ == 'roundtrip':
                    return_time.append(x[2].strip())
                    return_arrive_time.append(x[3].strip())
                else:
                    return_time.append(None)
                    return_arrive_time.append(None)
                
                # Get the travel times
                x = re.findall("[0-9]+h [0-9]+m", raw)
                going_travel_time.append(x[0].strip())
                if type_ == 'roundtrip': return_travel_time.append(x[0].strip())
                else: return_travel_time.append(None)
            
            for p in price_info:
                start = p.get_attribute('innerHTML')
                soup = bs(start, features='lxml')
                raw = soup.get_text().strip()

                # Get the price
                price.append(raw)
                
            ticket_type = ticket_type*len(date_scrape)
            ticket_class = ticket_class*len(date_scrape)
            adults = adults*len(date_scrape)
            students = students*len(date_scrape)
            youths = youths*len(date_scrape)
            children = children*len(date_scrape)
            infant_seat = infant_seat*len(date_scrape)
            infant_lap = infant_lap*len(date_scrape)
                
            # Close all windows and end the session
            browser.close()
            browser.switch_to.window(window_original)
            browser.quit()

            return [date_scrape, airline, ticket_type, ticket_class, adults, students, youths, children,
                   infant_seat, infant_lap, origin, destination, going_stops, going_date, going_time,
                   going_arrive_time, going_travel_time, return_stops, return_date, return_time,
                   return_arrive_time, return_travel_time, price]
            
        else:
            browser.close()
            browser.switch_to.window(window_original)
            browser.quit()
            sys.exit("There are no flights available for the selected parameters")
            

    def info_to_sql(self, ticket):
        for i in range(len(ticket[0])):
            ticket[22][i] = ticket[22][i].replace("\xa0", " ")
            ticket[13][i] = ticket[13][i].strftime('%Y-%m-%d')
            
        if ticket[18][0] != None:
            for i in range(len(ticket[18])):
                ticket[18][i] = ticket[18][i].strftime('%Y-%m-%d')

        i = 0
        for timestamp in ticket[16]:
            x = re.findall("[0-9]+", timestamp)
            for j in range(2):
                if len(x[j]) < 2:
                    x[j] = "0" + x[j]
            ticket[16][i] = ":".join([x[0], x[1]])
            i += 1        

        if ticket[21][0] != None:
            i = 0
            for timestamp in ticket[21]:
                x = re.findall("[0-9]+", timestamp)
                for j in range(2):
                    if len(x[j]) < 2:
                        x[j] = "0" + x[j]
                ticket[21][i] = ":".join([x[0], x[1]])
                i += 1 

        if ticket[19][0] != None:
            for i in range(len(ticket[14])):
                ticket[14][i] = ticket[14][i].upper()
                ticket[15][i] = ticket[15][i].upper()
                ticket[19][i] = ticket[19][i].upper()
                ticket[20][i] = ticket[20][i].upper()
        else:
            for i in range(len(ticket[14])):
                ticket[14][i] = ticket[14][i].upper()
                ticket[15][i] = ticket[15][i].upper()

        values = []
        for i in range(0, len(ticket[0])):
            values.append( tuple( [ ticket[0][i] ]))
            for j in range(1, len(ticket)):
                values[i] = values[i] + tuple( [ ticket[j][i] ] )

        cursor = self.conn.cursor()
        cursor.fast_executemany = True
        cursor.executemany("INSERT INTO AirFare.dbo.kayak (date_scrape, airline, ticket_type, ticket_class,\
                            adults, students, youths, children, infant_seat, infant_lap, origin, destination,\
                            going_stops, going_date, going_time, going_arrive_time, going_travel_time,\
                            return_stops, return_date, return_time, return_arrive_time, return_travel_time, price)\
                            VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)", values)

        cursor.executemany("INSERT INTO AirFare.dbo.##tmp_kayak (date_scrape, airline, ticket_type, ticket_class,\
                            adults, students, youths, children, infant_seat, infant_lap, origin, destination,\
                            going_stops, going_date, going_time, going_arrive_time, going_travel_time,\
                            return_stops, return_date, return_time, return_arrive_time, return_travel_time, price)\
                            VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)", values)
        
        self.conn.commit()
