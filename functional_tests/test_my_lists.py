from django.conf import settings
from django.contrib.auth import BACKEND_SESSION_KEY, SESSION_KEY, get_user_model
from django.contrib.sessions.backends.db import SessionStore
from .base import FunctionalTest

User = get_user_model()

class MyListTest(FunctionalTest):
  def create_pre_authenticated_session(self, email):
    user = User.objects.create(email=email)
    session = SessionStore()
    session[SESSION_KEY] = user.pk
    session[BACKEND_SESSION_KEY] = settings.AUTHENTICATION_BACKENDS[0]
    session.save()
    self.browser.get(self.live_server_url + "/404_no_such_url/")
    self.browser.add_cookie(dict(
      name=settings.SESSION_COOKIE_NAME,
      value=session.session_key,
      path='/',
    ))
  
  def test_logged_in_users_lists_are_saved_as_my_lists(self):
    email = 'example@example.com'
    self.create_pre_authenticated_session(email)

    self.browser.get(self.live_server_url)
    self.add_list_item('Buy Cat')
    self.add_list_item('Put in Hat')
    first_list_url = self.browser.current_url

    self.browser.find_element_by_link_text('My lists').click()

    self.wait_for(
      lambda: self.browser.find_element_by_link_text('Buy Cat')
    )
    self.browser.find_element_by_link_text('Buy Cat').click()
    self.wait_for(
      lambda: self.assertEqual(self.browser.current_url, first_list_url)
    )

    self.browser.get(self.live_server_url)
    self.add_list_item('Find Cat in the Hat')
    second_list_url = self.browser.get(self.browser.current_url)

    self.browser.find_element_by_link_text('My lists').click()
    self.wait_for(
      lambda: self.browser.find_element_by_link_text('Find Cat in the Hat')
    )
    self.browser.find_element_by_link_text('Find Cat in the Hat').click()
    self.wait_for(
      lambda: self.assertEqual(self.browser.current_url, second_list_url)
    )

    self.browser.find_element_by_link_text('Log out').click()
    self.wait_for(
      lambda: self.assertEqual(self.browser.find_elements_by_link_text('My lists'), [])
    )