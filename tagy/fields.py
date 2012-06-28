# vim: set fileencoding=utf-8 :
"""
Fields


AUTHOR:
    lambdalisue[Ali su ae] (lambdalisue@hashnote.net)

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
from django.db import models
from django.utils.translation import ugettext_lazy as _
from tagy.models import Tagy
from tagy.models import TagyManager


class RestrictedTagyManager(models.Manager):
    def __init__(self, model, instance, through=None):
        self.through = through or Tagy.objects
        self.model = model
        self.instance = instance

    def get_query_set(self):
        return self.through.get_for_object(self.instance)

    def add(self, label):
        self.through.add(self.instance, label)

    def remove(self, label):
        self.through.remove(self.instance, label)

    def apply(self, labels):
        self.through.apply(self.instance, labels)

    def __unicode__(self):
        return Tagy.to_string(self.all())

    def __str__(self):
        return self.__unicode__().encode('utf-8')


# Virtual field
class TagField(object):
    description = 'A commna-separated list of tags.'

    def __init__(self, verbose_name=None, name=None):
        self.name = name
        self.verbose_name = verbose_name

    def set_attributes_from_name(self, name):
        if not self.name:
            self.name = name
        self.attname = self.name
        if self.verbose_name is None and self.name:
            self.verbose_name = self.name.replace('_', ' ')

    def contribute_to_class(self, cls, name):
        self.set_attributes_from_name(name)
        self.model = cls
        cls._meta.add_virtual_field(self)
        setattr(cls, name, self)

    def __get__(self, instance, model):
        if instance is None:
            # return tags related to the model
            return Tagy.objects.get_for_model(model)
        if instance.pk is None:
            raise ValueError("%s objects need to have a primary key value "
                    "before you can access their tags." % models.__name__)
        # return tags related to the instance
        return RestrictedTagyManager(model=model, instance=instance)

    def __set__(self, instance, value):
        if instance is None:
            raise AttributeError(_('%s can only be set on instances.') % self.name)
        Tagy.objects.apply(instance, value)

    def __delete__(self, instance):
        Tagy.objects.apply(instance, '')
