# vim: set fileencoding=utf-8 :
"""
Unittest module of ...


AUTHOR:
    lambdalisue[Ali su ae] (lambdalisue@hashnote.net)
    
Copyright:
    Copyright 2011 Alisue allright reserved.

License:
    The MIT License (MIT)

    Copyright (c) 2012 Alisue allright reserved.

    Permission is hereby granted, free of charge, to any person obtaining a copy
    of this software and associated documentation files (the "Software"), to
    deal in the Software without restriction, including without limitation the
    rights to use, copy, modify, merge, publish, distribute, sublicense, and/or
    sell copies of the Software, and to permit persons to whom the Software is
    furnished to do so, subject to the following conditions:

    The above copyright notice and this permission notice shall be included in
    all copies or substantial portions of the Software.

    THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
    IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
    FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
    AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
    LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING
    FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS
    IN THE SOFTWARE.

"""
from __future__ import with_statement
from django.core.urlresolvers import reverse
from django.contrib.auth.models import User
from django.contrib.auth.models import Permission
from django.contrib.contenttypes.models import ContentType
from tastypie.test import ResourceTestCase
from tagy.models import Tag
from tagy.models import Tagy
from tagy.tests.models import Book


class TagyResourceTestCase(ResourceTestCase):

    def setUp(self):
        super(TagyResourceTestCase, self).setUp()

        # reverse base url of the API
        self.base_url = reverse('api_dispatch_list', kwargs={
            'resource_name': 'tagy', 'api_name': 'v1'})

        # create user for authentication
        self.username1 = 'tagy-test-user'
        self.password1 = 'tagy-test-user'
        self.user1 = User.objects.create_user(
                username=self.username1,
                email="{0}@example.com".format(self.username1),
                password=self.password1
            )
        self.username2 = 'tagy-test-user2'
        self.password2 = 'tagy-test-user2'
        self.user2 = User.objects.create_user(
                username=self.username2,
                email="{0}@example.com".format(self.username2),
                password=self.password2
            )
        # apply permissions to user1 for add/change/delete tagy
        ct = ContentType.objects.get_for_model(Tagy)
        add_permission = Permission.objects.get(codename='add_tagy', content_type=ct)
        change_permission = Permission.objects.get(codename='change_tagy', content_type=ct)
        delete_permission = Permission.objects.get(codename='delete_tagy', content_type=ct)
        self.user1.user_permissions.add(add_permission, change_permission, delete_permission)

        self.book1 = Book.objects.create(title='Book1')
        self.book2 = Book.objects.create(title='Book2')
        self.book3 = Book.objects.create(title='Book3')

        self.tagy11 = Tagy.objects.add(self.book1, 'label1')
        self.tagy12 = Tagy.objects.add(self.book1, 'label2')
        self.tagy13 = Tagy.objects.add(self.book1, 'label3')
        self.tagy14 = Tagy.objects.add(self.book1, 'label4')
        self.tagy21 = Tagy.objects.add(self.book2, 'label1')
        self.tagy22 = Tagy.objects.add(self.book2, 'label2')
        self.tagy31 = Tagy.objects.add(self.book3, 'label3')
        self.tagy32 = Tagy.objects.add(self.book3, 'label4')

        self.post_data = {
                'label': 'posted label',
                'content_type': ContentType.objects.get_for_model(Book).pk,
                'object_id': self.book1.pk,
            }

    def get_credentials1(self):
        return self.create_basic(username=self.username1, password=self.password1)

    def get_credentials2(self):
        return self.create_basic(username=self.username2, password=self.password2)

    # GET is allowed for all users include anonymous users
    def test_get_list_json(self):
        url = self.base_url
        response = self.api_client.get(url, format='json')
        self.assertValidJSONResponse(response)
        # scope out the data for correctness
        deserialized = self.deserialize(response)
        self.assertEqual(len(deserialized['objects']), 8)
        # check entire structure for the expected data
        self.assertEqual(deserialized['objects'][0], {
            'label': 'label1',
            'content_type': ContentType.objects.get_for_model(Book).pk,
            'object_id': self.book1.pk,
            'resource_uri': "{0}{1}/".format(self.base_url, self.tagy11.pk),
            'absolute_url': self.tagy11.get_absolute_url(),
        })

    def test_get_detail_json(self):
        url = "{0}{1}/".format(self.base_url, self.tagy11.pk)
        response = self.api_client.get(url, format='json')
        self.assertValidJSONResponse(response)
        # scope out the data for correctness
        deserialized = self.deserialize(response)
        self.assertKeys(deserialized, ['label', 'content_type', 'object_id', 'resource_uri', 'absolute_url'])
        self.assertEqual(deserialized['label'], 'label1')

    # POST is allowed for all authenticated users who has the permission
    def test_post_list_unauthenticated(self):
        url = self.base_url
        response = self.api_client.post(url, format='json', data=self.post_data)
        self.assertHttpUnauthorized(response)

    def test_post_list_disallowed(self):
        url = self.base_url
        response = self.api_client.post(
                url, format='json', data=self.post_data,
                authentication=self.get_credentials2())
        self.assertHttpUnauthorized(response)

    def test_post_list(self):
        url = self.base_url
        self.assertEqual(Tagy.objects.count(), 8)
        response = self.api_client.post(
                url, format='json', data=self.post_data,
                authentication=self.get_credentials1())
        self.assertHttpCreated(response)
        self.assertEqual(Tagy.objects.count(), 9)

    # PUT is not allowed for anyone
    def test_put_detail(self):
        url = "{0}{1}/".format(self.base_url, self.tagy11.pk)
        response = self.api_client.put(url, format='json', data=self.post_data)
        self.assertHttpMethodNotAllowed(response)

    # DELETE is allowed for all authenticated users who has the permission
    def test_delete_detail_unauthenticated(self):
        url = "{0}{1}/".format(self.base_url, self.tagy11.pk)
        response = self.api_client.delete(url, format='json')
        self.assertHttpUnauthorized(response)

    def test_delete_detail_disallowed(self):
        url = "{0}{1}/".format(self.base_url, self.tagy11.pk)
        response = self.api_client.delete(
                url, format='json', authentication=self.get_credentials2())
        self.assertHttpUnauthorized(response)

    def test_delete_detail(self):
        url = "{0}{1}/".format(self.base_url, self.tagy11.pk)
        self.assertEqual(Tagy.objects.count(), 8)
        response = self.api_client.delete(
                url, format='json', authentication=self.get_credentials1())
        self.assertHttpAccepted(response)
        self.assertEqual(Tagy.objects.count(), 7)


