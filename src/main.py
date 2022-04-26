# Function: get_key_2captcha()
def get_key_2captcha():
    try:
        dotenv.load_dotenv()
        return os.getenv('KEY_2CAPTCHA')
    except:
        print("Error on get_key_2captcha()")

# Function: get_path()
def get_path(ChromeDriverManager):
    return ChromeDriverManager().install()

# Function: get_option()
def get_options(Options):
    opts = Options()
    opts.add_experimental_option('excludeSwitches', ['enable-automation'])
    opts.add_experimental_option('useAutomationExtension', False)
    opts.headless = False
    opts.add_argument('--start-maximized')
    opts.add_extension('extension.crx')
    return opts

# Function: get_driver()
def get_driver(webdriver, PATH, options):
    return webdriver.Chrome(PATH, options=options)

# Function: click_element
def click_element(wb, selector_type, selector):
    try:
        el = WebDriverWait(wb, 10).until(EC.element_to_be_clickable((selector_type, selector)))
        el.click()
        time.sleep(1)
    except:
        print("Error on click_element()")

# Function: send_keys()
def send_keys(wb, selector_type, selector, keys):
    try:
        elem = wb.find_element(selector_type, selector)
        elem.clear()
        elem.send_keys(keys)
        time.sleep(1)
    except:
        print("Error on send_keys")

# Function: setup_2captcha()
def config_2captcha_extension(wd, KEY_2CAPTCHA):
    try:
        wd.switch_to.window(wd.window_handles[1])
        send_keys(wd, By.CSS_SELECTOR, "input[name=apiKey]", KEY_2CAPTCHA)
        click_element(wd, By.CSS_SELECTOR, "#connect")
        time.sleep(3)
        wd.switch_to.alert.accept()
        time.sleep(3)
        wd.close()
        wd.switch_to.window(wd.window_handles[0])
        wd.refresh()
        time.sleep(5)
    except:
        print("Error on setup_2captcha()")

# Function: solve_captcha()
def solve_captcha(wd):
    try:
        iframe = wd.find_elements(By.CSS_SELECTOR, "iframe[src*='geo.captcha']")

        wd.switch_to.frame(iframe[0])
        click_element(wd, By.CSS_SELECTOR, "div.captcha-solver")

        print('Solving captcha. please wait.')
        while 1:
            time.sleep(1)
            try:
                if not("Para ver que realmente eres tú y no un maligno robot" in wd.page_source):
                    break
            except:
                pass

        print('solved...')
        wd.switch_to.default_content()

    except:
        print("Error on solve_captcha()")

# Function: accept_cookies()
def accept_cookies(wd):
    try:
        click_element(wd, By.CSS_SELECTOR, "#didomi-notice-agree-button")
    except:
        print("Cookies already accepted")

# Function: handle_select
def handle_select(wb, selector, selector_type, value_to_select):
    try:
        select_element = wb.find_element(selector_type, selector)
        select_object = Select(select_element)
        # select_object.select_by_value(value_to_select)
        select_object.select_by_visible_text(value_to_select)
        time.sleep(1)
    except:
        print("Error on handle_select()")

# Function: get_options()
def get_districts_options(wb, selector, selector_type):
    try:
        select_element = wb.find_element(selector_type, selector)
        select_object = Select(select_element)
        opts = select_object.options
        return [opt.text for opt in opts][1:]
    except:
        print("Error on get_options()")

# Function: get_districts()
def get_districts(wd):
    try:
        handle_select(wd,'edit-location-level-1', By.ID, 'Madrid Comunidad')
        handle_select(wd,'edit-location-level-2', By.ID, 'Madrid')
        handle_select(wd,'edit-location-level-3', By.ID, 'Madrid')
        return get_districts_options(wd,'edit-location-level-4', By.ID)
    except:
        print("Error on get_districts(")

