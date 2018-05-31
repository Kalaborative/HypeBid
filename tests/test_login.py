from selenium import webdriver
from time import sleep

driver = webdriver.Chrome()

def test_setup():
	driver.get("http://localhost:5000/login")
	driver.implicitly_wait(30)
	page = driver.find_element_by_class_name('login-form')
	assert page

def test_less_than_five():
	loginUname = driver.find_element_by_xpath('(//form[@class="login-form"]/input)[1]')
	loginUname.send_keys("test")
	loginPw = driver.find_element_by_xpath('(//form[@class="login-form"]/input)[2]')
	loginPw.send_keys("test")
	driver.find_element_by_xpath('//form[@class="login-form"]/button').click()
	alertMsg = driver.find_element_by_class_name('alert-danger').text
	driver.find_element_by_xpath('//button[@class="close"]').click()
	assert "cannot be less than five characters" in alertMsg

def test_invalid_username():
	loginUname = driver.find_element_by_xpath('(//form[@class="login-form"]/input)[1]')
	loginUname.clear()
	loginUname.send_keys('testx')
	driver.find_element_by_xpath('//form[@class="login-form"]/button').click()
	alertMsg = driver.find_element_by_class_name('alert-danger').text
	assert "Invalid username" in alertMsg

def test_wrong_password():
	loginUname = driver.find_element_by_xpath('(//form[@class="login-form"]/input)[1]')
	loginUname.clear()
	loginUname.send_keys('Guest')
	driver.find_element_by_xpath('//form[@class="login-form"]/button').click()
	sleep(3)
	alertMsg = driver.find_element_by_class_name('alert-danger').text
	assert "Wrong password" in alertMsg

def test_login_success():
	loginPw = driver.find_element_by_xpath('(//form[@class="login-form"]/input)[2]')
	loginPw.clear()
	loginPw.send_keys("guest")
	driver.find_element_by_xpath('//form[@class="login-form"]/button').click()
	sleep(2)
	navLinks = driver.find_elements_by_xpath('//*[@id="navbarColor02"]//a')
	navText = []
	for nav in navLinks:
		navText.append(nav.text)
	assert "Logout" in navText

def test_logout():
	driver.find_element_by_link_text("Logout").click()
	sleep(2)
	btn = driver.find_element_by_class_name('w-button').text
	assert "Login" in btn

def test_teardown():
	assert True