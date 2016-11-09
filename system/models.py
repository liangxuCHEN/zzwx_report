#-*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models

# Create your models here.
class AbstractReport(models.Model):
    ex_report = models.ForeignKey('self', blank=True, null=True)
    class Meta:
        abstract = True

class Report(AbstractReport):
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
    totle_order = models.IntegerField(u'总订单量', null = True, blank = True)
    totle_order_tracery = models.IntegerField(u'窗饰订单量', null = True, blank = True)
    totle_order_clotheshorse = models.IntegerField(u'晾衣架订单量',null = True, blank = True)
    totle_order_bathroom = models.IntegerField(u'卫浴订单量', null = True, blank = True)
    totle_order_doorsandwindows = models.IntegerField(u'门窗订单量', null = True, blank = True)
    totle_order_price = models.FloatField(u'订单总额',null = True, blank = True)
    totle_new_user = models.IntegerField(u'新增用户',null = True, blank = True)

