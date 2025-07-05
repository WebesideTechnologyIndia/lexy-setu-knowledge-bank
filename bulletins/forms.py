# forms.py
from django import forms
from .models import Notification, NotificationCategory
from ckeditor.widgets import CKEditorWidget

class NotificationForm(forms.ModelForm):
    content = forms.CharField(widget=CKEditorWidget())
    notification_date = forms.DateField(
        widget=forms.DateInput(attrs={
            'class': 'form-control',
            'type': 'date'
        }),
        help_text="Select the notification date"
    )
    
    class Meta:
        model = Notification
        fields = ['title', 'notification_number', 'notification_date', 'content', 'category']
        widgets = {
            'title': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Enter notification title'
            }),
            'notification_number': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Enter notification number (e.g., NOT/2024/001)'
            }),
            'category': forms.Select(attrs={
                'class': 'form-control'
            }),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Hierarchical dropdown banane ke liye
        self.fields['category'].queryset = NotificationCategory.objects.all()
        
        # Custom choices banate hain with proper grouping
        choices = [('', '---------')]  # Empty choice
        
        # Main categories (jo parent nahi hain)
        main_categories = NotificationCategory.objects.filter(parent=None)
        for main_cat in main_categories:
            choices.append((main_cat.id, main_cat.display_name))
            
            # Sub-categories
            sub_categories = main_cat.subcategories.all()
            for sub_cat in sub_categories:
                choices.append((sub_cat.id, f"   ├── {sub_cat.display_name}"))  # Indented
        
        self.fields['category'].choices = choices
        self.fields['title'].required = True
        self.fields['notification_number'].required = True
        self.fields['notification_date'].required = True
        self.fields['content'].required = True
        self.fields['category'].required = True

    def clean_notification_number(self):
        notification_number = self.cleaned_data.get('notification_number')
        if notification_number:
            # Check if notification number already exists (excluding current instance if editing)
            existing = Notification.objects.filter(notification_number=notification_number)
            if self.instance.pk:
                existing = existing.exclude(pk=self.instance.pk)
            if existing.exists():
                raise forms.ValidationError("This notification number already exists.")
        return notification_number