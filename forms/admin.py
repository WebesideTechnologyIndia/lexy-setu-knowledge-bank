# admin.py
from django.contrib import admin
from django.utils.html import format_html
from django.urls import reverse
from django.utils.safestring import mark_safe
from .models import Category, TaxForm, FormDownload, FormLink

@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ['name', 'slug', 'order', 'forms_count', 'is_active', 'created_at']
    list_editable = ['order', 'is_active']
    list_filter = ['is_active', 'created_at']
    search_fields = ['name', 'description']
    prepopulated_fields = {'slug': ('name',)}
    ordering = ['order', 'name']

    def forms_count(self, obj):
        count = obj.forms.filter(is_active=True).count()
        if count > 0:
            url = reverse('admin:forms_taxform_changelist') + f'?category__id__exact={obj.id}'
            return format_html('<a href="{}">{} forms</a>', url, count)
        return count
    forms_count.short_description = 'Active Forms'


class FormLinkInline(admin.TabularInline):
    model = FormLink
    extra = 1
    fields = ['title', 'url', 'link_type', 'order', 'is_active']


@admin.register(TaxForm)
class TaxFormAdmin(admin.ModelAdmin):
    list_display = [
        'form_number', 'title', 'category', 'assessment_year', 
        'file_type', 'download_count', 'is_active', 'is_featured', 'order', 'created_at'
    ]
    list_editable = ['is_active', 'is_featured', 'order']
    list_filter = [
        'category', 'file_type', 'assessment_year', 'financial_year',
        'is_active', 'is_featured', 'created_at'
    ]
    search_fields = ['form_number', 'title', 'description']
    readonly_fields = ['pdf_size', 'word_size', 'excel_size', 'download_count', 'created_at', 'updated_at', 'get_file_info']
    

    fieldsets = (
    ('Basic Information', {
        'fields': ('form_number', 'title', 'category', 'description')
    }),
    ('File Uploads', {
        'fields': ('pdf_file', 'word_file', 'excel_file', 'external_url', 'file_type', 'get_file_info')
    }),
    ('File Sizes', {
        'fields': ('pdf_size', 'word_size', 'excel_size'),
        'classes': ('collapse',)
    }),
    ('Year Information', {
        'fields': ('assessment_year', 'financial_year')
    }),
    ('SEO & Meta', {
        'fields': ('meta_title', 'meta_description'),
        'classes': ('collapse',)
    }),
    ('Settings', {
        'fields': ('is_active', 'is_featured', 'order')
    }),
    ('Statistics', {
        'fields': ('download_count', 'pdf_download_count', 'word_download_count', 'excel_download_count', 'created_at', 'updated_at'),
        'classes': ('collapse',)
    })
)
    
    inlines = [FormLinkInline]
    
    def get_file_info(self, obj):
        file_info = []

        if obj.pdf_file:
            pdf_size = obj.get_file_size_display('pdf')
            file_info.append(f'<a href="{obj.pdf_file.url}" target="_blank">PDF ({pdf_size})</a>')

        if obj.word_file:
            word_size = obj.get_file_size_display('word')
            file_info.append(f'<a href="{obj.word_file.url}" target="_blank">Word ({word_size})</a>')

        if obj.excel_file:
            excel_size = obj.get_file_size_display('excel')
            file_info.append(f'<a href="{obj.excel_file.url}" target="_blank">Excel ({excel_size})</a>')

        if obj.external_url:
            file_info.append(f'<a href="{obj.external_url}" target="_blank">External Link</a>')

        if not file_info:
            return "No files uploaded"

        return format_html('<br>'.join(file_info))

    def get_queryset(self, request):
        return super().get_queryset(request).select_related('category')

    actions = ['make_active', 'make_inactive', 'make_featured', 'remove_featured']

    def make_active(self, request, queryset):
        updated = queryset.update(is_active=True)
        self.message_user(request, f'{updated} forms marked as active.')
    make_active.short_description = "Mark selected forms as active"

    def make_inactive(self, request, queryset):
        updated = queryset.update(is_active=False)
        self.message_user(request, f'{updated} forms marked as inactive.')
    make_inactive.short_description = "Mark selected forms as inactive"

    def make_featured(self, request, queryset):
        updated = queryset.update(is_featured=True)
        self.message_user(request, f'{updated} forms marked as featured.')
    make_featured.short_description = "Mark selected forms as featured"

    def remove_featured(self, request, queryset):
        updated = queryset.update(is_featured=False)
        self.message_user(request, f'{updated} forms removed from featured.')
    remove_featured.short_description = "Remove selected forms from featured"


@admin.register(FormDownload)
class FormDownloadAdmin(admin.ModelAdmin):
    list_display = ['form', 'ip_address', 'downloaded_at', 'referrer']
    list_filter = ['downloaded_at', 'form__category']
    search_fields = ['form__form_number', 'form__title', 'ip_address']
    readonly_fields = ['form', 'ip_address', 'user_agent', 'downloaded_at', 'referrer']
    date_hierarchy = 'downloaded_at'

    def has_add_permission(self, request):
        return False  # Prevent manual addition

    def has_change_permission(self, request, obj=None):
        return False  # Make read-only


@admin.register(FormLink)
class FormLinkAdmin(admin.ModelAdmin):
    list_display = ['title', 'form', 'link_type', 'order', 'is_active']
    list_editable = ['order', 'is_active']
    list_filter = ['link_type', 'is_active', 'form__category']
    search_fields = ['title', 'form__form_number', 'form__title']