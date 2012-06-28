# vim: set fileencoding=utf-8 :
"""
API with django-tastypie


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

    The above copyright notice and this permission notice shall be included       in
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
from django.contrib.contenttypes.models import ContentType
from tastypie import fields
from tastypie.resources import ModelResource
from tastypie.authentication import Authentication
from tastypie.authentication import BasicAuthentication
from tastypie.authorization import DjangoAuthorization
from tastypie.constants import ALL
from tagy.models import Tagy
from tagy.models import Tag


class TagyResource(ModelResource):
    label = fields.CharField(attribute='tag__label')
    content_type = fields.IntegerField(attribute='content_type__pk')

    class Meta:
        allowed_methods = ['get', 'post', 'delete']
        queryset = Tagy.objects.all()
        resource_name = 'tagy'
        authentication = BasicAuthentication()
        authorization = DjangoAuthorization()
        fields = ['label', 'content_type', 'object_id']
        include_absolute_url = True
        filtering = {
                'content_type': ['exact'],
                'object_id': ['exact'],
            }

    def hydrate(self, bundle):
        ct = ContentType.objects.get(pk=bundle.data['content_type'])
        fk = bundle.data['object_id']
        obj = ct.get_object_for_this_type(pk=fk)
        bundle.obj = Tagy.objects.add(obj, bundle.data['label'])
        return bundle

    def is_authenticated(self, request):
        # GET request is always allowed to anybody
        if request.method == 'GET':
            return True
        return super(TagyResource, self).is_authenticated(request)


class TagyTagResource(ModelResource):
    tagies = fields.ToManyField(TagyResource, attribute='tagies')

    class Meta:
        allowed_methods = ['get']
        queryset = Tag.objects.all()
        resource_name = 'tag'
        fields = ['pk', 'label', 'tagies']
        authentication = Authentication()
        include_absolute_url = True
        filtering = {
                'label': ALL,
            }
