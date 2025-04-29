from django.contrib import admin
from .models import ward_no, dept, Post, status, Vote

# Register your models here.
admin.site.register(ward_no)
admin.site.register(dept)
admin.site.register(Post)
admin.site.register(status)
admin.site.register(Vote)