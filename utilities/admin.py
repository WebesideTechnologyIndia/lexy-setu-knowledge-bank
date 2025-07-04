from django.contrib import admin

# Register your models here.
# admin.py
from django.contrib import admin
from .models import Category, Utility

@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ['display_name', 'name', 'parent', 'is_active', 'created_at']
    list_filter = ['is_active', 'parent', 'created_at']
    search_fields = ['display_name', 'name', 'description']
    list_editable = ['is_active']
    prepopulated_fields = {'name': ('display_name',)}
    
    fieldsets = (
        (None, {
            'fields': ('display_name', 'name', 'parent')
        }),
        ('Content', {
            'fields': ('description',)
        }),
        ('Settings', {
            'fields': ('is_active',)
        }),
    )

@admin.register(Utility)
class UtilityAdmin(admin.ModelAdmin):
    list_display = ['title', 'category', 'priority', 'is_published', 'is_featured', 'created_at']
    list_filter = ['category', 'priority', 'is_published', 'is_featured', 'created_at']
    search_fields = ['title', 'content', 'tags']
    list_editable = ['priority', 'is_published', 'is_featured']
    date_hierarchy = 'created_at'
    
    fieldsets = (
        (None, {
            'fields': ('title', 'category', 'content')
        }),
        ('Settings', {
            'fields': ('priority', 'tags', 'is_published', 'is_featured')
        }),
        ('SEO', {
            'fields': ('meta_title', 'meta_description'),
            'classes': ('collapse',)
        }),
        ('Timestamps', {
            'fields': ('published_at',),
            'classes': ('collapse',)
        }),
    )
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related('category')