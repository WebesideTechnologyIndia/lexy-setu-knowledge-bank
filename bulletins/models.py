# models.py
from django.db import models
from ckeditor.fields import RichTextField
from django.utils import timezone
import os

def notification_pdf_upload_path(instance, filename):
    """Generate upload path for notification PDFs"""
    # Create path like: notifications/2024/01/filename.pdf
    return f'notifications/{instance.notification_date.year}/{instance.notification_date.month:02d}/{filename}'

class NotificationCategory(models.Model):
    CATEGORY_CHOICES = [
        # Main Categories
        ('rbi_sebi', 'RBI SEBI'),
        ('notification', 'Notification'),
        ('circular', 'Circular'),
        ('income_tax', 'Income Tax'),
        ('service_tax', 'Service Tax'),
        ('central_sales_tax', 'Central Sales Tax'),
        ('excise_matters', 'Excise Matters'),
        ('customs', 'Customs'),
        ('company_law', 'Company Law'),
        ('labour_laws', 'Labour Laws'),
        ('fema', 'FEMA'),
        ('llp_act_2008', 'The LLP Act 2008'),
        ('accounting_standard', 'Accounting Standard (INDAS)'),
        ('others', 'Others'),
        
        # GST Categories
        ('gst', 'GST'),
        ('igst', 'IGST'),
        ('utgst', 'UTGST'),
        ('compensation_cess', 'Compensation Cess'),
        ('ibc_regulation', 'IBC Regulation'),
        
        # VAT as Direct Categories
        ('vat', 'VAT'),
        ('delhi_vat', 'Delhi VAT'),
        ('maharashtra_vat', 'Maharashtra VAT'),
        ('gujarat_vat', 'Gujarat VAT'),
        ('telangana_vat', 'Telangana VAT'),
        ('tamil_nadu_vat', 'Tamil Nadu VAT'),
        ('karnataka_vat', 'Karnataka VAT'),
        ('west_bengal_vat', 'West Bengal VAT'),
        ('rajasthan_vat', 'Rajasthan VAT'),
        ('uttar_pradesh_vat', 'Uttar Pradesh VAT'),
        ('punjab_vat', 'Punjab VAT'),
    ]

    name = models.CharField(max_length=100, choices=CATEGORY_CHOICES, unique=True)
    display_name = models.CharField(max_length=100)
    created_at = models.DateTimeField(auto_now_add=True)
    parent = models.ForeignKey('self', on_delete=models.CASCADE, null=True, blank=True, related_name='subcategories')

    def __str__(self):
        return self.display_name

    class Meta:
        verbose_name_plural = "Notification Categories"


class Notification(models.Model):
    title = models.CharField(max_length=255)
    notification_number = models.CharField(max_length=100, unique=True, help_text="Enter notification number (e.g., NOT/2024/001)")
    notification_date = models.DateField(default=timezone.now, help_text="Date of the notification")
    content = RichTextField()
    category = models.ForeignKey(NotificationCategory, on_delete=models.CASCADE, related_name='notifications')
    
    # PDF Upload Field
    pdf_file = models.FileField(
        upload_to=notification_pdf_upload_path,
        null=True,
        blank=True,
        help_text="Upload PDF file (optional)"
    )
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return f"{self.notification_number} - {self.title}"

    @property
    def has_pdf(self):
        """Check if notification has PDF file"""
        return bool(self.pdf_file)

    @property
    def pdf_filename(self):
        """Get PDF filename without path"""
        if self.pdf_file:
            return os.path.basename(self.pdf_file.name)
        return None

    @property
    def pdf_size(self):
        """Get PDF file size in MB"""
        if self.pdf_file:
            try:
                return round(self.pdf_file.size / (1024 * 1024), 2)
            except:
                return 0
        return 0

    def delete(self, *args, **kwargs):
        """Delete PDF file when notification is deleted"""
        if self.pdf_file:
            if os.path.isfile(self.pdf_file.path):
                os.remove(self.pdf_file.path)
        super().delete(*args, **kwargs)

    class Meta:
        ordering = ['-notification_date', '-created_at']
        unique_together = ['notification_number']