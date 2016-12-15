# -*- coding: utf-8 -*-

import selenium
from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support.ui import Select  # to deal with dropdown menues
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
import time
from selenium.common.exceptions import NoSuchElementException
import pandas as pd
from collections import defaultdict, namedtuple
from datetime import datetime, date # need to convert timezone

WAIT_TIME = 40  

#driver = webdriver.PhantomJS()
driver = webdriver.Chrome('/Users/ik/Codes/wta-ranking/chromedriver')

RNK_PAGE_CNT = 1

wtapl = []

print("-------> scraping wtatennis.com")

start_page  = "http://www.wtatennis.com/singles-rankings"
driver.get(start_page)

WTA_Player = namedtuple("WTA_Player", "crank name surname country dob")

start_time = time.time()

while RNK_PAGE_CNT < 1300:

	RNK_PAGE_CNT += 100

	# find tha table with rankings
	ranking_table = WebDriverWait(driver, WAIT_TIME).until(EC.presence_of_element_located((By.CSS_SELECTOR, "#myTable")))
	
	# find all rows
	rows = ranking_table.find_elements_by_xpath(".//tbody/tr")
	
	for row in rows:

		# find all cells, i.e. <td>s
		clls = row.find_elements_by_xpath(".//td[contains(@class, 'mobile') and contains(@class, 'center')]")

		wtapl.append(WTA_Player(crank=clls[0].text.strip(), 
			country=clls[1].find_element_by_xpath(".//span[contains(@class, 'hide')]").text.strip().capitalize(),
			name=row.find_element_by_xpath(".//td/a[@class='pink']").text.split(",")[1].strip().capitalize(),
			surname=row.find_element_by_xpath(".//td/a[@class='pink']").text.split(",")[0].strip().capitalize(),
			# on the page, DOBs are listed as, for example, 12 FEB 1992, i.e. %d %b %Y
			dob=datetime.strptime(row.find_element_by_xpath(".//td[contains(@class,'hide')]").text.strip(), "%d %b %Y").strftime("%d-%b-%Y")))
	
	print("ranks collected so far: {}".format(len(wtapl)))
	# go to the next ranking page via the menu
	Select(WebDriverWait(driver, WAIT_TIME).until(EC.element_to_be_clickable((By.CSS_SELECTOR, ".rankings-rank-change")))).select_by_value(str(RNK_PAGE_CNT))

driver.quit()

end_time = time.time()

print("done. collected {} ranks.".format(len(wtapl)))
print("elapsed time: {} min".format(round((end_time - start_time)/60, 1)))

df = pd.DataFrame(wtapl)

csv_fl = "wta_ranking_" + date.today().strftime("%d%b%Y") +".csv"

df.to_csv(csv_fl, index=False, sep="\t")

print("saved everything in the file called {} in your local directory".format(csv_fl))

