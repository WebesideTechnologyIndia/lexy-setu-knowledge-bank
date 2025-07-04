from django import forms
from django.forms.widgets import DateInput
from ckeditor.widgets import CKEditorWidget
from .models import (
    Category, SubCategory, Chapter, Act, Section, 
    Rule, Form, Notification
)

class CategoryForm(forms.ModelForm):
    class Meta:
        model = Category
        fields = ['name', 'description', 'icon', 'order', 'is_active']
        widgets = {
            'name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Enter category name'
            }),
            'description': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 4,
                'placeholder': 'Enter category description'
            }),
            'icon': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'e.g., fas fa-balance-scale'
            }),
            'order': forms.NumberInput(attrs={
                'class': 'form-control',
                'value': 0
            }),
            'is_active': forms.CheckboxInput(attrs={
                'class': 'form-check-input',
                'checked': True
            })
        }


class SubCategoryForm(forms.ModelForm):
    class Meta:
        model = SubCategory
        fields = ['category', 'name', 'description', 'order', 'is_active']
        widgets = {
            'category': forms.Select(attrs={
                'class': 'form-select',
                'required': True
            }),
            'name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Enter subcategory name'
            }),
            'description': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 4,
                'placeholder': 'Enter subcategory description'
            }),
            'order': forms.NumberInput(attrs={
                'class': 'form-control',
                'value': 0
            }),
            'is_active': forms.CheckboxInput(attrs={
                'class': 'form-check-input',
                'checked': True
            })
        }


class ChapterForm(forms.ModelForm):
    class Meta:
        model = Chapter
        fields = ['subcategory', 'parent_chapter', 'chapter_number', 'name', 'full_name', 
                 'description', 'content', 'order', 'is_active']
        widgets = {
            'subcategory': forms.Select(attrs={
                'class': 'form-select',
                'required': True
            }),
            'parent_chapter': forms.Select(attrs={
                'class': 'form-select'
            }),
            'chapter_number': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'e.g., I, II, 1, 2'
            }),
            'name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Enter chapter name'
            }),
            'full_name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Enter full chapter name (optional)'
            }),
            'description': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 4,
                'placeholder': 'Enter chapter description'
            }),
            'content': CKEditorWidget(attrs={
                'class': 'form-control'
            }),
            'order': forms.NumberInput(attrs={
                'class': 'form-control',
                'value': 0
            }),
            'is_active': forms.CheckboxInput(attrs={
                'class': 'form-check-input',
                'checked': True
            })
        }

# Update your ActForm in forms.py

class ActForm(forms.ModelForm):
    class Meta:
        model = Act
        fields = ['chapter', 'name', 'full_name', 'act_number', 'year', 
                 'short_description', 'long_description', 'amendments', 
                 'last_amended_date', 'enacted_date', 'effective_date', 
                 'order', 'is_active', 'is_featured']
        widgets = {
            'chapter': forms.Select(attrs={
                'class': 'form-select',
                'required': True
            }),
            'name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'e.g., Income Tax Act'
            }),
            'full_name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Full name of the act (optional)'
            }),
            'act_number': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'e.g., 43 OF 1961'
            }),
            'year': forms.NumberInput(attrs={
                'class': 'form-control',
                'placeholder': 'e.g., 1961'
            }),
            'short_description': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Brief description'
            }),
            'long_description': CKEditorWidget(attrs={
                'class': 'form-control'
            }),
            'amendments': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 4,
                'placeholder': 'Amendment details'
            }),
            'last_amended_date': DateInput(attrs={
                'class': 'form-control',
                'type': 'date'
            }),
            'enacted_date': DateInput(attrs={
                'class': 'form-control',
                'type': 'date'
            }),
            'effective_date': DateInput(attrs={
                'class': 'form-control',
                'type': 'date'
            }),
            'order': forms.NumberInput(attrs={
                'class': 'form-control',
                'value': 0
            }),
            'is_active': forms.CheckboxInput(attrs={
                'class': 'form-check-input',
                'checked': True
            }),
            'is_featured': forms.CheckboxInput(attrs={
                'class': 'form-check-input'
            })
        }
