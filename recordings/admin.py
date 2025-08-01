from django.contrib import admin
from .models import *
from django.shortcuts import render, HttpResponse, redirect
from jinja2 import Template
from django.utils.html import format_html
from django import forms
from django_ace import AceWidget
import string
import secrets
import urllib.parse
import time
from django.http import HttpResponseRedirect
import base64
import re
import requests

# Register your models here.

admin.site.site_title = "录音后台管理"
admin.site.site_header = "录音后台管理"


@admin.register(Recording)
class RecordingAdmin(admin.ModelAdmin):
    list_display = (
        "user",
        "title",
        "audio_file",
        "duration",
        "created_at",
    )

    search_fields = ("title", "user")  # list

    # exclude = []
    # form = HostConfigForm

    # def button_(self, obj):
    #     if obj.Id:
    #         print("===Password", obj.name)
    #         password = obj.password
    #         _password = urllib.parse.quote(password)
    #         private_key = re.sub(r"\s+", "", obj.host_key)

    #         return format_html(
    #             '<td class="field-name"><a     href="http://cmdb.keli.vip/DeployCen/exec_cmd/?Id={}&Cmd=/bin/bash&ws=103.63.139.134">登陆终端</td>',
    #             obj.Id,
    #         )
    #         return format_html(
    #             '<td class="field-name"><a     href="http://cmdb.keli.vip/DeployCen/exec_cmd/?Id=1202&Cmd=/bin/bash&LocalMode=no&ws=103.63.139.134&Password={}&Username={}&Host={}:{}">登陆终端</td>',
    #             _password,
    #             obj.user,
    #             obj.ip,
    #             obj.port,
    #         )

    #     else:
    #         return "-"

    # button_.short_description = format_html(
    #     '<th scope="col" class="sortable field-button_"><div class="text"><a href="?o=3">操作</a></div><div class="clear"></div></th>'
    # )
    # button_.allow_tags = True

    # def pass_(self, obj):
    #     if obj.Id:
    #         print("===Password", obj.name)
    #         return format_html(
    #             '<td class="field-name"><a  class="show_password" value="{}">查看密码</td>',
    #             obj.Id,
    #         )

    # pass_.short_description = format_html(
    #     '<th scope="col" class="sortable field-button_"><div class="text"><a href="?o=3">密码</a></div><div class="clear"></div></th>'
    # )
    # pass_.allow_tags = True

    # def Id_(self, obj):
    #     if obj.Id:
    #         print("===Password", obj.name)
    #         return format_html(
    #             '<td class="field-name"><a  value="{}" class="show_password" href="#true">{}</a></td>',
    #             obj.Id,
    #             obj.Id,
    #         )

    # Id_.short_description = format_html(
    #     '<th scope="col" class="sortable field-button_"><div class="text"><a href="?o=3">Id</a></div><div class="clear"></div></th>'
    # )
    # Id_.allow_tags = True
