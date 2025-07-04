from django.db import models

# Create your models here.
from django.db import models
from django.urls import reverse
from django.utils.text import slugify

class Category(models.Model):
    """
    Main categories like Direct Tax, Indirect Tax, Corporate Laws, etc.
    """
    name = models.CharField(max_length=200)
    slug = models.SlugField(max_length=200, unique=True, blank=True)
    description = models.TextField(blank=True, null=True)
    icon = models.CharField(max_length=100, blank=True, null=True)
    order = models.PositiveIntegerField(default=0)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['order', 'name']
        verbose_name_plural = "Categories"

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        if not self.slug:
            base_slug = slugify(self.name)
            slug = base_slug
            counter = 1
            while Category.objects.filter(slug=slug).exists():
                slug = f"{base_slug}-{counter}"
                counter += 1
            self.slug = slug
        super().save(*args, **kwargs)

    def get_absolute_url(self):
        return f"/rules/category/{self.slug}/"


class SubCategory(models.Model):
    """
    Sub-categories under main categories
    Category → SubCategory
    """
    category = models.ForeignKey(Category, on_delete=models.CASCADE, related_name='subcategories')
    name = models.CharField(max_length=200)
    slug = models.SlugField(max_length=200, blank=True)
    description = models.TextField(blank=True, null=True)
    order = models.PositiveIntegerField(default=0)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['order', 'name']
        unique_together = ['category', 'slug']
        verbose_name_plural = "Sub Categories"

    def __str__(self):
        return f"{self.category.name} - {self.name}"

    def save(self, *args, **kwargs):
        if not self.slug:
            base_slug = slugify(self.name)
            slug = base_slug
            counter = 1
            while SubCategory.objects.filter(category=self.category, slug=slug).exists():
                slug = f"{base_slug}-{counter}"
                counter += 1
            self.slug = slug
        super().save(*args, **kwargs)

    def get_absolute_url(self):
        return f"/rules/category/{self.category.slug}/subcategory/{self.slug}/"


