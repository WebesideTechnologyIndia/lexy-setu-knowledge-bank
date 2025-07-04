from django.contrib import admin
from django.utils.html import format_html
from django.urls import reverse
from django.utils.safestring import mark_safe
from .models import (
    Category, SubCategory, Act, Chapter, Section, Rule, 
    Form, Notification, SearchHistory, Bookmark
)


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ['name', 'slug', 'order', 'subcategories_count', 'is_active', 'created_at']
    list_filter = ['is_active', 'created_at']
    search_fields = ['name', 'description']
    prepopulated_fields = {'slug': ('name',)}
    ordering = ['order', 'name']
    
    def subcategories_count(self, obj):
        return obj.subcategories.count()
    subcategories_count.short_description = 'SubCategories'


@admin.register(SubCategory)
class SubCategoryAdmin(admin.ModelAdmin):
    list_display = ['name', 'category', 'slug', 'order', 'chapters_count', 'is_active']
    list_filter = ['category', 'is_active', 'created_at']
    search_fields = ['name', 'category__name']
    prepopulated_fields = {'slug': ('name',)}
    ordering = ['category', 'order', 'name']
    
    def chapters_count(self, obj):
        return obj.chapters.count()
    chapters_count.short_description = 'Chapters'


@admin.register(Chapter)
class ChapterAdmin(admin.ModelAdmin):
    list_display = [
        'chapter_number', 'name', 'subcategory', 'parent_chapter', 
        'acts_count', 'level_indicator', 'is_active'
    ]
    list_filter = ['subcategory__category', 'subcategory', 'is_active']
    search_fields = ['name', 'chapter_number', 'subcategory__name']
    prepopulated_fields = {'slug': ('name',)}
    ordering = ['subcategory', 'order', 'chapter_number']
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('subcategory', 'parent_chapter', 'chapter_number', 'name', 'full_name', 'slug')
        }),
        ('Content', {
            'fields': ('description', 'content')
        }),
        ('Settings', {
            'fields': ('order', 'is_active')
        })
    )
    
    def acts_count(self, obj):
        return obj.acts.count()
    acts_count.short_description = 'Acts'
    
    def level_indicator(self, obj):
        level = getattr(obj, 'level', 1)
        indent = '—' * level
        return format_html(f'{indent} Level {level}')
    level_indicator.short_description = 'Hierarchy Level'


# Define inline classes first
class RuleInline(admin.TabularInline):
    model = Rule
    extra = 0
    fields = ['rule_number', 'name', 'order', 'is_active']


class FormInline(admin.TabularInline):
    model = Form
    extra = 0
    fields = ['form_number', 'name', 'order', 'is_active']


class NotificationInline(admin.TabularInline):
    model = Notification
    extra = 0
    fields = ['notification_number', 'title', 'notification_date', 'is_active']


class SectionInline(admin.TabularInline):
    model = Section
    extra = 0
    fields = ['section_number', 'name', 'order', 'is_active']


