#-*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models

# Create your models here.
class Report(models.Model):
    def __unicode__(self):
        return self.name
    R_TYPE = (
        ('W', u'周报告'),
        ('M', u'月报告'),
        ('Y', u'年报告'),
    )
    name = models.CharField(u"报告", max_length = 60)
    begin_time = models.DateField()
    end_time = models.DateField()
    report_type = models.CharField(max_length = 1, choices = R_TYPE)