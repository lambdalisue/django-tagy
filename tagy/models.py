# vim: set fileencoding=utf-8 :
"""
Models


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
from urllib import quote_plus
from django.db import models
from django.db.models import Max
from django.db.models import Count
from django.db.models.query import QuerySet
from django.core.urlresolvers import NoReverseMatch
from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes.generic import GenericForeignKey
from django.utils.translation import ugettext_lazy as _
from tagy.utils import tagging


LABEL_MAX_LENGTH = 120


class TagManager(models.Manager):
    def get_for_model(self, model):
        ct = ContentType.objects.get_for_model(model)
        return self.filter(tagies__content_type=ct).distinct()

    def get_for_object(self, obj):
        qs = self.get_for_model(obj)
        return qs.filter(tagies__object_id=obj.pk)

    def remove_unused(self):
        """remove unused tags"""
        qs = self.annotate(num_tagy=Count('tagies'))
        qs = qs.filter(num_tagy=0)
        qs.delete()


class Tag(models.Model):
    """A tag model class"""
    label = models.CharField(_('label'),
            max_length=LABEL_MAX_LENGTH,
            unique=True, db_index=True)

    objects = TagManager()

    class Meta:
        ordering = ('label',)
        verbose_name = _('tag')
        verbose_name_plural = _('tags')

    def __unicode__(self):
        return self.label

    @property
    def _url_safe_label(self):
        return quote_plus(self.label)

    @models.permalink
    def get_absolute_url(self):
        return ('tagy-tag-detail', (), {'slug': self._url_safe_label})


class TagyManager(models.Manager):
    def get_for_model(self, model):
        ct = ContentType.objects.get_for_model(model)
        return self.filter(content_type=ct)

    def get_for_object(self, obj):
        qs = self.get_for_model(obj)
        return qs.filter(object_id=obj.pk)

    def add(self, obj, label):
        """get or create a tagy"""
        # get or create a tag with the label
        tag = Tag.objects.get_or_create(label=label)[0]
        # get or create a tagy with the tag
        kwargs = Tagy._lookup_kwargs(obj)
        tagy = self.create(tag=tag, **kwargs)
        return tagy

    def remove(self, obj, label):
        """remove a tagy"""
        tagy = self.get_for_object(obj).get(tag__label=label)
        # remove the tagy
        tagy.delete()
        # check the related tag and remove if the tag is no longer required
        if tagy.tag.tagies.count() == 0:
            tagy.tag.delete()
        return tagy

    def apply(self, obj, labels):
        """apply labels to the object"""
        # clear tags related to the object
        self.get_for_object(obj).delete()
        # convert labels if necessary
        if isinstance(labels, basestring):
            labels = tagging.parse_tags(labels)
        # add all tags
        tagies = []
        for label in labels:
            tagies.append(self.add(obj, label))
        # remove unused tags
        Tag.objects.remove_unused()
        return tagies


class Tagy(models.Model):
    """A bridge model between a tag and a object"""
    tag = models.ForeignKey(Tag, related_name='tagies')
    content_type = models.ForeignKey(ContentType)
    object_id = models.PositiveIntegerField()
    content_object = GenericForeignKey(
            ct_field='content_type', fk_field='object_id')
    sortkey = models.PositiveIntegerField(default=0)

    objects = TagyManager()

    class Meta:
        ordering = ['sortkey']
        unique_together = ('tag', 'content_type', 'object_id')
        verbose_name = _('tagy')
        verbose_name_plural = _('tagies')

    def __unicode__(self):
        return "%s - %s" % (self.tag, self.content_object)

    def get_absolute_url(self):
        if self.content_object and hasattr(self.content_object, 'get_absolute_url'):
            try:
                return self.content_object.get_absolute_url()
            except NoReverseMatch:  # ignore reverse error
                pass
        return None

    def save(self, *args, **kwargs):
        if self.sortkey == 0:
            qs = Tagy.objects.get_for_object(self.content_object)
            if qs.count() > 0:
                result = qs.aggregate(sortkey_max=Max('sortkey'))
                self.sortkey = result['sortkey_max'] + 1
            else:
                self.sortkey = 1
        return super(Tagy, self).save(*args, **kwargs)

    @classmethod
    def _lookup_kwargs(cls, obj):
        ct = ContentType.objects.get_for_model(obj)
        return {'content_type': ct, 'object_id': obj.pk}

    @classmethod
    def to_string(cls, tagies):
        if isinstance(tagies, (list, tuple)):
            iterator = tagies
        elif isinstance(tagies, QuerySet):
            iterator = tagies.iterator()
        else:
            iterator = [tagies]
        # convert tagies to django-tagging like objects list
        tags = [tagging.MockTagging(x) for x in iterator]
        # convert list of tags to comma separated string
        return tagging.edit_string_for_tags(tags)
