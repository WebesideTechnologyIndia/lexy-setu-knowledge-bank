# admin.py

from django.contrib import admin
from django.utils.html import format_html
from .models import Category, SubCategory, Link, LinkClick

@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ['name', 'slug', 'order', 'is_active', 'subcategory_count', 'created_at']
    list_filter = ['is_active', 'created_at']
    search_fields = ['name', 'description']
    prepopulated_fields = {'slug': ('name',)}
    list_editable = ['order', 'is_active']
    
    def subcategory_count(self, obj):
        return obj.subcategories.count()
    subcategory_count.short_description = 'Sub Categories'


class LinkInline(admin.TabularInline):
    model = Link
    extra = 0
    fields = ['title', 'url', 'order', 'is_active']
    ordering = ['order']


@admin.register(SubCategory)
class SubCategoryAdmin(admin.ModelAdmin):
    list_display = ['name', 'category', 'slug', 'order', 'is_active', 'link_count', 'created_at']
    list_filter = ['category', 'is_active', 'created_at']
    search_fields = ['name', 'description', 'category__name']
    prepopulated_fields = {'slug': ('name',)}
    list_editable = ['order', 'is_active']
    inlines = [LinkInline]
    
    def link_count(self, obj):
        return obj.links.count()
    link_count.short_description = 'Links'


@admin.register(Link)
class LinkAdmin(admin.ModelAdmin):
    list_display = ['title', 'subcategory', 'category_name', 'url_display', 'order', 'click_count', 'is_active', 'created_at']
    list_filter = ['subcategory__category', 'subcategory', 'is_active', 'is_external', 'created_at']
    search_fields = ['title', 'url', 'description', 'subcategory__name']
    list_editable = ['order', 'is_active']
    readonly_fields = ['click_count']
    
    def category_name(self, obj):
        return obj.subcategory.category.name
    category_name.short_description = 'Category'
    
    def url_display(self, obj):
        return format_html('<a href="{}" target="_blank">{}</a>', obj.url, obj.url[:50] + '...' if len(obj.url) > 50 else obj.url)
    url_display.short_description = 'URL'


@admin.register(LinkClick)
class LinkClickAdmin(admin.ModelAdmin):
    list_display = ['link', 'ip_address', 'clicked_at']
    list_filter = ['clicked_at', 'link__subcategory__category']
    search_fields = ['link__title', 'ip_address']
    readonly_fields = ['link', 'ip_address', 'user_agent', 'clicked_at']
    
    def has_add_permission(self, request):
        return False  # Don't allow manual creation