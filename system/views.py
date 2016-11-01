#-*- coding: utf-8 -*-
from django.shortcuts import render
from django.http import HttpResponseRedirect, HttpResponse
from system.models import Report
from sql import gene_report

# Create your views here.
def home(request):
    print "home"
    return render(request, 'index.html')

def report(request):
    reports = Report.objects.all()
    return render(request, 'report.html', {'reports':reports})

def report_detail(request, report_id):
    report = Report.objects.get(id=report_id)
    content = {}
    content["report"] = gene_report(report.begin_time, report.end_time)
    return render(request, 'report_detail.html', content)