from test_login import driver
from time import sleep
from randomNameGen import generate_bot
from selenium import webdriver

# driver = webdriver.Chrome()
bot_id = generate_bot()

def test_setup():
	driver.get("https://localhost:5000/login")
	driver.implicitly_wait(30)
	page = driver.find_element_by_class_name('login-page')
	assert page

def test_register_section():
	driver.find_element_by_link_text("Create an account").click()
	registerForm = driver.find_element_by_class_name('register-form')
	assert registerForm

def test_username_too_short():
	inputFields = driver.find_elements_by_xpath('//form[@class="register-form"]/input')
	inputFields[0].send_keys("test")
	inputFields[1].send_keys("bot")
	inputFields[2].send_keys("bot")
	inputFields[3].send_keys("bot@bot.com")
	sleep(2)
	driver.find_element_by_xpath('//form[@class="register-form"]/button').click()
	alertMsg = driver.find_element_by_class_name('alert-danger').text
	driver.find_element_by_xpath('//button[@class="close"]').click()
	assert "cannot be less than five characters" in alertMsg

def test_mismatching_pw():
	newUsername = driver.find_element_by_xpath('(//form[@class="register-form"]/input)[1]')
	newUsername.clear()
	newUsername.send_keys(bot_id)
	inputFields = driver.find_elements_by_xpath('//form[@class="register-form"]/input')
	inputFields[1].clear()
	inputFields[2].clear()
	inputFields[1].send_keys("test1")
	inputFields[2].send_keys("test2")
	sleep(2)
	driver.find_element_by_xpath('//form[@class="register-form"]/button').click()
	alertMsg = driver.find_element_by_class_name('alert-danger').text
	driver.find_element_by_xpath('//button[@class="close"]').click()
	assert "Passwords must match" in alertMsg

def test_bad_email_1():
	inputFields = driver.find_elements_by_xpath('//form[@class="register-form"]/input')
	inputFields[1].clear()
	inputFields[2].clear()
	botPw = bot_id[4:]
	inputFields[1].send_keys(botPw)
	inputFields[2].send_keys(botPw)
	newEmail = driver.find_element_by_xpath('(//form[@class="register-form"]/input)[4]')
	newEmail.clear()
	newEmail.send_keys("hjoaweofijioeajfo")
	driver.find_element_by_xpath('//form[@class="register-form"]/button').click()
	sleep(2)
	alertMsg = driver.find_element_by_class_name('alert-danger').text
	driver.find_element_by_xpath('//button[@class="close"]').click()
	assert "valid email address" in alertMsg

def test_bad_email_2():
	newEmail = driver.find_element_by_xpath('(//form[@class="register-form"]/input)[4]')
	newEmail.clear()
	newEmail.send_keys("testemailgmail.com")
	driver.find_element_by_xpath('//form[@class="register-form"]/button').click()
	sleep(2)
	alertMsg = driver.find_element_by_class_name('alert-danger').text
	driver.find_element_by_xpath('//button[@class="close"]').click()
	assert "valid email address" in alertMsg

def test_bad_email_3():
	newEmail = driver.find_element_by_xpath('(//form[@class="register-form"]/input)[4]')
	newEmail.clear()
	newEmail.send_keys("gmail@")
	driver.find_element_by_xpath('//form[@class="register-form"]/button').click()
	sleep(2)
	alertMsg = driver.find_element_by_class_name('alert-danger').text
	driver.find_element_by_xpath('//button[@class="close"]').click()
	assert "valid email address" in alertMsg

def test_decline_terms():
	newEmail = driver.find_element_by_xpath('(//form[@class="register-form"]/input)[4]')
	newEmail.clear()
	newEmail.send_keys("{}@bot.com".format(bot_id))
	driver.find_element_by_xpath('//form[@class="register-form"]/button').click()
	sleep(2)
	alertMsg = driver.find_element_by_class_name('alert-danger').text
	driver.find_element_by_xpath('//button[@class="close"]').click()
	assert "accept our terms and conditions to register" in alertMsg

def test_successful_register():
	terms = driver.find_element_by_xpath('(//form[@class="register-form"]/input)[5]')
	terms.click()
	driver.find_element_by_xpath('//form[@class="register-form"]/button').click()
	sleep(2)
	alertMsg = driver.find_element_by_class_name('alert-success').text
	driver.find_element_by_xpath('//button[@class="close"]').click()
	assert "creation successful" in alertMsg

def test_teardown():
	driver.quit()
	assert True
