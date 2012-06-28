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
from django.test import TestCase
from tagy.models import Tag
from tagy.models import Tagy
from tagy.fields import TagField
from tagy.tests.models import Book


class TagFieldTestCase(TestCase):
    def setUp(self):
        # Hack: Add `TagField` to `Book` class programatically
        cls = Book
        name = 'tags'
        field = TagField()
        field.contribute_to_class(cls, name)

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

    def test_restricted_tagy_manager(self):
        self.assertEqual(str(self.book1.tags), 'label1, label2, label3, label4')
        self.assertEqual(self.book1.tags.count(), self.book1.tagies.count())
        self.assertQuerysetEqual(self.book1.tags.all(),
                ['label1', 'label2', 'label3', 'label4'],
                transform=lambda x: x.tag.label)

    def test_restricted_tagy_manager_add(self):
        self.assertEqual(self.book1.tags.count(), 4)
        self.book1.tags.add('hello')
        self.assertEqual(self.book1.tags.count(), 5)

    def test_restricted_tagy_manager_remove(self):
        self.assertEqual(self.book1.tags.count(), 4)
        self.book1.tags.remove('label1')
        self.assertEqual(self.book1.tags.count(), 3)

    def test_restricted_tagy_manager_apply(self):
        self.assertEqual(self.book1.tags.count(), 4)
        self.book1.tags.apply(['label1', 'label2'])
        self.assertEqual(self.book1.tags.count(), 2)
        self.assertQuerysetEqual(self.book1.tags.all(),
                ['label1', 'label2'],
                transform=lambda x: x.tag.label)
        self.book1.tags.apply("Hello, Good, Bye")
        self.assertEqual(self.book1.tags.count(), 3)
        self.assertQuerysetEqual(self.book1.tags.all(),
                ['Hello', 'Good', 'Bye'],
                transform=lambda x: x.tag.label)

    def test_descriptor(self):
        self.assertEqual(self.book1.tags.count(), 4)
        self.book1.tags = "Hello, Good, Bye"
        self.assertEqual(self.book1.tags.count(), 3)
        self.assertQuerysetEqual(self.book1.tags.all(),
                ['Hello', 'Good', 'Bye'],
                transform=lambda x: x.tag.label)