# Function: navigate_to_district()
def navigate_to_district(wd, url, district):
    try:
        wd.get(url)
        handle_select(wd,'edit-location-level-1', By.ID, 'Madrid Comunidad')
        handle_select(wd,'edit-location-level-2', By.ID, 'Madrid')
        handle_select(wd,'edit-location-level-3', By.ID, 'Madrid')
        handle_select(wd,'edit-location-level-4', By.ID, district)
        click_element(wd, By.CSS_SELECTOR, "#edit-submit")
        time.sleep(3)
        click_element(wd, By.CSS_SELECTOR, "#content > div > div.price-indicator > div > div.price-indicator-table-block.price-indicator-table-block--evolution > a")
        time.sleep(3)
    except:
        print("Error on select_district()")

def replace_regex(df, col, patterns):
    df[col]=df[col].replace(patterns, regex=True)

def convert_to_datetime(df, col):
    d = {
        'Enero':'Jan',
        'Febrero':'Feb',
        'Marzo':'Mar',
        'Abril':'Apr',
        'Mayo':'May',
        'Junio':'Jun',
        'Julio':'Jul',
        'Agosto':'Aug',
        'Septiembre':'Sep',
        'Octubre':'Oct',
        'Noviembre':'Nov',
        'Diciembre':'Dec'
    }
    df[col]=pd.to_datetime(df[col].replace(d, regex=True), format='%b %Y', errors='coerce')

def scrape_districts(wd, url, districts):
    data = []

    for district in districts:
        navigate_to_district(wd, url, district)
        table=wd.find_element_by_tag_name('tbody')
        rows=table.find_elements_by_tag_name('tr')
        rows_lst=[]

        for row in rows:
            elements=row.find_elements_by_tag_name('td')
            register_lst=[]
            for el in elements:
                register_lst.append(el.text)
            register_lst.append(district)

            rows_lst.append(register_lst)
        data.extend(rows_lst)

    return data

#%%
# Step 1: imports
import dotenv
import os
import pandas as pd
import time

from selenium.webdriver.common.by import By
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.select import Select
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

# Step 2: Get KEY_2CAPTCHA environment variable
KEY_2CAPTCHA = get_key_2captcha()
url = 'https://www.idealista.com/sala-de-prensa/informes-precio-vivienda/'

# Step 3: Get driver
PATH = get_path(ChromeDriverManager)
options=get_options(Options)
wd=get_driver(webdriver, PATH, options)

# Step 4: Navigate to idealista website
wd.get(url)

# Step 5: Config 2captcha extension
config_2captcha_extension(wd, KEY_2CAPTCHA)

# Step 6: Solve captcha
solve_captcha(wd)

# Step 7: Accept cookies
accept_cookies(wd)

# Step 8: Get districts
districts = get_districts(wd)

# Step 9: Scrape districts
districts_data = scrape_districts(wd, url, districts)

# Step 10: Create DataFrame
headers=["DATE", "PRICE_M2", "MONTHLY_VARIATION", "QUATERLY_VARIATION", "ANNUAL_VARIATION", "DISTRICT"]
df=pd.DataFrame(districts_data, columns=headers)
original=df.copy()

# Step 11: Convert DATE col to datetime
convert_to_datetime(df, "DATE")

# Step 12: Convert PRICE_M2 to number
patterns_price = {' \€/m2':'', '\.': ''}
replace_regex(df, "PRICE_M2", patterns_price)
df["PRICE_M2"] = pd.to_numeric(df["PRICE_M2"], errors='coerce')

# Step 13: Convert VARIATION cols to number
patterns_variation = {' %':'', '\+ ':'+', '\- ':'-', ',': '.'}
replace_regex(df, "MONTHLY_VARIATION", patterns_variation)
replace_regex(df, "QUATERLY_VARIATION", patterns_variation)
replace_regex(df, "ANNUAL_VARIATION", patterns_variation)
df["MONTHLY_VARIATION"] = pd.to_numeric(df["MONTHLY_VARIATION"], errors='coerce')
df["QUATERLY_VARIATION"] = pd.to_numeric(df["QUATERLY_VARIATION"], errors='coerce')
df["ANNUAL_VARIATION"] = pd.to_numeric(df["ANNUAL_VARIATION"], errors='coerce')

# Step 14: Save DataFrame to Excel
df.to_excel('../data/pricem2.xlsx', index=False)