class TagyTagResourceTestCase(ResourceTestCase):

    def setUp(self):
        super(TagyTagResourceTestCase, self).setUp()

        # reverse base url of the API
        self.base_url = reverse('api_dispatch_list', kwargs={
            'resource_name': 'tag', 'api_name': 'v1'})

        self.tagy_base_url = reverse('api_dispatch_list', kwargs={
            'resource_name': 'tagy', 'api_name': 'v1'})

        self.book1 = Book.objects.create(title='Book1')
        self.book2 = Book.objects.create(title='Book2')
        self.book3 = Book.objects.create(title='Book3')

        self.tagy11 = Tagy.objects.add(self.book1, 'label1')
        self.tagy12 = Tagy.objects.add(self.book1, 'label2')
        self.tagy13 = Tagy.objects.add(self.book1, 'label3')
        self.tagy14 = Tagy.objects.add(self.book1, 'label4')
        self.tagy21 = Tagy.objects.add(self.book2, 'label1')
        self.tagy22 = Tagy.objects.add(self.book2, 'label2')
        self.tagy31 = Tagy.objects.add(self.book3, 'label3')
        self.tagy32 = Tagy.objects.add(self.book3, 'label4')

        self.tag1 = Tag.objects.get(label='label1')
        self.tag2 = Tag.objects.get(label='label2')
        self.tag3 = Tag.objects.get(label='label3')
        self.tag4 = Tag.objects.get(label='label4')

    # GET is allowed for all users include anonymous users
    def test_get_list_json(self):
        url = self.base_url
        response = self.api_client.get(url, format='json')
        self.assertValidJSONResponse(response)
        # scope out the data for correctness
        deserialized = self.deserialize(response)
        self.assertEqual(len(deserialized['objects']), 4)
        # check entire structure for the expected data
        self.assertEqual(deserialized['objects'][0], {
            'label': 'label1',
            'tagies': ["{0}{1}/".format(self.tagy_base_url, x.pk) for x in self.tag1.tagies.iterator()],
            'resource_uri': "{0}{1}/".format(self.base_url, self.tag1.pk),
            'absolute_url': self.tag1.get_absolute_url(),
        })

    def test_get_detail_json(self):
        url = "{0}{1}/".format(self.base_url, self.tag1.pk)
        response = self.api_client.get(url, format='json')
        self.assertValidJSONResponse(response)
        # scope out the data for correctness
        deserialized = self.deserialize(response)
        self.assertKeys(deserialized, ['label', 'tagies', 'resource_uri', 'absolute_url'])
        self.assertEqual(deserialized['label'], 'label1')

    # POST is not allowed for anyone
    def test_post_list(self):
        url = self.base_url
        response = self.api_client.put(url, format='json', data={})
        self.assertHttpMethodNotAllowed(response)

    # PUT is not allowed for anyone
    def test_put_detail(self):
        url = "{0}{1}/".format(self.base_url, self.tag1.pk)
        response = self.api_client.put(url, format='json', data={})
        self.assertHttpMethodNotAllowed(response)

    # DELETE is not allowed for anyone
    def test_delete_detail(self):
        url = "{0}{1}/".format(self.base_url, self.tag1.pk)
        response = self.api_client.put(url, format='json')
        self.assertHttpMethodNotAllowed(response)
