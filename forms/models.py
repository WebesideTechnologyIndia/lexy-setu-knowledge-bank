# models.py
from django.db import models
from django.urls import reverse
from django.db.models import Q  # Add this import for search functionality
from ckeditor.fields import RichTextField
import os

class Category(models.Model):
    name = models.CharField(max_length=200, unique=True)
    slug = models.SlugField(max_length=200, unique=True)
    description = models.TextField(blank=True, null=True)
    order = models.PositiveIntegerField(default=0)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['order', 'name']
        verbose_name_plural = "Categories"

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse('forms:category_forms', kwargs={'slug': self.slug})


def form_upload_path(instance, filename):
    return f'forms/{instance.category.slug}/{filename}'


class TaxForm(models.Model):
    FORM_TYPE_CHOICES = [
        ('pdf', 'PDF'),
        ('word', 'Word Document'),
        ('excel', 'Excel'),
        ('multiple', 'Multiple Formats'),
        ('other', 'Other'),
    ]

    form_number = models.CharField(max_length=50)
    title = models.CharField(max_length=300)
    description = RichTextField(blank=True, null=True)  # CKEditor field
    category = models.ForeignKey(Category, on_delete=models.CASCADE, related_name='forms')
    
    # Multiple file uploads - PDF, Word, Excel versions
    pdf_file = models.FileField(upload_to=form_upload_path, blank=True, null=True, 
                               help_text="Upload PDF version of the form")
    word_file = models.FileField(upload_to=form_upload_path, blank=True, null=True,
                                help_text="Upload Word version of the form") 
    excel_file = models.FileField(upload_to=form_upload_path, blank=True, null=True,
                                 help_text="Upload Excel version of the form")
    
    # File sizes for each format (in bytes)
    pdf_size = models.PositiveIntegerField(blank=True, null=True)
    word_size = models.PositiveIntegerField(blank=True, null=True)
    excel_size = models.PositiveIntegerField(blank=True, null=True)
    
    # Primary file type (for display purposes)
    file_type = models.CharField(max_length=20, choices=FORM_TYPE_CHOICES, default='pdf')
    
    # External URL (alternative to file upload)
    external_url = models.URLField(blank=True, null=True,
                                  help_text="Direct URL to the form if not uploading files")
    
    # Assessment Year / Financial Year
    assessment_year = models.CharField(max_length=20, blank=True, null=True)
    financial_year = models.CharField(max_length=20, blank=True, null=True)
    
    # SEO and Meta
    meta_title = models.CharField(max_length=200, blank=True, null=True)
    meta_description = models.TextField(max_length=500, blank=True, null=True)
    
    # Status and ordering
    is_active = models.BooleanField(default=True)
    is_featured = models.BooleanField(default=False)
    order = models.PositiveIntegerField(default=0)
    
    # Downloads tracking
    download_count = models.PositiveIntegerField(default=0)
    pdf_download_count = models.PositiveIntegerField(default=0)
    word_download_count = models.PositiveIntegerField(default=0)
    excel_download_count = models.PositiveIntegerField(default=0)
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['order', 'form_number']
        unique_together = ['form_number', 'assessment_year']

    def __str__(self):
        return f"{self.form_number} - {self.title}"

    def get_absolute_url(self):
        return reverse('forms:form_detail', kwargs={'pk': self.pk})

    def get_file_url(self, file_type='pdf'):
        """Returns file URL for specific format"""
        if file_type == 'pdf' and self.pdf_file:
            return self.pdf_file.url
        elif file_type == 'word' and self.word_file:
            return self.word_file.url
        elif file_type == 'excel' and self.excel_file:
            return self.excel_file.url
        elif self.external_url:
            return self.external_url
        else:
            # Return any available file
            if self.pdf_file:
                return self.pdf_file.url
            elif self.word_file:
                return self.word_file.url
            elif self.excel_file:
                return self.excel_file.url
        return None

    def get_primary_file_url(self):
        """Returns URL of the primary/default file"""
        return self.get_file_url(self.file_type)

    def get_available_formats(self):
        """Returns list of available file formats"""
        formats = []
        if self.pdf_file:
            formats.append('pdf')
        if self.word_file:
            formats.append('word')
        if self.excel_file:
            formats.append('excel')
        if self.external_url and not formats:
            formats.append('external')
        return formats

    def has_multiple_formats(self):
        """Check if form has multiple file formats"""
        return len(self.get_available_formats()) > 1

    def get_file_size_display(self, file_type='total'):
        """Convert bytes to human readable format"""
        if file_type == 'pdf' and self.pdf_size:
            size = self.pdf_size
        elif file_type == 'word' and self.word_size:
            size = self.word_size
        elif file_type == 'excel' and self.excel_size:
            size = self.excel_size
        elif file_type == 'total':
            size = (self.pdf_size or 0) + (self.word_size or 0) + (self.excel_size or 0)
        else:
            return "Unknown"
        
        if size == 0:
            return "Unknown"
        
        for unit in ['B', 'KB', 'MB', 'GB']:
            if size < 1024.0:
                return f"{size:.1f} {unit}"
            size /= 1024.0
        return f"{size:.1f} TB"

    def get_total_size(self):
        """Get total size of all files"""
        return (self.pdf_size or 0) + (self.word_size or 0) + (self.excel_size or 0)

    def increment_download_count(self, file_type='pdf'):
        """Increment download counter for specific file type"""
        self.download_count += 1
        
        if file_type == 'pdf':
            self.pdf_download_count += 1
        elif file_type == 'word':
            self.word_download_count += 1
        elif file_type == 'excel':
            self.excel_download_count += 1
        
        self.save(update_fields=['download_count', f'{file_type}_download_count'])

    def get_download_stats(self):
        """Get download statistics for all formats"""
        return {
            'total': self.download_count,
            'pdf': self.pdf_download_count,
            'word': self.word_download_count,
            'excel': self.excel_download_count
        }

    def get_most_popular_format(self):
        """Get the most downloaded file format"""
        stats = self.get_download_stats()
        formats = {'pdf': stats['pdf'], 'word': stats['word'], 'excel': stats['excel']}
        return max(formats, key=formats.get) if max(formats.values()) > 0 else 'pdf'

    def save(self, *args, **kwargs):
        # Calculate file sizes if files are uploaded
        if self.pdf_file and hasattr(self.pdf_file, 'size'):
            self.pdf_size = self.pdf_file.size
        
        if self.word_file and hasattr(self.word_file, 'size'):
            self.word_size = self.word_file.size
            
        if self.excel_file and hasattr(self.excel_file, 'size'):
            self.excel_size = self.excel_file.size

        # Determine primary file type
        available_formats = []
        if self.pdf_file:
            available_formats.append('pdf')
        if self.word_file:
            available_formats.append('word')
        if self.excel_file:
            available_formats.append('excel')
        
        if len(available_formats) > 1:
            self.file_type = 'multiple'
        elif available_formats:
            self.file_type = available_formats[0]
        elif self.external_url:
            self.file_type = 'other'
        
        # Auto-generate meta fields if not provided
        if not self.meta_title:
            self.meta_title = f"{self.form_number} - {self.title}"
        
        if not self.meta_description and self.description:
            # Strip HTML tags for meta description
            import re
            clean_desc = re.sub('<[^<]+?>', '', str(self.description))
            self.meta_description = clean_desc[:300] + "..." if len(clean_desc) > 300 else clean_desc
            
        super().save(*args, **kwargs)


