from django.contrib import admin
from users.models import User, Article, Thread

admin.site.register(User)
admin.site.register(Article)
admin.site.register(Thread)
