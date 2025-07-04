from django.db import models

# Create your models here.
# models.py

from django.db import models
from django.urls import reverse

class Category(models.Model):
    """Main Categories like Quick Links, Important Links, GST/VAT Links, etc."""
    name = models.CharField(max_length=200)
    slug = models.SlugField(unique=True)
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
        return reverse('category_detail', kwargs={'slug': self.slug})


class SubCategory(models.Model):
    """Sub-categories like Income Tax, Service Tax, etc."""
    category = models.ForeignKey(Category, on_delete=models.CASCADE, related_name='subcategories')
    name = models.CharField(max_length=200)
    slug = models.SlugField()
    description = models.TextField(blank=True, null=True)
    order = models.PositiveIntegerField(default=0)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['order', 'name']
        unique_together = ('category', 'slug')
        verbose_name_plural = "Sub Categories"

    def __str__(self):
        return f"{self.category.name} > {self.name}"

    def get_absolute_url(self):
        return reverse('subcategory_detail', kwargs={
            'category_slug': self.category.slug,
            'slug': self.slug
        })


class Link(models.Model):
    """Individual links like E-payment of Taxes, etc."""
    subcategory = models.ForeignKey(SubCategory, on_delete=models.CASCADE, related_name='links')
    title = models.CharField(max_length=300)
    url = models.URLField()
    description = models.TextField(blank=True, null=True)
    order = models.PositiveIntegerField(default=0)
    is_external = models.BooleanField(default=True)  # True for external links
    is_active = models.BooleanField(default=True)
    click_count = models.PositiveIntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['order', 'title']

    def __str__(self):
        return f"{self.subcategory.name} > {self.title}"

    def increment_click_count(self):
        """Track how many times link is clicked"""
        self.click_count += 1
        self.save(update_fields=['click_count'])


class LinkClick(models.Model):
    """Track link clicks with timestamp and IP"""
    link = models.ForeignKey(Link, on_delete=models.CASCADE, related_name='clicks')
    ip_address = models.GenericIPAddressField()
    user_agent = models.TextField(blank=True, null=True)
    clicked_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-clicked_at']

    def __str__(self):
        return f"{self.link.title} clicked at {self.clicked_at}"