@admin.register(Act)
class ActAdmin(admin.ModelAdmin):
    list_display = [
        'name', 'act_number', 'year', 
        'get_chapter', 'get_subcategory', 'get_category',
        'sections_count', 'is_active', 'is_featured'
    ]
    list_filter = ['chapter__subcategory__category', 'chapter__subcategory', 'chapter', 'year', 'is_active', 'is_featured']
    search_fields = ['name', 'full_name', 'act_number', 'chapter__name']
    prepopulated_fields = {'slug': ('name',)}
    ordering = ['chapter__subcategory__category', 'chapter__subcategory', 'chapter', 'order', 'name']
    
    fieldsets = (
        ('Hierarchy Information', {
            'fields': ('chapter', 'get_category_readonly', 'get_subcategory_readonly')
        }),
        ('Basic Information', {
            'fields': ('name', 'full_name', 'slug')
        }),
        ('Act Details', {
            'fields': ('act_number', 'year', 'short_description', 'long_description')
        }),
        ('Dates', {
            'fields': ('enacted_date', 'effective_date', 'last_amended_date'),
            'classes': ('collapse',)
        }),
        ('Amendment Information', {
            'fields': ('amendments',),
            'classes': ('collapse',)
        }),
        ('Settings', {
            'fields': ('order', 'is_active', 'is_featured')
        })
    )

    readonly_fields = ['get_category_readonly', 'get_subcategory_readonly']
    inlines = [SectionInline, RuleInline, FormInline, NotificationInline]

    def get_chapter(self, obj):
        if obj.chapter:
            return f"Ch.{obj.chapter.chapter_number}: {obj.chapter.name}"
        return ''
    get_chapter.short_description = 'Chapter'

    def get_subcategory(self, obj):
        if obj.chapter and obj.chapter.subcategory:
            return obj.chapter.subcategory.name
        return ''
    get_subcategory.short_description = 'SubCategory'

    def get_category(self, obj):
        if obj.chapter and obj.chapter.subcategory and obj.chapter.subcategory.category:
            return obj.chapter.subcategory.category.name
        return ''
    get_category.short_description = 'Category'
    
    def get_category_readonly(self, obj):
        if obj.chapter and obj.chapter.subcategory and obj.chapter.subcategory.category:
            return obj.chapter.subcategory.category.name
        return 'No Category'
    get_category_readonly.short_description = 'Category'
    
    def get_subcategory_readonly(self, obj):
        if obj.chapter and obj.chapter.subcategory:
            return obj.chapter.subcategory.name
        return 'No SubCategory'
    get_subcategory_readonly.short_description = 'SubCategory'
    
    def sections_count(self, obj):
        return obj.sections.count()
    sections_count.short_description = 'Sections'


class RuleInlineForSection(admin.TabularInline):
    model = Rule
    extra = 0
    fields = ['rule_number', 'name', 'order', 'is_active']


class FormInlineForSection(admin.TabularInline):
    model = Form
    extra = 0
    fields = ['form_number', 'name', 'order', 'is_active']


@admin.register(Section)
class SectionAdmin(admin.ModelAdmin):
    list_display = [
        'section_number', 'name', 'act', 'parent_section', 
        'level_indicator', 'is_active'
    ]
    list_filter = ['act__chapter__subcategory__category', 'act__chapter__subcategory', 'act__chapter', 'act', 'is_active']
    search_fields = ['name', 'section_number', 'content', 'act__name']
    prepopulated_fields = {'slug': ('name',)}
    ordering = ['act__chapter__subcategory__category', 'act__chapter__subcategory', 'act__chapter', 'act', 'order', 'section_number']
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('act', 'parent_section', 'section_number', 'name', 'full_name', 'slug')
        }),
        ('Content', {
            'fields': ('content', 'short_description')
        }),
        ('Legal Information', {
            'fields': ('notes', 'amendments', 'effective_date'),
            'classes': ('collapse',)
        }),
        ('Settings', {
            'fields': ('order', 'is_active')
        })
    )
    
    inlines = [RuleInlineForSection, FormInlineForSection]
    
    def level_indicator(self, obj):
        level = 1
        parent = obj.parent_section
        while parent:
            level += 1
            parent = parent.parent_section
        indent = '—' * level
        return format_html(f'{indent} Level {level}')
    level_indicator.short_description = 'Hierarchy Level'


@admin.register(Rule)
class RuleAdmin(admin.ModelAdmin):
    list_display = ['rule_number', 'name', 'act', 'section', 'is_active']
    list_filter = ['act__chapter__subcategory__category', 'act__chapter__subcategory', 'act__chapter', 'act', 'is_active']
    search_fields = ['name', 'rule_number', 'content', 'act__name']
    prepopulated_fields = {'slug': ('name',)}
    ordering = ['act__chapter__subcategory__category', 'act__chapter__subcategory', 'act__chapter', 'act', 'order', 'rule_number']
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('act', 'section', 'rule_number', 'name', 'slug')
        }),
        ('Content', {
            'fields': ('content', 'description')
        }),
        ('Legal Information', {
            'fields': ('effective_date', 'amendments'),
            'classes': ('collapse',)
        }),
        ('Settings', {
            'fields': ('order', 'is_active')
        })
    )


