#-*- coding: utf-8 -*-
from django.shortcuts import render
from django.http import HttpResponseRedirect, HttpResponse
from django.template.loader import render_to_string
from system.models import Report
from sql import gene_report
from tool import send_mail

# Create your views here.
def home(request):
    return render(request, 'index.html')

def report(request):
    reports = Report.objects.all()
    return render(request, 'report.html', {'reports':reports})

def report_detail(request, report_id):
    report = Report.objects.get(id=report_id)
    content = {}
    content["report"] = gene_report(report.begin_time, report.end_time, report)
    msg_txt = render(request, 'report_detail.html', content)
    mail_to = 'liangxu.chen@livingdiy.com'
    subject = report.name
    #send_mail(mail_to, subject, msg_txt.content)
    return msg_txt