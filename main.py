from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.select import Select
from selenium.webdriver.support.ui import Select
import time

department = input("Class department abbreviation: ")
class_num = input("Class number: ")

service = Service(executable_path="chromedriver.exe")
driver = webdriver.Chrome(service=service)

driver.get("https://csprd.louisville.edu/psp/ps_class/EMPLOYEE/PSFT_CS/c/COMMUNITY_ACCESS.CLASS_SEARCH./x?")

#WebDriverWait(driver, 5).until(
#    EC.presence_of_element_located((By.ID, "CLASS_SRCH_WRK2_INSTITUTION$31$"))
#)
#
#select_element = driver.find_element(By.ID, "CLASS_SRCH_WRK2_INSTITUTION$31$")
#select = Select(select_element)
#select.select_by_visible_text("University of Louisville")

driver.switch_to.frame("TargetContent")

WebDriverWait(driver, 15).until(
   EC.presence_of_element_located((By.ID, "CLASS_SRCH_WRK2_STRM$35$"))
)

select_element = driver.find_element(By.ID, "CLASS_SRCH_WRK2_STRM$35$")
select = Select(select_element)
select.select_by_index(12)
time.sleep(1)

select_element = driver.find_element(By.ID, "SSR_CLSRCH_WRK_ACAD_CAREER$0")
select = Select(select_element)
select.select_by_value("UGRD")
time.sleep(1)

select_element = driver.find_element(By.ID, "SSR_CLSRCH_WRK_SUBJECT_SRCH$1")
select = Select(select_element)
select.select_by_value(department)

select_element = driver.find_element(By.ID, "SSR_CLSRCH_WRK_INSTRUCTION_MODE$3")
select = Select(select_element)
select.select_by_value("P")

class_num_element = driver.find_element(By.ID, "SSR_CLSRCH_WRK_CATALOG_NBR$2")
class_num_element.send_keys(class_num)

search = driver.find_element(By.ID, "CLASS_SRCH_WRK2_SSR_PB_CLASS_SRCH")
search.click()

time.sleep(5)

driver.switch_to.default_content()
driver.switch_to.frame("TargetContent")

i = 0
available_times = []
time_prefix = "MTG_DAYTIME$"

while True:
    this_prefix = time_prefix + str(i)

    try:
        driver.find_element(By.ID, this_prefix).is_displayed()
        available_times.append(driver.find_element(By.ID, this_prefix).text)
    except:
        break
    i += 1
        
for e in available_times:
    print(e)

driver.quit()