@admin.register(Form)
class FormAdmin(admin.ModelAdmin):
    list_display = ['form_number', 'name', 'act', 'section', 'has_files', 'is_active']
    list_filter = ['act__chapter__subcategory__category', 'act__chapter__subcategory', 'act__chapter', 'act', 'is_active']
    search_fields = ['name', 'form_number', 'description', 'act__name']
    prepopulated_fields = {'slug': ('name',)}
    ordering = ['act__chapter__subcategory__category', 'act__chapter__subcategory', 'act__chapter', 'act', 'order', 'form_number']
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('act', 'section', 'form_number', 'name', 'slug')
        }),
        ('Content', {
            'fields': ('description', 'purpose')
        }),
        ('Files', {
            'fields': ('pdf_file', 'excel_file')
        }),
        ('Dates', {
            'fields': ('effective_date', 'last_updated_date'),
            'classes': ('collapse',)
        }),
        ('Settings', {
            'fields': ('order', 'is_active')
        })
    )
    
    def has_files(self, obj):
        files = []
        if obj.pdf_file:
            files.append('PDF')
        if obj.excel_file:
            files.append('Excel')
        return ', '.join(files) if files else 'No files'
    has_files.short_description = 'Files Available'


@admin.register(Notification)
class NotificationAdmin(admin.ModelAdmin):
    list_display = [
        'notification_number', 'title', 'act', 'notification_type', 
        'notification_date', 'has_pdf', 'is_active'
    ]
    list_filter = ['act__chapter__subcategory__category', 'act__chapter__subcategory', 'act__chapter', 'act', 'notification_type', 'is_active', 'notification_date']
    search_fields = ['title', 'notification_number', 'content', 'act__name']
    prepopulated_fields = {'slug': ('title',)}
    ordering = ['-notification_date']
    date_hierarchy = 'notification_date'
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('act', 'notification_number', 'title', 'slug', 'notification_type')
        }),
        ('Content', {
            'fields': ('content', 'summary')
        }),
        ('Dates', {
            'fields': ('notification_date', 'effective_date')
        }),
        ('File', {
            'fields': ('pdf_file',)
        }),
        ('Settings', {
            'fields': ('is_active',)
        })
    )
    
    def has_pdf(self, obj):
        return "Yes" if obj.pdf_file else "No"
    has_pdf.short_description = 'PDF Available'
    has_pdf.boolean = True


@admin.register(SearchHistory)
class SearchHistoryAdmin(admin.ModelAdmin):
    list_display = ['query', 'results_count', 'ip_address', 'created_at']
    list_filter = ['created_at', 'results_count']
    search_fields = ['query']
    ordering = ['-created_at']
    date_hierarchy = 'created_at'
    readonly_fields = ['query', 'results_count', 'ip_address', 'created_at']
    
    def has_add_permission(self, request):
        return False


@admin.register(Bookmark)
class BookmarkAdmin(admin.ModelAdmin):
    list_display = ['title', 'content_type', 'user_session', 'created_at']
    list_filter = ['content_type', 'created_at']
    search_fields = ['title', 'url']
    ordering = ['-created_at']
    date_hierarchy = 'created_at'
    readonly_fields = ['created_at']


# Custom admin site configuration
admin.site.site_header = "Tax Laws Administration"
admin.site.site_title = "Tax Laws Admin"
admin.site.index_title = "Welcome to Tax Laws Administration - Correct Hierarchy: Category → SubCategory → Chapter → Act → Section → Rule/Form/Notification"