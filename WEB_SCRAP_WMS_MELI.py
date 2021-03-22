from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
import time
import pandas as pd

login_url = 'https://www.mercadolivre.com/jms/mlb/lgz/login?platform_id=ML&go=https%3A%2F%2Fwms.mercadolivre.com.br%2F&loginType=explicit'

data = {
	'username': 'USER_ACESS',
	'password': 'PASSWORD_ACESS',
}



def openDriver():
	# i put some security measures so website can't detect that u use selenium, just incase!
	options = webdriver.ChromeOptions()
	options.add_experimental_option("useAutomationExtension", False)
	options.add_argument("--headless")
	options.add_argument('--no-sandbox')
	options.add_argument('--disable-dev-shm-usage')
	driver = webdriver.Chrome(options=options)
	driver.implicitly_wait(10)
	driver.execute_cdp_cmd("Page.addScriptToEvaluateOnNewDocument", {
		"source": """
			Object.defineProperty(navigator, 'webdriver', {
			get: () => undefined
			})
		"""
	})
	driver.execute_cdp_cmd("Page.addScriptToEvaluateOnNewDocument", {
		"source": """
			Object.defineProperty(navigator, 'plugins', {
			get: () => '[1,2,3]'
			})
		"""
	})
	return driver
			
# open driver
driver = openDriver()

# open login page
driver.get(login_url)

# type username
userBox = WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.XPATH ,'//*[@id="user_id"]')))
userBox.send_keys(data['username'])

# click on the continue button
contineButton = driver.find_element_by_xpath('//*[@id="login_user_form"]/div[2]/button')
contineButton.click()

# type password
passBox = WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.XPATH ,'//*[@id="password"]')))
passBox.send_keys(data['password'])

# click on the login button
loginButton = driver.find_element_by_xpath('//*[@id="action-complete"]')
loginButton.click()


# scrape url

report_final = []



url = 'https://wms.mercadolivre.com.br/reports/movements?process_name=transfer_multi_warehouse&external_references.transfer_plan_id=1951,2198,2233,2171,2134,2190,2172,2102,2041,2043,2191,2067,2011,2040,2162,2049,2008,1990,1991,1992,1952,2078,1765,1790,1823,1811,1810,1748,1777,1747,1764,1737,1729,1766,1708,831,843,854,638,703,704,746,774,804,821,832,829,830,845,848&date_from=2019-10-01&date_to=2021-03-17&limit=1&offset='

for x in range(1,291112):

	driver.get(url+str(x))
	html = driver.page_source
	soup = BeautifulSoup(html, 'html.parser')
	content = soup.find_all('table', class_='andes-table table table-sticky')


	for dados in content:
		td = soup.find('td', class_='andes-table__column andes-table__column--left').text
		process= soup.find('td', class_='andes-table__column andes-table__column--center single-line').text
		inventory_id = soup.find('a', class_='inventory-id-code').text
		tp = [my_tag.text for my_tag in soup.find_all(class_="andes-table__column andes-table__column--center")][0]
		qty = [my_tag.text for my_tag in soup.find_all(class_="andes-table__column andes-table__column--center")][2]
		origem = [my_tag.text for my_tag in soup.find_all(class_="andes-table__column andes-table__column--center")][3]
		destino = [my_tag.text for my_tag in soup.find_all(class_="andes-table__column andes-table__column--center")][4]
		user = [my_tag.text for my_tag in soup.find_all(class_="andes-table__column andes-table__column--center")][6]

		movements_report = {
			'td':td,
			'process':process,
			'inventory_id':inventory_id,
			'tp':tp,
			'qty':qty,
			'origem':origem,
			'destino':destino,
			'data':data,
			'user':user

		}
		report_final.append(movements_report)
		

		df = pd.DataFrame(report_final)
		df.to_csv('report_erros_sistemicos_multiwhse_pt4.csv', index=False)
print(df.head())




print(len(report_final))
print(soup.title)


# close driver
driver.close()
