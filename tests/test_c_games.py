from test_b_register import driver
from time import sleep

def test_setup():
	driver.get("http://localhost:5000/login")
	driver.implicitly_wait(30)
	title = driver.find_element_by_tag_name('h1')
	assert "Login" in title.text

def test_kalab_login():
	inputs = driver.find_elements_by_tag_name('input')
	inputs[0].send_keys('Kalaborative')
	inputs[1].send_keys('Comput3ch')
	driver.find_element_by_class_name('submitBtn').click()
	sleep(2)
	assert 'games' in driver.current_url

def test_find_a_game():
	games = driver.find_elements_by_tag_name('h2')
	games[0].click()
	id_name = driver.find_element_by_class_name("gameID").text
	game_id = int(id_name)
	assert game_id > 1

def test_cant_bid_over_maximum():
	driver.find_element_by_id('headingThree').click()
	sleep(1)
	max_bid_text = driver.find_element_by_id('maxBidFloat').text
	max_bid = float(max_bid_text)
	over_bid = max_bid + 1
	driver.find_element_by_id('bidInput').send_keys(str(over_bid))
	driver.find_element_by_class_name('placerbtn').click()
	error_text = driver.switch_to_alert().text
	assert "cannot be higher" in error_text

def test_make_good_bid():
	driver.switch_to_alert().accept()
	driver.find_element_by_id('bidInput').clear()
	driver.find_element_by_id('bidInput').send_keys('0.33')
	driver.find_element_by_class_name('placerbtn').click()
	sleep(5)
	result_text = driver.switch_to_alert().text
	assert "successful" in result_text

def test_teardown():
	assert 1