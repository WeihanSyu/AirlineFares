from bs4 import BeautifulSoup as bs
from datetime import date
from datetime import datetime
from datetime import timedelta
import pyodbc
import re
import requests
from selenium import webdriver
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import Select
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import sys
import time


class expedia_flight:
    def __init__(self, chrome_driver, chrome_options, conn):
        self.chrome_driver = chrome_driver
        self.chrome_options = chrome_options
        self.conn = conn


    def get_ticket_info(self, type_='roundtrip', class_='economy', leave="yvr", going="tpe", 
                       depart=date.today(), return_=date.today()+timedelta(days=1), 
                       trav=[1,0,0,0], nonstop=False):

        flight_inputs = {'roundtrip': 'ROUND_TRIP', 'one-way': 'ONE_WAY', 'multi-city': 'MULTI_CITY', 
                         'economy': (Keys.DOWN, Keys.ENTER), 'premium economy': (Keys.DOWN, Keys.DOWN, Keys.ENTER), 
                         'business class': (Keys.DOWN, Keys.DOWN, Keys.DOWN, Keys.ENTER), 
                         'first class': (Keys.DOWN, Keys.DOWN, Keys.DOWN, Keys.DOWN, Keys.ENTER)}
        
        ### Handle out of bound dates ###################################################################################
        if (depart - date.today()).days < 0:
            sys.exit("Depart date cannot be earlier than current date")
        elif (return_ - depart).days < 0:
            sys.exit("Return date cannot be earlier than depart date")
        elif ((depart - date.today()).days > 330) or ((return_ - date.today()).days > 330):
            sys.exit("Selected dates are too far in the future")
        else:
            pass
        
        ### Handle invalid traveller counts #############################################################################
        if trav[0] < 1:
            sys.exit("must have at least 1 adult selected")
        elif sum(trav) > 6 or trav[0] > 6 or trav[1] > 5:
            sys.exit("total travellers can't exceed 6")
        elif trav[2] > 0 and trav[3] > 0:
            sys.exit("infants must be either ALL on lap, or ALL on seat")
        elif trav[2] > 4 or trav[3] > 4:
            sys.exit("infants cannot exceed 4")
        else:
            pass
        
        ### If there are children and/or infants selected ###############################################################
        if trav[1] > 0:
            num = 1
            child_ages = []
            for i in range(0, trav[1]):
                print(f"Enter the age of child {num} (ages: 2-17)")
                child_ages.append(input())
                num += 1
            child_12_up = 0
            for i in child_ages:
                if int(i) >= 12:
                    child_12_up += 1
            # For every infant on lap, there must be a traveller (age 12+) for them
            if (trav[0] + child_12_up) < trav[2]:
                sys.exit("Not enough age 12+ travellers selected for infants on lap")
            
        if (trav[0] + trav[1]) < trav[2]:
            sys.exit("Not enough age 12+ travellers selected for infants on lap")
        
        if trav[2] > 0:
            num = 1
            infant_ages = []
            for i in range(0, trav[2]):
                print(f"Enter the age of infant {num} (ages: 0-1)")
                infant_ages.append(input())
                num += 1
                
        if trav[3] > 0:
            num = 1
            infant_ages = []
            for i in range(0, trav[3]):
                print(f"Enter the age of infant {num} (ages: 0-1)")
                infant_ages.append(input())
                num += 1
        
        ### Request the webpage #########################################################################################
        url = "https://www.expedia.ca/"
        browser = webdriver.Chrome(self.chrome_driver, options=self.chrome_options)
        # Change the property of the navigator value for webdriver to undefined
        browser.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})") 
        browser.get(url)

        ### Select "Flights" tab ########################################################################################
        flight_xpath = '//a[@aria-controls="search_form_product_selector_flights"]'
        flight_element = WebDriverWait(browser, 5).until(EC.presence_of_element_located((By.XPATH, flight_xpath)))
        flight_element.click()
        
        ### Select "type" of flight #####################################################################################
        type_xpath = '//a[@aria-controls="FlightSearchForm_' + flight_inputs[type_] + '"]'
        type_element = WebDriverWait(browser, 5).until(EC.presence_of_element_located((By.XPATH, type_xpath)))
        type_element.click()

        ### Select ticket "class" #######################################################################################
        class_xpath = '//button[@id="cabin_class"]'
        class_element = WebDriverWait(browser, 5).until(EC.presence_of_element_located((By.XPATH, class_xpath)))
        class_element.click()
        time.sleep(1)
        class_element.send_keys(flight_inputs[class_])

        ### Select Leaving from and Going to locations ##################################################################
        leave_xpath = '//button[@aria-label="Leaving from"]'
        leave_element = WebDriverWait(browser, 5).until(EC.presence_of_element_located((By.XPATH, leave_xpath)))
        leave_element.clear
        leave_element.click()
        leaveDrop_xpath = '//input[@data-stid="origin_select-menu-input"]'  
        leaveDrop_element = WebDriverWait(browser, 5).until(EC.presence_of_element_located((By.XPATH, leaveDrop_xpath)))
        leaveDrop_element.click()
        time.sleep(1)
        leaveDrop_element.send_keys(leave)
        time.sleep(1)
        leaveDrop_element.send_keys(Keys.DOWN, Keys.ENTER)
        
        going_xpath = '//button[@aria-label="Going to"]'
        going_element = WebDriverWait(browser, 5).until(EC.presence_of_element_located((By.XPATH, going_xpath)))
        going_element.clear
        going_element.click()
        goingDrop_xpath = '//input[@data-stid="destination_select-menu-input"]'
        goingDrop_element = WebDriverWait(browser, 5).until(EC.presence_of_element_located((By.XPATH, goingDrop_xpath)))
        goingDrop_element.click()
        time.sleep(1)
        goingDrop_element.send_keys(going)
        time.sleep(1)
        goingDrop_element.send_keys(Keys.DOWN, Keys.ENTER)
        
        ### Select Dates ###############################################################################################
        
        # First: click the Dates container which opens up the calender
        display_date_depart = (date.today() + timedelta(days=14)).strftime('%b') # expedia always adds 2 weeks
        date_xpath = f'//button[starts-with(@aria-label, "Date") and contains(@aria-label, "{display_date_depart}")]'
        date_element = WebDriverWait(browser, 5).until(EC.presence_of_element_located((By.XPATH, date_xpath)))
        date_element.click()
        time.sleep(1)
        
        # Second: go to the right calendar pages and click the dates we want
        display_date_depart = (date.today() + timedelta(days=14))
        display_date_return = (date.today() + timedelta(days=15))
        depart_month = depart.strftime('%b')
        return_month = return_.strftime('%b')
        month_diff_depart = (depart.year - display_date_depart.year)*12 + (depart.month - display_date_depart.month)
        month_diff_return = (return_.year - depart.year)*12 + (return_.month - depart.month)
        
        if type_ == 'roundtrip':
            # Find and click the depart date
            if month_diff_depart < 0:
                datePrev_xpath = '//button[@data-stid="date-picker-paging"][1] | //button[@data-stid=\
                "uitk-calendar-navigation-controls-previous-button"]'
                datePrev_element = WebDriverWait(browser, 5).until(EC.presence_of_element_located((By.XPATH, datePrev_xpath)))
                datePrev_element.click()
                time.sleep(1)
            elif month_diff_depart > 0:
                dateNext_xpath = '//button[@data-stid="date-picker-paging"][2] | //button[@data-stid=\
                "uitk-calendar-navigation-controls-next-button"]' 
                dateNext_element = WebDriverWait(browser, 5).until(EC.presence_of_element_located((By.XPATH, dateNext_xpath)))
                for i in range(0, month_diff_depart):
                    time.sleep(1)
                    dateNext_element.click()
                    time.sleep(1)      
            else:
                pass
            pickDepart_xpath = '//button[@data-day="' + str(depart.day) + '" and contains(@aria-label, "' + depart_month + '")]\
            | //div[starts-with(text(), "' + str(depart.day) + '")]'
            time.sleep(1)
            browser.find_element_by_xpath(pickDepart_xpath).click()
            time.sleep(1)
            
            # Find and click the return date
            if month_diff_return > 0:
                dateNext_xpath = '//button[@data-stid="date-picker-paging"][2] | //button[@data-stid=\
                "uitk-calendar-navigation-controls-next-button"]' 
                dateNext_element = WebDriverWait(browser, 5).until(EC.presence_of_element_located((By.XPATH, dateNext_xpath)))
                for i in range(0, month_diff_return):
                    time.sleep(1)
                    dateNext_element.click()
                    time.sleep(1)
            else:
                pass
            pickReturn_xpath = '//button[@data-day="' + str(return_.day) + '" and contains(@aria-label, "' + return_month + '")]\
            | //div[starts-with(text(), "' + str(return_.day) + '")]'
            time.sleep(1)
            browser.find_element_by_xpath(pickReturn_xpath).click()
            time.sleep(1)    
            
            # Click done on the calender to save selection and close
            done_xpath = '//button[@data-stid="apply-date-picker"] | //button[contains(text(), "Done")]'
            done_element = WebDriverWait(browser, 5).until(EC.presence_of_element_located((By.XPATH, done_xpath)))
            done_element.click() 
            time.sleep(1)
            
        elif type_ == 'one-way':
            # Find and click the depart date
            if month_diff_depart < 0:
                datePrev_xpath = '//button[@data-stid="date-picker-paging"][1] | //button[@data-stid=\
                "uitk-calendar-navigation-controls-previous-button"]'
                datePrev_element = WebDriverWait(browser, 5).until(EC.presence_of_element_located((By.XPATH, datePrev_xpath)))
                datePrev_element.click()
                time.sleep(2)
            elif month_diff_depart > 0:
                dateNext_xpath = '//button[@data-stid="date-picker-paging"][2] | //button[@data-stid=\
                "uitk-calendar-navigation-controls-next-button"]' 
                dateNext_element = WebDriverWait(browser, 5).until(EC.presence_of_element_located((By.XPATH, dateNext_xpath)))
                for i in range(0, month_diff_depart):
                    time.sleep(1)
                    dateNext_element.click()
                    time.sleep(1)      
            else:
                pass
            pickDepart_xpath = '//button[@data-day="' + str(depart.day) + '" and contains(@aria-label, "' + depart_month + '")]\
            | //div[starts-with(text(), "' + str(depart.day) + '")]'
            time.sleep(1)
            browser.find_element_by_xpath(pickDepart_xpath).click()
            time.sleep(2)
            
            # Click done on the calender to save selection and close
            done_xpath = '//button[@data-stid="apply-date-picker"] | //button[contains(text(), "Done")]'
            done_element = WebDriverWait(browser, 5).until(EC.presence_of_element_located((By.XPATH, done_xpath)))
            done_element.click() 
        
        ### Select Travellers ##########################################################################################
        trav_xpath = '//button[@data-stid="open-room-picker"]'
        trav_element = WebDriverWait(browser, 5).until(EC.presence_of_element_located((By.XPATH, trav_xpath)))
        trav_element.click()
        time.sleep(1)
        
        trav_add_xpath = {1: '//*[starts-with(@aria-label, "Increase the number of adults")]/..',
                         2: '//*[starts-with(@aria-label, "Increase the number of children")]/..',
                         3: '//*[starts-with(@aria-label, "Increase the number of infants on lap")]/..',
                         4: '//*[starts-with(@aria-label, "Increase the number of infants in seat")]/..'}
        
        x = 1
        for traveller_type in trav:
            if x == 1:
                for i in range(0, traveller_type - 1):
                    browser.find_element_by_xpath(trav_add_xpath[x]).click()
                    time.sleep(1)
            elif x == 2:
                for i in range(0, traveller_type):
                    browser.find_element_by_xpath(trav_add_xpath[x]).click()
                    time.sleep(1)
                    select = Select(browser.find_element_by_id(f"age-traveler_selector_children_age_selector-{i}"))
                    select.select_by_value(child_ages[i])
                    time.sleep(1)
            else:
                for i in range(0, traveller_type):
                    browser.find_element_by_xpath(trav_add_xpath[x]).click()
                    time.sleep(1)
                    select = Select(browser.find_element_by_id(f"age-traveler_selector_infant_age_selector-{i}"))
                    select.select_by_value(infant_ages[i])
                    time.sleep(1)
            x += 1
        
        trav_done_xpath = '//button[@id="travelers_selector_done_button"]'
        trav_done_element = WebDriverWait(browser, 5).until(EC.presence_of_element_located((By.XPATH, trav_done_xpath)))
        trav_done_element.click() 
        
        ### Click "Search" and wait for results ########################################################################          
        search_xpath = '//button[@id="search_button"]'
        search_element = WebDriverWait(browser, 5).until(EC.presence_of_element_located((By.XPATH, search_xpath)))
        time.sleep(1)
        search_element.click()
        time.sleep(13)
        
        ### Getting the Info and placing it in SQL #####################################################################
        
        # Create empty lists for each column in our SQL expedia Table
        date_scrape = []
        airline = []
        ticket_type = [type_]
        ticket_class = [class_]
        adults = [trav[0]]
        children = [trav[1]]
        infant_lap = [trav[2]]
        infant_seat = [trav[3]]
        origin = []
        destination = []
        going_stops = []
        going_date = []
        going_time = []
        going_arrive_time = []
        going_travel_time = []
        return_date = []
        price = []
        
        # Select the nonstop checkbox if we want
        if nonstop:
            nonstop_xpath = '//input[starts-with(@id, "NUM_OF_STOPS-0")]'
            
            # Check if there are any available nonstop flights
            if len(browser.find_elements_by_xpath(nonstop_xpath)) > 0:
                browser.find_element_by_xpath(nonstop_xpath).click()
                time.sleep(8)
                
                ticket_css_selector = '.uitk-card-has-primary-theme .uitk-card-content-section-padded .uitk-card-link'
                content = browser.find_elements_by_css_selector(ticket_css_selector)
                for e in content:
                    start = e.get_attribute('innerHTML')
                    soup = bs(start, features='lxml')
                    raw = soup.get_text().strip()
                    
                    # Get the time of scrape
                    date_scrape.append(datetime.now().strftime('%Y-%m-%d %H:%M:%S'))
                    
                    # Get the airline
                    x = re.sub("[a-zA-Z ]*information for ", "", raw) 
                    m = re.search("flight", x)
                    airline.append( x[:m.start()].strip() )

                    # Get the stops
                    going_stops.append( re.findall("[a-zA-Z ]*stop[s]*", raw)[0].strip() )

                    # Get the depart_date -> Just use the input
                    going_date.append(depart)
                    
                    # Get the depart_time
                    going_time.append( re.findall(" [0-9]+:[0-9]+ PM| [0-9]+:[0-9]+ AM", raw)[0].strip() )
                    
                    # Get the arrive_time
                    going_arrive_time.append( re.findall(" [0-9]+:[0-9]+ PM| [0-9]+:[0-9]+ AM", raw)[1].strip() )

                    # Get the origin/destination -> Why don't we just use the airport. It is unique unlike city names
                    origin.append(leave)
                    destination.append(going)

                    # Get the travel_time
                    x = re.findall("[^.]*total travel time", raw)[0].strip()
                    going_travel_time.append( re.sub(" total travel time", "", x) )
                
                    # Get the return_date -> Just use the input
                    if type_ == 'roundtrip': return_date.append(return_)
                    else: return_date.append(None)

                    # Get the price
                    x = re.findall("Priced at.*\$[0-9,]*", raw)[0].strip()
                    price.append( re.sub("Priced at ", "", x) )
                
                browser.quit()
                
                ticket_type = ticket_type*len(date_scrape)
                ticket_class = ticket_class*len(date_scrape)
                adults = adults*len(date_scrape)
                children = children*len(date_scrape)
                infant_lap = infant_lap*len(date_scrape)
                infant_seat = infant_seat*len(date_scrape)
                
                return [date_scrape, airline, ticket_type, ticket_class, adults, children, 
                        infant_lap, infant_seat, origin, destination, going_stops, going_date, 
                        going_time, going_arrive_time, going_travel_time, return_date, price]
                
            else:
                browser.quit()
                sys.exit("There are no nonstop flights available for the selected parameters")
        
        # Scrape all flights
        else:
            ticket_css_selector = '.uitk-card-has-primary-theme .uitk-card-content-section-padded .uitk-card-link'
            content = browser.find_elements_by_css_selector(ticket_css_selector)
            
            # Check if there are any available flights
            if len(content) > 0:
                for e in content:
                    start = e.get_attribute('innerHTML')
                    soup = bs(start, features='lxml')
                    raw = soup.get_text().strip()
                    
                    # Get the time of scrape
                    date_scrape.append(datetime.now().strftime('%Y-%m-%d %H:%M:%S'))
                    
                    # Get the airline
                    x = re.sub("[a-zA-Z ]*information for ", "", raw) 
                    m = re.search("flight", x)
                    airline.append( x[:m.start()].strip() )

                    # Get the stops
                    going_stops.append( re.findall("[a-zA-Z ]*stop[s]*", raw)[0].strip() )

                    # Get the depart_date -> Just use the input
                    going_date.append(depart)
                    
                    # Get the depart_time
                    going_time.append( re.findall(" [0-9]+:[0-9]+ PM| [0-9]+:[0-9]+ AM", raw)[0].strip() )
                    
                    # Get the arrive_time
                    going_arrive_time.append( re.findall(" [0-9]+:[0-9]+ PM| [0-9]+:[0-9]+ AM", raw)[1].strip() )

                    # Get the origin/destination -> Why don't we just use the airport. It is unique unlike city names
                    origin.append(leave)
                    destination.append(going)

                    # Get the travel_time
                    x = re.findall("[^.]*total travel time", raw)[0].strip()
                    going_travel_time.append( re.sub(" total travel time", "", x) )
                
                    # Get the return_date -> Just use the input
                    if type_ == 'roundtrip': return_date.append(return_)
                    else: return_date.append(None)

                    # Get the price
                    x = re.findall("Priced at.*\$[0-9,]*", raw)[0].strip()
                    price.append( re.sub("Priced at ", "", x) )  
                    
                browser.quit()
                
                ticket_type = ticket_type*len(date_scrape)
                ticket_class = ticket_class*len(date_scrape)
                adults = adults*len(date_scrape)
                children = children*len(date_scrape)
                infant_lap = infant_lap*len(date_scrape)
                infant_seat = infant_seat*len(date_scrape)
                
                return [date_scrape, airline, ticket_type, ticket_class, adults, children, 
                        infant_lap, infant_seat, origin, destination, going_stops, going_date, 
                        going_time, going_arrive_time, going_travel_time, return_date, price]
            
            else:
                browser.quit()
                sys.exit("There are no flights available for the selected parameters")


    def info_to_sql(self, ticket):
        for i in range(len(ticket[0])):
            ticket[16][i] = ticket[16][i].replace("\xa0", " ")
            ticket[11][i] = ticket[11][i].strftime('%Y-%m-%d')

        if ticket[15][0] != None:
            for i in range(len(ticket[15])):
                ticket[15][i] = ticket[15][i].strftime('%Y-%m-%d')

        i = 0
        for timestamp in ticket[14]:
            x = re.findall("[0-9]+", timestamp)
            for j in range(2):
                if len(x[j]) < 2:
                    x[j] = "0" + x[j]
            ticket[14][i] = ":".join([x[0], x[1]])
            i += 1

        values = []
        for i in range(0, len(ticket[0])):
            values.append( tuple( [ ticket[0][i] ]))
            for j in range(1, len(ticket)):
                values[i] = values[i] + tuple( [ ticket[j][i] ] )

        cursor = self.conn.cursor()
        cursor.fast_executemany = True
        cursor.executemany("INSERT INTO AirFare.dbo.expedia (date_scrape, airline, ticket_type, ticket_class,\
                    adults, children, infant_lap, infant_seat, origin, destination, going_stops,\
                    going_date, going_time, going_arrive_time, going_travel_time, return_date, price)\
                    VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)", values)

        cursor.executemany("INSERT INTO AirFare.dbo.##tmp_expedia (date_scrape, airline, ticket_type, ticket_class,\
                    adults, children, infant_lap, infant_seat, origin, destination, going_stops,\
                    going_date, going_time, going_arrive_time, going_travel_time, return_date, price)\
                    VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)", values)
        
        self.conn.commit()
