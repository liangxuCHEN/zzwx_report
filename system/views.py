#-*- coding: utf-8 -*-
from django.shortcuts import render
from django.http import HttpResponseRedirect, HttpResponse
from django.template.loader import render_to_string
from django.core.paginator import Paginator, InvalidPage, EmptyPage
from system.models import Report
from sql import gene_report
from tool import send_mail
import datetime

# Create your views here.
def home(request):
    return render(request, 'index.html')

def report(request):
    reports = Report.objects.all()
    if request.GET != {}:
        date = request.GET.get('date', '')
        report_type = request.GET.get('report_type','')
        if report_type != '':
            reports = reports.filter(report_type=report_type)
        if date != "":
            year, month, day=date.split('-')
            reports = reports.filter(begin_time__month=month)
    
    page_size =  20
    paginator = Paginator(reports, page_size)
    try:
        page = int(request.GET.get('page','1'))
    except ValueError:
        page = 1
    try:
        report_page = paginator.page(page)
    except (EmptyPage, InvalidPage):
        report_page = paginator.page(paginator.num_pages)
    
    return render(request, 'report.html', {'reports':report_page})

def report_detail(request, report_id):
    report = Report.objects.get(id=report_id)
    content = {}
    content["report"] = gene_report(report.begin_time, report.end_time, report)
    msg_txt = render(request, 'report_detail.html', content)
    mail_to = 'liangxu.chen@livingdiy.com'
    subject = report.name
    #send_mail(mail_to, subject, msg_txt.content)
    return msg_txt