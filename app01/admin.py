from django.contrib import admin

# Register your models here.

# 注册模型表，显示在admin页面中
from .models import UserInfo,Room,Book

admin.site.register(UserInfo)
admin.site.register(Room)
admin.site.register(Book)
