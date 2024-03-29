from selenium import webdriver
import time
from selenium.common.exceptions import WebDriverException
from django.contrib.staticfiles.testing import StaticLiveServerTestCase
import os
from selenium.webdriver.common.keys import Keys

MAX_WAIT = 5

class FunctionalTest(StaticLiveServerTestCase):
  def setUp(self):
    self.browser = webdriver.Firefox()
    staging_server = os.environ.get('STAGING_SERVER')
    if staging_server:
      self.live_server_url = 'http://' + staging_server
  
  def tearDown(self):
    self.browser.quit()

  def wait(fn):
    def modified_fn(*args, **kwargs):
      start_time = time.time()
      while True:
        try:
          return fn(*args, **kwargs)
        except(AssertionError, WebDriverException) as e:
          if time.time() - start_time > MAX_WAIT:
            raise e
          time.sleep(0.5)
    return modified_fn

  @wait
  def wait_for_row_in_list_table(self, row_text):
    table = self.browser.find_element_by_id('id_list_table')
    rows = table.find_elements_by_tag_name('tr')
    self.assertIn(row_text, [row.text for row in rows])

  def get_item_input_box(self):
    return self.browser.find_element_by_id('id_text')
  
  @wait
  def wait_to_be_logged_in(self, email):
    self.browser.find_element_by_link_text('Log out')
    navbar = self.browser.find_element_by_css_selector('.navbar')
    self.assertIn(email, navbar.text)

  @wait
  def wait_to_be_logged_out(self, email):
    self.browser.find_element_by_name('email')
    navbar = self.browser.find_element_by_css_selector('.navbar')
    self.assertNotIn(email, navbar.text)

  @wait
  def wait_for(self, fn):
    return fn()
  
  def add_list_item(self, text):
    num_rows = len(self.browser.find_elements_by_css_selector('#id_list_table tr'))
    self.get_item_input_box().send_keys(text)
    self.get_item_input_box().send_keys(Keys.ENTER)
    item_number = num_rows + 1
    self.wait_for_row_in_list_table(f'{item_number}: {text}')