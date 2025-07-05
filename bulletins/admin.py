# admin.py
from django.contrib import admin
from .models import Notification, NotificationCategory

@admin.register(NotificationCategory)
class NotificationCategoryAdmin(admin.ModelAdmin):
    list_display = ['display_name', 'name', 'parent', 'created_at']
    list_filter = ['created_at', 'parent']
    search_fields = ['display_name', 'name']
    ordering = ['display_name']

@admin.register(Notification)
class NotificationAdmin(admin.ModelAdmin):
    list_display = ['notification_number', 'title', 'notification_date', 'category', 'created_at', 'is_active']
    list_filter = ['category', 'is_active', 'notification_date', 'created_at']
    search_fields = ['title', 'notification_number', 'content']
    list_editable = ['is_active']
    readonly_fields = ['created_at', 'updated_at']
    ordering = ['-notification_date', '-created_at']
    date_hierarchy = 'notification_date'  # Date navigation at top
    
    fieldsets = (
        ('Basic Information', {
            'fields': ['title', 'notification_number', 'notification_date', 'category']
        }),
        ('Content', {
            'fields': ['content']
        }),
        ('Status', {
            'fields': ['is_active']
        }),
        ('Timestamps', {
            'fields': ['created_at', 'updated_at'],
            'classes': ['collapse']
        }), 
    )
    
    # Admin form mein date widget improve karne ke liye
    class Media:
        css = {
            'all': ('admin/css/widgets.css',)
        }
        js = ('admin/js/calendar.js', 'admin/js/admin/DateTimeShortcuts.js')

    def get_form(self, request, obj=None, **kwargs):
        form = super().get_form(request, obj, **kwargs)
        # Notification number field ko highlight karo
        form.base_fields['notification_number'].widget.attrs.update({
            'placeholder': 'e.g., NOT/2024/001'
        })
        return form