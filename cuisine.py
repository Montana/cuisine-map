import re
import time
import csv
import itertools
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.options import Options

chrome_options = Options()
# chrome_options.add_argument("--headless")
chrome_options.add_argument("--window-position=-2400,-2400")
chrome_options.add_argument("--no-sandbox")
chrome_options.add_argument("--disable-dev-shm-usage")

driver = webdriver.Chrome(options=chrome_options)

driver.get("https://www.google.com/maps")
print("Opened Google Maps")

def sendQuery(query=""):
    search_box = driver.find_element(By.ID, "searchboxinput")
    search_box.send_keys(query)
    search_box.send_keys(Keys.ENTER)
    time.sleep(5)
    currentUrl = driver.current_url
    return currentUrl

city = 'Mountain View, CA'
currentUrl = sendQuery(f"restaurants in {city}")

driver.get(currentUrl)

def scroll_panel_with_page_down(driver, panel_xpath, presses, pause_time):
    panel_element = driver.find_element(By.XPATH, panel_xpath)

    actions = ActionChains(driver)
    actions.move_to_element(panel_element).click().perform()

    for _ in range(presses):
        actions = ActionChains(driver)
        actions.send_keys(Keys.PAGE_DOWN).perform()
        time.sleep(pause_time)
        actions.move_to_element(panel_element).click().perform()
        window_handles = driver.window_handles
        driver.switch_to.window(window_handles[0])

panel_xpath = "//*[@id='QA0Szd']/div/div/div[1]/div[2]/div"

scroll_panel_with_page_down(driver, panel_xpath, presses=20, pause_time=5)

addresses = driver.find_elements(By.CLASS_NAME, 'hfpxzc')

page_source = driver.page_source
soup = BeautifulSoup(page_source, "html.parser")

data_containers = soup.find_all("a", class_="hfpxzc")
cuisine = soup.find_all("div", class_="W4Efsd")

driver.quit()

restaurantNames = []
for address in data_containers:
    restaurantName = re.findall(r'\<a\saria\-label\=\"(.+)\"\sclass', str(address))
    restaurantNames.append(restaurantName[0].replace("'",''))
print(f"Found {len(restaurantNames)} restaurants in {city}")

cuisine = soup.find_all("div", class_="W4Efsd")
restaurantInfo = []
for address in cuisine:
    cuisineType = re.findall(r'\<span\>([\w\s\#\-]+)\<', str(address))
    if len(cuisineType) <=  1:
        continue
    elif len(cuisineType) == 4:
        restaurantInfo.append(cuisineType)

restaurantInfo.sort()
restaurantInfo = list(k for k,_ in itertools.groupby(restaurantInfo))

restaurantCuisine = []
restaurantAddress = []
for r in restaurantInfo:
    restaurantCuisine.append(r[0])
    restaurantAddress.append(r[3])

with open('restaurants_data.csv', 'w', newline='', encoding='utf-8') as file:
    writer = csv.writer(file)
    writer.writerow(['Restaurant Name', 'Cuisine', 'Address'])

    for i in range(min(len(restaurantNames), len(restaurantCuisine), len(restaurantAddress))):
        writer.writerow([restaurantNames[i], restaurantCuisine[i], restaurantAddress[i]])

print(f"Wrote {min(len(restaurantNames), len(restaurantCuisine), len(restaurantAddress))} restaurants to restaurants_data.csv")

with open('restaurantNames.txt', 'w') as file:
    for i in restaurantNames:
        file.write(i + ", " + city + "\n")
print(f"Wrote {len(restaurantNames)} restaurant names to restaurantNames.txt")
