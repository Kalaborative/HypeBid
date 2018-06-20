from test_c_games import driver
from selenium.webdriver.support.ui import Select
from datetime import datetime, timedelta
from os import listdir, getcwd
from time import sleep

created_id = ""

def test_setup():
	driver.get('http://localhost:5000/login')
	inputs = driver.find_elements_by_tag_name('input')
	inputs[0].send_keys('Kalaborative')
	inputs[1].send_keys('Comput3ch')
	driver.find_element_by_class_name('submitBtn').click()
	sleep(3)
	assert 'games' in driver.current_url

def test_on_newitem_page():
	driver.get('http://localhost:5000/admin/kalaborative/makenewitem')
	sleep(2)
	new_item_Form = driver.find_element_by_tag_name('form')
	assert new_item_Form

def test_new_item():
	driver.find_element_by_id('itemName').send_keys("Pytest item")
	driver.find_element_by_id('itemDesc').send_keys("This item was created through an automated testing service.")
	driver.find_element_by_xpath('(//input)[3]').send_keys('3.00')
	driver.find_element_by_xpath('(//input)[4]').send_keys(getcwd() + '/test_item.jpg')
	tomorrow = datetime.today() + timedelta(days=1)
	driver.find_element_by_id('datetimepicker1').clear()
	driver.find_element_by_id('datetimepicker1').send_keys(tomorrow.strftime("%x %X %p"))
	driver.find_element_by_xpath('(//button)[3]').click()
	sleep(1)
	result = driver.find_element_by_class_name('alert').text
	assert "success" in result

def test_gameID_extracted():
	response = driver.find_element_by_class_name('alert').text.strip()
	extract_id = response[-10:-1]
	global created_id
	created_id = extract_id
	id_number = int(extract_id)
	assert id_number > 1

def test_folder_remained_empty():
	temp_path = "itemUploads/"
	assert listdir(temp_path) == []


def test_game_created():
	driver.get('http://localhost:5000/game/{}'.format(created_id))
	sleep(1)
	page_game_id = driver.find_element_by_class_name('gameID').text
	assert created_id == page_game_id

def test_delete_testgame():
	driver.get('http://localhost:5000/admin/kalaborative/simulatebidding')
	select = Select(driver.find_element_by_id('chooseGame'))
	select.select_by_visible_text(created_id)
	sleep(1)
	deleteModal = driver.find_element_by_class_name('btn-danger')
	deleteModal.click()
	sleep(1)
	driver.find_element_by_id('deleteGameBtn').click()
	sleep(1)
	status = driver.find_element_by_id('creationStatus').text
	assert "Complete" in status

def test_teardown():
	driver.quit()
	assert 1