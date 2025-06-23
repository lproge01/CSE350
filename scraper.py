from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.select import Select
from selenium.webdriver.support.ui import Select
import time
import pandas as pd
import numpy as np

service = Service(executable_path="chromedriver.exe")
driver = webdriver.Chrome(service=service)

driver.get("https://csprd.louisville.edu/psp/ps_class/EMPLOYEE/PSFT_CS/c/COMMUNITY_ACCESS.CLASS_SEARCH./x?")

catalog = []
departments = []
numbers = []
times = []
locations = []
instructors = []
card_cores = []
titles = []

for outer in range(109):
    # Outer loop will iterate through departments
    department = outer + 1
    if outer == 0:
        driver.switch_to.frame("TargetContent")

    WebDriverWait(driver, 15).until(
    EC.presence_of_element_located((By.ID, "CLASS_SRCH_WRK2_STRM$35$"))
    )

    select_element = driver.find_element(By.ID, "CLASS_SRCH_WRK2_STRM$35$")
    select = Select(select_element)
    select.select_by_index(11)
    time.sleep(1)

    select_element = driver.find_element(By.ID, "SSR_CLSRCH_WRK_ACAD_CAREER$0")
    select = Select(select_element)
    select.select_by_value("UGRD")
    time.sleep(1)

    select_element = driver.find_element(By.ID, "SSR_CLSRCH_WRK_SUBJECT_SRCH$1")
    select = Select(select_element)
    select.select_by_index(department)

    search = driver.find_element(By.ID, "CLASS_SRCH_WRK2_SSR_PB_CLASS_SRCH")
    search.click()

    driver.switch_to.default_content()
    driver.switch_to.frame("TargetContent")

    course = []
    course_nums = []

    # Get the department's abbreviation, or continue if no classes in dept.
    try:
        WebDriverWait(driver, 15).until(
        EC.presence_of_element_located((By.ID, "SSR_CLSRSLT_WRK_GROUPBOX2$0"))
        )
        abbr = driver.find_element(By.ID, "SSR_CLSRSLT_WRK_GROUPBOX2$0").get_attribute("title").split()[2]
    except:
        continue
    
    # Gathers the class nums for the department
    for j in range(100):
        try:
            full_name = driver.find_element(By.ID, "SSR_CLSRSLT_WRK_GROUPBOX2$" + str(j)).get_attribute("title")
            num = full_name.split()[3]
            course_nums.append(num)
        except:
            break

    # Go back to input screen to modify search
    modify = driver.find_element(By.ID, "CLASS_SRCH_WRK2_SSR_PB_MODIFY$5$")
    modify.click()

    # Gather information for each course
    for num in course_nums:
        WebDriverWait(driver, 15).until(
        EC.presence_of_element_located((By.ID, "SSR_CLSRCH_WRK_CATALOG_NBR$2"))
        )

        class_num_element = driver.find_element(By.ID, "SSR_CLSRCH_WRK_CATALOG_NBR$2")
        class_num_element.clear()
        class_num_element.send_keys(num)

        search = driver.find_element(By.ID, "CLASS_SRCH_WRK2_SSR_PB_CLASS_SRCH")
        search.click()

        driver.switch_to.default_content()
        driver.switch_to.frame("TargetContent")

        WebDriverWait(driver, 15).until(
        EC.presence_of_element_located((By.ID, "MTG_DAYTIME$0"))
        )

        # Gather information for each section of each course
        for k in range(20):
            try:    
                course = []
                
                # Course time
                driver.find_element(By.ID, "MTG_DAYTIME$" + str(k)).is_displayed()
                times.append(driver.find_element(By.ID, "MTG_DAYTIME$" + str(k)).text.replace("\n", "/"))
                
                # Department and number
                departments.append(abbr)
                numbers.append(num)

                # Card core and title
                card_core = ""
                driver.find_element(By.ID, "SSR_CLSRSLT_WRK_GROUPBOX2$0").is_displayed()
                dash_split = driver.find_element(By.ID, "SSR_CLSRSLT_WRK_GROUPBOX2$0").get_attribute("title").split(" - ")
                if(len(dash_split) > 3):
                    card_core = dash_split[len(dash_split) - 1]
                elif(len(dash_split) == 3):
                    card_core = dash_split[2]
                card_cores.append(card_core)
                titles.append(dash_split[1])

                # Course location
                driver.find_element(By.ID, "MTG_ROOM$" + str(k)).is_displayed()
                location = driver.find_element(By.ID, "MTG_ROOM$" + str(k)).text.replace("\n", " ")
                location = location.rstrip(" / ")
                location = location.rstrip(" /")
                if(location == "ONLINE / Online"):
                    location = "ONLINE"
                locations.append(location)

                # Instructor(s)
                driver.find_element(By.ID, "MTG_ROOM$" + str(k)).is_displayed()
                instructors.append(driver.find_element(By.ID, "MTG_INSTR$" + str(k)).text.replace("\n", " "))
            except:
                break
        modify = driver.find_element(By.ID, "CLASS_SRCH_WRK2_SSR_PB_MODIFY$5$")
        modify.click()
    WebDriverWait(driver, 15).until(
    EC.presence_of_element_located((By.ID, "CLASS_SRCH_WRK2_SSR_PB_CLEAR"))
    )
    clear = driver.find_element(By.ID, "CLASS_SRCH_WRK2_SSR_PB_CLEAR")
    clear.click()

# print("departments: " + str(len(departments)))
# print("numbers: " + str(len(numbers)))
# print("titles: " + str(len(titles)))
# print("times: " + str(len(times)))
# print("locations: " + str(len(locations)))
# print("instructors: " + str(len(instructors)))
# print("card_cores: " + str(len(card_cores)))

dict = {'department': departments, 'number': numbers, 'title': titles, 'time': times, 'location': locations, 'instructor': instructors, 'card_core': card_cores}
df = pd.DataFrame(dict)
df.to_csv('catalog.csv')

driver.quit()
