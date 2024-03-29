from django.test import TestCase
from lists.models import Item, List
from django.core.exceptions import ValidationError
from django.contrib.auth import get_user_model
User = get_user_model()

class ItemModelsTest(TestCase):
  def test_default_text(self):
    item = Item()
    self.assertEqual(item.text, '')

  def test_item_is_related_to_list(self):
    list_ = List.objects.create()
    item = Item()
    item.list = list_
    item.save()
    self.assertIn(item, list_.item_set.all())

  def test_cannot_save_empty_list_items(self):
    list_ = List.objects.create()
    item = Item(list=list_, text='')
    with self.assertRaises(ValidationError):
      item.save()
      item.full_clean()

  def test_duplicate_items_are_invalid(self):
    list_ = List.objects.create()
    Item.objects.create(list=list_, text='hello')
    with self.assertRaises(ValidationError):
      item = Item(list=list_, text='hello')
      item.full_clean()
  
  def test_can_save_duplicates_to_different_lists(self):
    list1 = List.objects.create()
    list2 = List.objects.create()
    Item.objects.create(list=list1, text='note')
    item = Item(list=list2, text='note')
    item.full_clean() #should not raise error

class ListModelTest(TestCase):
  def test_get_absolute_url(self):
    list_ = List.objects.create()
    self.assertEqual(list_.get_absolute_url(), f'/lists/{list_.id}/')

  def test_lists_can_have_owners(self):
    user = User.objects.create(email='a@b.com')
    list_ = List.objects.create(owner=user)
    self.assertIn(list_, user.list_set.all())
  
  def test_list_owner_is_optional(self):
    List.objects.create() #should be no error

  def test_list_name_is_first_item_text(self):
    list_ = List.objects.create()
    Item.objects.create(list=list_, text='first item')
    Item.objects.create(list=list_, text='second item')
    self.assertEqual(list_.name, 'first item')