class SectionForm(forms.ModelForm):
    class Meta:
        model = Section
        fields = ['act', 'parent_section', 'section_number', 'name', 'full_name',
                 'content', 'short_description', 'notes', 'amendments', 
                 'effective_date', 'order', 'is_active']
        widgets = {
            'act': forms.Select(attrs={
                'class': 'form-select',
                'required': True
            }),
            'parent_section': forms.Select(attrs={
                'class': 'form-select'
            }),
            'section_number': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'e.g., 1, 2, 3A'
            }),
            'name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Enter section name'
            }),
            'full_name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Full section name (optional)'
            }),
            'content': CKEditorWidget(attrs={
                'class': 'form-control'
            }),
            'short_description': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Brief description'
            }),
            'notes': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 4,
                'placeholder': 'Additional notes'
            }),
            'amendments': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 4,
                'placeholder': 'Amendment details'
            }),
            'effective_date': DateInput(attrs={
                'class': 'form-control',
                'type': 'date'
            }),
            'order': forms.NumberInput(attrs={
                'class': 'form-control',
                'value': 0
            }),
            'is_active': forms.CheckboxInput(attrs={
                'class': 'form-check-input',
                'checked': True
            })
        }


class RuleForm(forms.ModelForm):
    class Meta:
        model = Rule
        fields = ['act', 'section', 'rule_number', 'name', 'content', 
                 'description', 'amendments', 'effective_date', 'order', 'is_active']
        widgets = {
            'act': forms.Select(attrs={
                'class': 'form-select',
                'required': True
            }),
            'section': forms.Select(attrs={
                'class': 'form-select'
            }),
            'rule_number': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'e.g., 1, 2A'
            }),
            'name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Enter rule name'
            }),
            'content': CKEditorWidget(attrs={
                'class': 'form-control'
            }),
            'description': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 4,
                'placeholder': 'Rule description'
            }),
            'amendments': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 4,
                'placeholder': 'Amendment details'
            }),
            'effective_date': DateInput(attrs={
                'class': 'form-control',
                'type': 'date'
            }),
            'order': forms.NumberInput(attrs={
                'class': 'form-control',
                'value': 0
            }),
            'is_active': forms.CheckboxInput(attrs={
                'class': 'form-check-input',
                'checked': True
            })
        }


class FormForm(forms.ModelForm):
    class Meta:
        model = Form
        fields = ['act', 'section', 'form_number', 'name', 'description', 
                 'purpose', 'pdf_file', 'excel_file', 'effective_date', 
                 'last_updated_date', 'order', 'is_active']
        widgets = {
            'act': forms.Select(attrs={
                'class': 'form-select',
                'required': True
            }),
            'section': forms.Select(attrs={
                'class': 'form-select'
            }),
            'form_number': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'e.g., 16, 26AS'
            }),
            'name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Enter form name'
            }),
            'description': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 4,
                'placeholder': 'Form description'
            }),
            'purpose': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Purpose of the form'
            }),
            'pdf_file': forms.FileInput(attrs={
                'class': 'form-control',
                'accept': '.pdf'
            }),
            'excel_file': forms.FileInput(attrs={
                'class': 'form-control',
                'accept': '.xls,.xlsx'
            }),
            'effective_date': DateInput(attrs={
                'class': 'form-control',
                'type': 'date'
            }),
            'last_updated_date': DateInput(attrs={
                'class': 'form-control',
                'type': 'date'
            }),
            'order': forms.NumberInput(attrs={
                'class': 'form-control',
                'value': 0
            }),
            'is_active': forms.CheckboxInput(attrs={
                'class': 'form-check-input',
                'checked': True
            })
        }


class NotificationForm(forms.ModelForm):
    class Meta:
        model = Notification
        fields = ['act', 'notification_number', 'title', 'content', 'summary',
                 'notification_date', 'effective_date', 'pdf_file', 
                 'notification_type', 'is_active']
        widgets = {
            'act': forms.Select(attrs={
                'class': 'form-select',
                'required': True
            }),
            'notification_number': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'e.g., SO 1234(E)'
            }),
            'title': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Enter notification title'
            }),
            'content': CKEditorWidget(attrs={
                'class': 'form-control'
            }),
            'summary': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 4,
                'placeholder': 'Brief summary'
            }),
            'notification_date': DateInput(attrs={
                'class': 'form-control',
                'type': 'date',
                'required': True
            }),
            'effective_date': DateInput(attrs={
                'class': 'form-control',
                'type': 'date'
            }),
            'pdf_file': forms.FileInput(attrs={
                'class': 'form-control',
                'accept': '.pdf'
            }),
            'notification_type': forms.Select(attrs={
                'class': 'form-select'
            }),
            'is_active': forms.CheckboxInput(attrs={
                'class': 'form-check-input',
                'checked': True
            })
        }