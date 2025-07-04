# forms.py
from django import forms
from ckeditor.widgets import CKEditorWidget
from .models import Utility, Category

class UtilityForm(forms.ModelForm):
    class Meta:
        model = Utility
        fields = ['title', 'category', 'content', 'priority', 'is_published', 'is_featured', 'tags', 'meta_title', 'meta_description']
        widgets = {
            'title': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Enter utility title'
            }),
            'category': forms.Select(attrs={
                'class': 'form-control'
            }),
            'content': CKEditorWidget(attrs={
                'class': 'form-control'
            }),
            'priority': forms.Select(attrs={
                'class': 'form-control'
            }),
            'tags': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Enter tags separated by commas'
            }),
            'meta_title': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'SEO Title (optional)'
            }),
            'meta_description': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'SEO Description (optional)'
            }),
            'is_published': forms.CheckboxInput(attrs={
                'class': 'form-check-input'
            }),
            'is_featured': forms.CheckboxInput(attrs={
                'class': 'form-check-input'
            }),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Filter categories to show only active ones
        self.fields['category'].queryset = Category.objects.filter(is_active=True)
        
        # Add required attribute to required fields
        self.fields['title'].required = True
        self.fields['category'].required = True
        self.fields['content'].required = True

class CategoryForm(forms.ModelForm):
    class Meta:
        model = Category
        fields = ['name', 'display_name', 'description', 'parent', 'is_active']
        widgets = {
            'name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Enter category name (for URL)'
            }),
            'display_name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Enter display name'
            }),
            'description': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Enter category description'
            }),
            'parent': forms.Select(attrs={
                'class': 'form-control'
            }),
            'is_active': forms.CheckboxInput(attrs={
                'class': 'form-check-input'
            }),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Don't allow selecting self as parent
        if self.instance.pk:
            self.fields['parent'].queryset = Category.objects.filter(is_active=True).exclude(pk=self.instance.pk)