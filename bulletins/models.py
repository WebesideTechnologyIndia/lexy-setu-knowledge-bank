# models.py
from django.db import models
from ckeditor.fields import RichTextField
from django.utils import timezone

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
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return f"{self.notification_number} - {self.title}"

    class Meta:
        ordering = ['-notification_date', '-created_at']
        unique_together = ['notification_number']  # Ensure notification number is unique
