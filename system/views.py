#-*- coding: utf-8 -*-
from django.shortcuts import render
from django.http import HttpResponseRedirect, HttpResponse

# Create your views here.
def home(request):
    print "home"
    return render(request, 'index.html')

def report(request):
    print "report"
    return render(request, 'report.html')