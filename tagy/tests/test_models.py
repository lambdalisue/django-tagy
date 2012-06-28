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
from django.db import IntegrityError
from tagy.models import Tag
from tagy.models import Tagy
from tagy.tests.models import Book


class TagyTestCase(TestCase):

    def test_tag_creation(self):
        tag1 = Tag.objects.create(label='label1')
        self.assertEqual(tag1.label, 'label1')

    def test_tagy_creation(self):
        tag1 = Tag.objects.create(label='label1')
        book1 = Book.objects.create(title='book1')
        tagy1 = Tagy.objects.create(tag=tag1, **Tagy._lookup_kwargs(book1))
        self.assertEqual(tagy1.tag, tag1)
        self.assertEqual(tagy1.content_object, book1)

    def test_tagy_add(self):
        book1 = Book.objects.create(title='book1')
        Tagy.objects.add(book1, 'label1')
        Tagy.objects.add(book1, 'label2')
        Tagy.objects.add(book1, 'label3')
        self.assertEqual(book1.tagies.count(), 3)
        self.assertEqual(
                [x.tag.label for x in book1.tagies.all()],
                ['label1', 'label2', 'label3']
            )

    def test_tagy_add_fail(self):
        book1 = Book.objects.create(title='book1')
        Tagy.objects.add(book1, 'label1')
        Tagy.objects.add(book1, 'label2')
        Tagy.objects.add(book1, 'label3')
        self.assertRaises(IntegrityError,
                Tagy.objects.add,
                book1, 'label1')

    def test_tagy_remove(self):
        book1 = Book.objects.create(title='book1')
        Tagy.objects.add(book1, 'label1')
        Tagy.objects.add(book1, 'label2')
        Tagy.objects.add(book1, 'label3')
        self.assertEqual(book1.tagies.count(), 3)

        Tagy.objects.remove(book1, 'label2')
        self.assertEqual(book1.tagies.count(), 2)
        self.assertEqual(
                [x.tag.label for x in book1.tagies.all()],
                ['label1', 'label3']
            )

    def test_tagy_remove_fail(self):
        book1 = Book.objects.create(title='book1')
        Tagy.objects.add(book1, 'label1')
        Tagy.objects.add(book1, 'label2')
        Tagy.objects.add(book1, 'label3')
        self.assertEqual(book1.tagies.count(), 3)

        self.assertRaises(Tagy.DoesNotExist,
                Tagy.objects.remove,
                book1, 'hello')

    def test_tagy_apply(self):
        book1 = Book.objects.create(title='book1')
        Tagy.objects.add(book1, 'label1')
        Tagy.objects.add(book1, 'label2')
        Tagy.objects.add(book1, 'label3')
        Tagy.objects.add(book1, 'label4')
        Tagy.objects.add(book1, 'label5')
        self.assertEqual(book1.tagies.count(), 5)
        self.assertEqual(
                [x.tag.label for x in book1.tagies.all()],
                ['label1', 'label2', 'label3', 'label4', 'label5']
            )

        Tagy.objects.apply(book1,
            ['label5', 'label3', 'label1', 'labelA', 'labelB', 'labelC'])
        self.assertEqual(book1.tagies.count(), 6)
        self.assertEqual(
                [x.tag.label for x in book1.tagies.all()],
                ['label5', 'label3', 'label1', 'labelA', 'labelB', 'labelC'],
            )

        # label2, label4 should be removed from db
        self.assertFalse(Tag.objects.filter(label='label2').exists())
        self.assertFalse(Tag.objects.filter(label='label4').exists())
