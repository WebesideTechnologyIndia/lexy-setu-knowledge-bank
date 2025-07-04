# forms.py
from django import forms
from .models import Notification, NotificationCategory
from ckeditor.widgets import CKEditorWidget

class NotificationForm(forms.ModelForm):
    content = forms.CharField(widget=CKEditorWidget())
    
    class Meta:
        model = Notification
        fields = ['title', 'content', 'category']
        widgets = {
            'title': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Enter notification title'
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
            
            # Sub-categories (subcategories - changed from children)
            sub_categories = main_cat.subcategories.all()  # Fixed: children -> subcategories
            for sub_cat in sub_categories:
                choices.append((sub_cat.id, f"   ├── {sub_cat.display_name}"))  # Indented
        
        self.fields['category'].choices = choices
        self.fields['title'].required = True
        self.fields['content'].required = True
        self.fields['category'].required = True