class Chapter(models.Model):
    """
    Chapters under subcategories
    Category → SubCategory → Chapter
    """
    subcategory = models.ForeignKey(SubCategory, on_delete=models.CASCADE, related_name='chapters')
    parent_chapter = models.ForeignKey('self', on_delete=models.CASCADE, 
                                     blank=True, null=True, related_name='sub_chapters')
    
    chapter_number = models.CharField(max_length=50)  # e.g., "I", "II", "III", "1", "2", etc.
    name = models.CharField(max_length=500)
    full_name = models.CharField(max_length=1000, blank=True, null=True)
    slug = models.SlugField(max_length=500, blank=True)
    
    description = models.TextField(blank=True, null=True)
    content = models.TextField(blank=True, null=True)
    
    order = models.PositiveIntegerField(default=0)
    is_active = models.BooleanField(default=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['order', 'chapter_number']
        unique_together = ['subcategory', 'slug']

    def __str__(self):
        return f"Chapter {self.chapter_number}: {self.name}"

    def save(self, *args, **kwargs):
        if not self.slug:
            base_slug = slugify(f"chapter-{self.chapter_number}-{self.name}")
            slug = base_slug
            counter = 1
            while Chapter.objects.filter(subcategory=self.subcategory, slug=slug).exists():
                slug = f"{base_slug}-{counter}"
                counter += 1
            self.slug = slug
        super().save(*args, **kwargs)

    def get_absolute_url(self):
        return f"/rules/category/{self.subcategory.category.slug}/subcategory/{self.subcategory.slug}/chapter/{self.slug}/"

    @property
    def level(self):
        """Calculate the nesting level of this chapter"""
        level = 0
        parent = self.parent_chapter
        while parent:
            level += 1
            parent = parent.parent_chapter
        return level


class Rule(models.Model):
    """
    Rules under chapters (Previously Acts)
    Category → SubCategory → Chapter → Rule  (FIXED HIERARCHY)
    """
    chapter = models.ForeignKey(Chapter, on_delete=models.CASCADE, related_name='rules')
    
    name = models.CharField(max_length=300)  # e.g., "Income Tax Rules"
    full_name = models.CharField(max_length=500, blank=True, null=True)
    rule_number = models.CharField(max_length=100, blank=True, null=True)  # e.g., "1962"
    year = models.PositiveIntegerField(blank=True, null=True)
    slug = models.SlugField(max_length=300, blank=True)
    
    short_description = models.TextField(blank=True, null=True)
    long_description = models.TextField(blank=True, null=True)

    # Amendment information
    amendments = models.TextField(blank=True, null=True, help_text="Details about amendments")
    last_amended_date = models.DateField(blank=True, null=True)
    
    # Effective dates
    enacted_date = models.DateField(blank=True, null=True)
    effective_date = models.DateField(blank=True, null=True)
    
    order = models.PositiveIntegerField(default=0)
    is_active = models.BooleanField(default=True)
    is_featured = models.BooleanField(default=False)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['order', 'name']
        unique_together = ['chapter', 'slug']

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        if not self.slug:
            base_slug = slugify(self.name)
            slug = base_slug
            counter = 1
            while Rule.objects.filter(chapter=self.chapter, slug=slug).exists():
                slug = f"{base_slug}-{counter}"
                counter += 1
            self.slug = slug
        super().save(*args, **kwargs)

    def get_absolute_url(self):
        return f"/rules/category/{self.chapter.subcategory.category.slug}/subcategory/{self.chapter.subcategory.slug}/chapter/{self.chapter.slug}/rule/{self.slug}/"

    # Helper properties for easier access
    @property
    def category(self):
        return self.chapter.subcategory.category
    
    @property 
    def subcategory(self):
        return self.chapter.subcategory


class RuleSection(models.Model):
    """
    Sections within Rules (Previously Sections within Acts)
    Category → SubCategory → Chapter → Rule → RuleSection
    """
    rule = models.ForeignKey(Rule, on_delete=models.CASCADE, related_name='sections')
    parent_section = models.ForeignKey('self', on_delete=models.CASCADE, 
                                     blank=True, null=True, related_name='sub_sections')
    
    section_number = models.CharField(max_length=50)  # e.g., "1", "2", "3A", etc.
    name = models.CharField(max_length=500)
    full_name = models.CharField(max_length=1000, blank=True, null=True)
    slug = models.SlugField(max_length=500, blank=True)
    
    content = models.TextField()
    short_description = models.TextField(blank=True, null=True)
    
    # Legal references
    notes = models.TextField(blank=True, null=True)
    amendments = models.TextField(blank=True, null=True)
    effective_date = models.DateField(blank=True, null=True)
    
    order = models.PositiveIntegerField(default=0)
    is_active = models.BooleanField(default=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['order', 'section_number']
        unique_together = ['rule', 'slug']

    def __str__(self):
        return f"Section {self.section_number}: {self.name}"

    def save(self, *args, **kwargs):
        if not self.slug:
            base_slug = slugify(f"section-{self.section_number}-{self.name}")
            slug = base_slug
            counter = 1
            while RuleSection.objects.filter(rule=self.rule, slug=slug).exists():
                slug = f"{base_slug}-{counter}"
                counter += 1
            self.slug = slug
        super().save(*args, **kwargs)

    def get_absolute_url(self):
        return f"/rules/category/{self.rule.chapter.subcategory.category.slug}/subcategory/{self.rule.chapter.subcategory.slug}/chapter/{self.rule.chapter.slug}/rule/{self.rule.slug}/section/{self.slug}/"


class SubRule(models.Model):
    """
    Sub-rules associated with rule sections (Previously Rules associated with sections)
    """
    section = models.ForeignKey(RuleSection, on_delete=models.CASCADE, related_name='subrules', blank=True, null=True)
    rule = models.ForeignKey(Rule, on_delete=models.CASCADE, related_name='subrules')
    
    subrule_number = models.CharField(max_length=50)
    name = models.CharField(max_length=500)
    slug = models.SlugField(max_length=500, blank=True)
    
    content = models.TextField()
    description = models.TextField(blank=True, null=True)
    
    effective_date = models.DateField(blank=True, null=True)
    amendments = models.TextField(blank=True, null=True)
    
    order = models.PositiveIntegerField(default=0)
    is_active = models.BooleanField(default=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['order', 'subrule_number']
        unique_together = ['rule', 'slug']

    def __str__(self):
        return f"Sub-Rule {self.subrule_number}: {self.name}"

    def save(self, *args, **kwargs):
        if not self.slug:
            base_slug = slugify(f"subrule-{self.subrule_number}-{self.name}")
            slug = base_slug
            counter = 1
            while SubRule.objects.filter(rule=self.rule, slug=slug).exists():
                slug = f"{base_slug}-{counter}"
                counter += 1
            self.slug = slug
        super().save(*args, **kwargs)


class Form(models.Model):
    """
    Forms associated with rules/rule sections
    """
    rule = models.ForeignKey(Rule, on_delete=models.CASCADE, related_name='forms')
    section = models.ForeignKey(RuleSection, on_delete=models.CASCADE, related_name='forms', blank=True, null=True)
    
    form_number = models.CharField(max_length=50)
    name = models.CharField(max_length=500)
    slug = models.SlugField(max_length=500, blank=True)
    
    description = models.TextField(blank=True, null=True)
    purpose = models.TextField(blank=True, null=True)
    
    # File attachments
    pdf_file = models.FileField(upload_to='forms/pdf/', blank=True, null=True)
    excel_file = models.FileField(upload_to='forms/excel/', blank=True, null=True)
    
    effective_date = models.DateField(blank=True, null=True)
    last_updated_date = models.DateField(blank=True, null=True)
    
    order = models.PositiveIntegerField(default=0)
    is_active = models.BooleanField(default=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['order', 'form_number']
        unique_together = ['rule', 'slug']

    def __str__(self):
        return f"Form {self.form_number}: {self.name}"

    def save(self, *args, **kwargs):
        if not self.slug:
            base_slug = slugify(f"form-{self.form_number}-{self.name}")
            slug = base_slug
            counter = 1
            while Form.objects.filter(rule=self.rule, slug=slug).exists():
                slug = f"{base_slug}-{counter}"
                counter += 1
            self.slug = slug
        super().save(*args, **kwargs)


class Notification(models.Model):
    """
    Government notifications and circulars
    """
    rule = models.ForeignKey(Rule, on_delete=models.CASCADE, related_name='notifications')
    
    notification_number = models.CharField(max_length=100)
    title = models.CharField(max_length=500)
    slug = models.SlugField(max_length=500, blank=True)
    
    content = models.TextField()
    summary = models.TextField(blank=True, null=True)
    
    notification_date = models.DateField()
    effective_date = models.DateField(blank=True, null=True)
    
    # File attachment
    pdf_file = models.FileField(upload_to='notifications/', blank=True, null=True)
    
    NOTIFICATION_TYPES = [
        ('circular', 'Circular'),
        ('notification', 'Notification'),
        ('amendment', 'Amendment'),
        ('clarification', 'Clarification'),
        ('guideline', 'Guideline'),
    ]
    notification_type = models.CharField(max_length=20, choices=NOTIFICATION_TYPES, default='notification')
    
    is_active = models.BooleanField(default=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-notification_date']

    def __str__(self):
        return f"{self.notification_number}: {self.title}"

    def save(self, *args, **kwargs):
        if not self.slug:
            base_slug = slugify(f"{self.notification_number}-{self.title}")
            slug = base_slug
            counter = 1
            while Notification.objects.filter(rule=self.rule, slug=slug).exists():
                slug = f"{base_slug}-{counter}"
                counter += 1
            self.slug = slug
        super().save(*args, **kwargs)


# Search and Utility Models
class SearchHistory(models.Model):
    """
    Track search queries for analytics
    """
    query = models.CharField(max_length=500)
    results_count = models.PositiveIntegerField(default=0)
    ip_address = models.GenericIPAddressField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']
        verbose_name_plural = "Search Histories"

    def __str__(self):
        return f"{self.query} ({self.results_count} results)"


class Bookmark(models.Model):
    """
    User bookmarks for quick access
    """
    user_session = models.CharField(max_length=100)  # Session ID for anonymous users
    
    # Generic foreign key to bookmark any content
    content_type = models.CharField(max_length=50)  # 'rule', 'chapter', 'rulesection', etc.
    object_id = models.PositiveIntegerField()
    
    title = models.CharField(max_length=500)
    url = models.URLField()
    
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']
        unique_together = ['user_session', 'content_type', 'object_id']

    def __str__(self):
        return self.title