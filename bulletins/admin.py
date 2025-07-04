from django.contrib import admin

# Register your models here.
# admin.py
from django.contrib import admin
from .models import Notification, NotificationCategory

@admin.register(NotificationCategory)
class NotificationCategoryAdmin(admin.ModelAdmin):
    list_display = ['display_name', 'name', 'created_at']
    list_filter = ['created_at']
    search_fields = ['display_name', 'name']

@admin.register(Notification)
class NotificationAdmin(admin.ModelAdmin):
    list_display = ['title', 'category', 'created_at', 'is_active']
    list_filter = ['category', 'is_active', 'created_at']
    search_fields = ['title', 'content']
    list_editable = ['is_active']
    readonly_fields = ['created_at', 'updated_at']
    
    fieldsets = (
        (None, {
            'fields': ['title', 'category', 'content', 'is_active']
        }),
        ('Timestamps', {
            'fields': ['created_at', 'updated_at'],
            'classes': ['collapse']
        }), 
    )
