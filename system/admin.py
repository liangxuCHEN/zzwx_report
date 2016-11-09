from django.contrib import admin
from system.models import Report

class ReportAdmin(admin.ModelAdmin):
    list_display = ('name', 'begin_time', 'report_type')

# Register your models here.
admin.site.register(Report, ReportAdmin)