# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models

# Create your models here.


class Document(models.Model):
    name = models.CharField(max_length=1000, blank=True)
    title = models.CharField(max_length=1000, blank=True)
    abstract = models.CharField(max_length=10000, blank=True)
    file_path = models.CharField(max_length=1000, blank=True)
    obtain_topic = models.IntegerField(default=2)
    expect_topic = models.IntegerField(default=2)
    is_edit = models.BooleanField(default=False)
    uploaded_at = models.DateTimeField(auto_now_add=True)
    modified_at = models.DateTimeField(null=True, blank=True)


class OverallScore(models.Model):
    document = models.ForeignKey(Document, related_name='upload_document')
    grammer_language = models.IntegerField(default=2)
    no_of_words = models.IntegerField(default=2)
    journal_title = models.IntegerField(default=2)
    author_nationality = models.IntegerField(default=2)
    article_type = models.IntegerField(default=2)
    score = models.CharField(max_length=1000, default="Intermidiate")
    created_at = models.DateTimeField(auto_now_add=True)
    created_by = models.ForeignKey('auth.Group', related_name='scoregroup')