class FormLink(models.Model):
    """Additional useful links related to forms"""
    LINK_TYPE_CHOICES = [
        ('official', 'Official Website'),
        ('guide', 'How-to Guide'),
        ('instruction', 'Instructions'),
        ('sample', 'Sample Form'),
        ('related', 'Related Form'),
        ('pdf_alt', 'Alternative PDF Link'),
        ('word_alt', 'Alternative Word Link'),
        ('excel_alt', 'Alternative Excel Link'),
        ('other', 'Other'),
    ]
    
    form = models.ForeignKey(TaxForm, on_delete=models.CASCADE, related_name='related_links')
    title = models.CharField(max_length=200)
    url = models.URLField()
    link_type = models.CharField(max_length=20, choices=LINK_TYPE_CHOICES, default='other')
    description = models.TextField(blank=True, null=True)
    order = models.PositiveIntegerField(default=0)
    is_active = models.BooleanField(default=True)

    class Meta:
        ordering = ['order', 'title']

    def __str__(self):
        return f"{self.form.form_number} - {self.title}"


class FormFile(models.Model):
    """Store additional files for forms (if needed for more than 3 formats)"""
    FILE_TYPE_CHOICES = [
        ('pdf', 'PDF'),
        ('word', 'Word Document'),
        ('excel', 'Excel Spreadsheet'),
        ('txt', 'Text File'),
        ('xml', 'XML File'),
        ('zip', 'ZIP Archive'),
        ('other', 'Other'),
    ]
    
    form = models.ForeignKey(TaxForm, on_delete=models.CASCADE, related_name='additional_files')
    file = models.FileField(upload_to=form_upload_path)
    file_type = models.CharField(max_length=20, choices=FILE_TYPE_CHOICES)
    file_name = models.CharField(max_length=255, blank=True)
    file_size = models.PositiveIntegerField(blank=True, null=True)
    description = models.TextField(blank=True, null=True)
    download_count = models.PositiveIntegerField(default=0)
    is_active = models.BooleanField(default=True)
    order = models.PositiveIntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['order', 'file_name']

    def __str__(self):
        return f"{self.form.form_number} - {self.file_name or self.file.name}"

    def save(self, *args, **kwargs):
        if self.file and hasattr(self.file, 'size'):
            self.file_size = self.file.size
        
        if not self.file_name and self.file:
            self.file_name = self.file.name
            
        super().save(*args, **kwargs)

    def get_file_size_display(self):
        """Convert bytes to human readable format"""
        if not self.file_size:
            return "Unknown"
        
        size = self.file_size
        for unit in ['B', 'KB', 'MB', 'GB']:
            if size < 1024.0:
                return f"{size:.1f} {unit}"
            size /= 1024.0
        return f"{size:.1f} TB"


class FormDownload(models.Model):
    """Track form downloads for analytics"""
    DOWNLOAD_TYPE_CHOICES = [
        ('pdf', 'PDF Download'),
        ('word', 'Word Download'),
        ('excel', 'Excel Download'),
        ('external', 'External Link'),
    ]
    
    form = models.ForeignKey(TaxForm, on_delete=models.CASCADE, related_name='downloads')
    download_type = models.CharField(max_length=20, choices=DOWNLOAD_TYPE_CHOICES, default='pdf')
    ip_address = models.GenericIPAddressField()
    user_agent = models.TextField(blank=True, null=True)
    downloaded_at = models.DateTimeField(auto_now_add=True)
    referrer = models.URLField(blank=True, null=True)

    class Meta:
        ordering = ['-downloaded_at']

    def __str__(self):
        return f"{self.form.form_number} ({self.download_type}) - {self.downloaded_at}"