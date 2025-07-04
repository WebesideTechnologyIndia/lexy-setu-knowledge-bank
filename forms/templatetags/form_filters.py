# forms/templatetags/form_filters.py
from django import template
from django.utils.safestring import mark_safe
import re
import os

register = template.Library()

@register.filter
def basename(value):
    """Return the base name of a file path"""
    if not value:
        return ''
    return os.path.basename(str(value))

@register.filter
def highlight(text, search):
    """Highlight search terms in text"""
    if not search or not text:
        return text
    
    # Escape special regex characters
    search = re.escape(search)
    
    # Create regex pattern for case-insensitive search
    pattern = re.compile(f'({search})', re.IGNORECASE)
    
    # Replace with highlighted version
    highlighted = pattern.sub(r'<mark class="bg-warning text-dark">\1</mark>', str(text))
    
    return mark_safe(highlighted)

@register.filter
def file_icon(file_type):
    """Return appropriate icon for file type"""
    icons = {
        'pdf': 'fas fa-file-pdf text-danger',
        'word': 'fas fa-file-word text-primary',
        'excel': 'fas fa-file-excel text-success',
        'other': 'fas fa-file text-secondary'
    }
    return icons.get(file_type, 'fas fa-file text-secondary')

@register.filter
def truncate_filename(filename, length=20):
    """Truncate filename if too long"""
    if not filename or len(filename) <= length:
        return filename
    
    name, ext = filename.rsplit('.', 1)
    if len(name) > length - len(ext) - 3:
        name = name[:length - len(ext) - 3] + '...'
    return f"{name}.{ext}"

@register.simple_tag
def category_icon(category_name):
    """Return appropriate icon for category"""
    category_lower = category_name.lower()
    
    if 'income' in category_lower or 'itr' in category_lower:
        return 'fas fa-calculator'
    elif 'roc' in category_lower:
        return 'fas fa-building'
    elif 'gst' in category_lower:
        return 'fas fa-receipt'
    elif 'company' in category_lower:
        return 'fas fa-briefcase'
    elif 'llp' in category_lower:
        return 'fas fa-handshake'
    elif 'wealth' in category_lower:
        return 'fas fa-coins'
    elif 'service' in category_lower:
        return 'fas fa-tools'
    elif 'fema' in category_lower:
        return 'fas fa-globe'
    else:
        return 'fas fa-file-alt'