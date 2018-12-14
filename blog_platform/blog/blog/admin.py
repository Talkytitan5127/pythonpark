from django.contrib import admin
from blog import models

def hide_post(modeladmin, request, queryset):
    queryset.update(is_hidden=True)

def show_post(modeladmin, request, queryset):
    queryset.update(is_hidden=False)

class PostAdmin(admin.ModelAdmin):
    list_display = ('pk', 'theme', 'creation_date', 'is_hidden')
    actions = [hide_post, show_post]

class CommentAdmin(admin.ModelAdmin):
    list_display = ('post', 'author')


admin.site.register(models.Post, PostAdmin)
admin.site.register(models.Comment, CommentAdmin)