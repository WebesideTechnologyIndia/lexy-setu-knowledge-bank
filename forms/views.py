from django.shortcuts import render

# Create your views here.
# views.py
from django.shortcuts import render, get_object_or_404, redirect
from django.http import HttpResponse, JsonResponse
from django.db.models import Q, Count
from django.core.paginator import Paginator
from django.views.decorators.csrf import csrf_exempt
from django.views.generic import ListView, DetailView
from django.contrib import messages
from django.urls import reverse
from .models import Category, TaxForm, FormDownload, FormLink
import json
from django.views.decorators.http import require_http_methods
from django.utils.text import slugify



def get_client_ip(request):
    """Get client IP address"""
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0]
    else:
        ip = request.META.get('REMOTE_ADDR')
    return ip

def home_view(request):
    """Homepage with categories and featured forms"""
    categories = Category.objects.filter(is_active=True)
    featured_forms = TaxForm.objects.filter(is_active=True, is_featured=True)[:6]
    recent_forms = TaxForm.objects.filter(is_active=True).order_by('-created_at')[:8]
    
    # Get popular forms (most downloaded)
    popular_forms = TaxForm.objects.filter(is_active=True).order_by('-download_count')[:6]
    
    context = {
        'categories': categories,
        'featured_forms': featured_forms,
        'recent_forms': recent_forms,
        'popular_forms': popular_forms,
    }
    return render(request, 'forms/home.html', context)

def category_forms_view(request, slug):
    """Display forms by category with search and filtering"""
    category = get_object_or_404(Category, slug=slug, is_active=True)
    
    # Get forms for this category
    forms_queryset = TaxForm.objects.filter(category=category, is_active=True)
    
    # Search functionality
    search_query = request.GET.get('search', '')
    if search_query:
        forms_queryset = forms_queryset.filter(
            Q(form_number__icontains=search_query) |
            Q(title__icontains=search_query) |
            Q(description__icontains=search_query)
        )
    
    # Filter by assessment year
    year_filter = request.GET.get('year', '')
    if year_filter:
        forms_queryset = forms_queryset.filter(assessment_year=year_filter)
    
    # Filter by file type
    file_type_filter = request.GET.get('file_type', '')
    if file_type_filter:
        forms_queryset = forms_queryset.filter(file_type=file_type_filter)
    
    # Get available years and file types for filters
    available_years = forms_queryset.values_list('assessment_year', flat=True).distinct()
    available_file_types = forms_queryset.values_list('file_type', flat=True).distinct()
    
    # Pagination
    paginator = Paginator(forms_queryset, 20)  # 20 forms per page
    page_number = request.GET.get('page')
    forms = paginator.get_page(page_number)
    
    context = {
        'category': category,
        'forms': forms,
        'search_query': search_query,
        'year_filter': year_filter,
        'file_type_filter': file_type_filter,
        'available_years': available_years,
        'available_file_types': available_file_types,
    }
    return render(request, 'forms/category_forms.html', context)

def form_detail_view(request, pk):
    """Form detail page"""
    form = get_object_or_404(TaxForm, pk=pk, is_active=True)
    
    # Get related forms from same category
    related_forms = TaxForm.objects.filter(
        category=form.category, 
        is_active=True
    ).exclude(pk=form.pk)[:5]
    
    context = {
        'form': form,
        'related_forms': related_forms,
    }
    return render(request, 'forms/form_detail.html', context)


def download_form_view(request, pk):
    """Handle form download and track analytics"""
    form = get_object_or_404(TaxForm, pk=pk, is_active=True)
    
    # Get requested file type from query parameter
    file_type = request.GET.get('type', 'pdf')
    
    # Track download with specific file type
    FormDownload.objects.create(
        form=form,
        download_type=file_type,
        ip_address=get_client_ip(request),
        user_agent=request.META.get('HTTP_USER_AGENT', ''),
        referrer=request.META.get('HTTP_REFERER', '')
    )
    
    # Increment download counter for specific file type
    form.increment_download_count(file_type)
    
    # Get file URL based on type
    file_url = form.get_file_url(file_type)
    
    if file_url:
        return redirect(file_url)
    else:
        messages.error(request, f'{file_type.upper()} file not available for download.')
        return redirect('forms:form_detail', pk=form.pk)



def search_forms_view(request):
    """Global search across all forms"""
    search_query = request.GET.get('q', '')
    category_filter = request.GET.get('category', '')
    year_filter = request.GET.get('year', '')
    
    forms_queryset = TaxForm.objects.filter(is_active=True)
    
    if search_query:
        forms_queryset = forms_queryset.filter(
            Q(form_number__icontains=search_query) |
            Q(title__icontains=search_query) |
            Q(description__icontains=search_query)
        )
    
    if category_filter:
        forms_queryset = forms_queryset.filter(category__slug=category_filter)
    
    if year_filter:
        forms_queryset = forms_queryset.filter(assessment_year=year_filter)
    
    # Get filter options
    categories = Category.objects.filter(is_active=True)
    available_years = TaxForm.objects.filter(is_active=True).values_list('assessment_year', flat=True).distinct()
    
    # Pagination
    paginator = Paginator(forms_queryset, 20)
    page_number = request.GET.get('page')
    forms = paginator.get_page(page_number)
    
    context = {
        'forms': forms,
        'search_query': search_query,
        'category_filter': category_filter,
        'year_filter': year_filter,
        'categories': categories,
        'available_years': available_years,
    }
    return render(request, 'forms/search_results.html', context)

@csrf_exempt
def ajax_search_forms(request):
    """AJAX search for autocomplete"""
    if request.method == 'GET':
        query = request.GET.get('q', '')
        if len(query) >= 2:  # Start searching after 2 characters
            forms = TaxForm.objects.filter(
                Q(form_number__icontains=query) |
                Q(title__icontains=query),
                is_active=True
            )[:10]  # Limit to 10 results
            
            results = []
            for form in forms:
                results.append({
                    'id': form.pk,
                    'form_number': form.form_number,
                    'title': form.title,
                    'category': form.category.name,
                    'url': form.get_absolute_url()
                })
            
            return JsonResponse({'results': results})
    
    return JsonResponse({'results': []})

def forms_by_year_view(request, year):
    """Display forms by assessment year"""
    forms_queryset = TaxForm.objects.filter(
        assessment_year=year, 
        is_active=True
    ).select_related('category')
    
    # Group by category
    forms_by_category = {}
    for form in forms_queryset:
        category_name = form.category.name
        if category_name not in forms_by_category:
            forms_by_category[category_name] = []
        forms_by_category[category_name].append(form)
    
    context = {
        'year': year,
        'forms_by_category': forms_by_category,
        'total_forms': forms_queryset.count()
    }
    return render(request, 'forms/forms_by_year.html', context)

def popular_forms_view(request):
    """Display most downloaded forms"""
    forms = TaxForm.objects.filter(
        is_active=True,
        download_count__gt=0
    ).order_by('-download_count')[:50]
    
    context = {
        'forms': forms,
        'title': 'Most Popular Forms'
    }
    return render(request, 'forms/popular_forms.html', context)

def recent_forms_view(request):
    """Display recently added forms"""
    forms = TaxForm.objects.filter(
        is_active=True
    ).order_by('-created_at')[:50]
    
    context = {
        'forms': forms,
        'title': 'Recently Added Forms'
    }
    return render(request, 'forms/recent_forms.html', context)

# API Views for mobile app or external integration
def api_categories(request):
    """API endpoint for categories"""
    categories = Category.objects.filter(is_active=True).values(
        'id', 'name', 'slug', 'description'
    )
    return JsonResponse(list(categories), safe=False)

def api_forms_by_category(request, category_slug):
    """API endpoint for forms by category"""
    category = get_object_or_404(Category, slug=category_slug, is_active=True)
    forms = TaxForm.objects.filter(
        category=category, 
        is_active=True
    ).values(
        'id', 'form_number', 'title', 'description', 
        'assessment_year', 'file_type', 'download_count'
    )
    return JsonResponse(list(forms), safe=False)


def upload_form_view(request):
    """Form upload page where users can upload forms and get URLs"""
    categories = Category.objects.filter(is_active=True)
    
    if request.method == 'POST':
        try:
            # Get form data
            form_number = request.POST.get('form_number')
            title = request.POST.get('title')
            category_id = request.POST.get('category')
            assessment_year = request.POST.get('assessment_year')
            description = request.POST.get('description')
            external_url = request.POST.get('external_url')
            is_featured = request.POST.get('is_featured') == 'on'
            is_active = request.POST.get('is_active') == 'on'
            
            # Get category
            category = get_object_or_404(Category, id=category_id)
            
            # Create form instance
            form = TaxForm.objects.create(
                form_number=form_number,
                title=title,
                category=category,
                assessment_year=assessment_year,
                description=description,
                external_url=external_url,
                is_featured=is_featured,
                is_active=is_active
            )
            
            # Handle multiple file uploads
            uploaded_files = []
            total_size = 0
            
            # Handle PDF file
            if 'pdf_file' in request.FILES:
                form.pdf_file = request.FILES['pdf_file']
                uploaded_files.append('PDF')
                total_size += request.FILES['pdf_file'].size
            
            # Handle Word file
            if 'word_file' in request.FILES:
                form.word_file = request.FILES['word_file']
                uploaded_files.append('Word')
                total_size += request.FILES['word_file'].size
            
            # Handle Excel file
            if 'excel_file' in request.FILES:
                form.excel_file = request.FILES['excel_file']
                uploaded_files.append('Excel')
                total_size += request.FILES['excel_file'].size
            
            form.save()
            
            # Format total size for display
            def format_size(size_bytes):
                if size_bytes == 0:
                    return "0 B"
                for unit in ['B', 'KB', 'MB', 'GB']:
                    if size_bytes < 1024.0:
                        return f"{size_bytes:.1f} {unit}"
                    size_bytes /= 1024.0
                return f"{size_bytes:.1f} TB"
            
            # Return JSON response with URLs
            return JsonResponse({
                'success': True,
                'form_number': form.form_number,
                'title': form.title,
                'category': form.category.name,
                'assessment_year': form.assessment_year,
                'has_pdf': bool(form.pdf_file),
                'has_word': bool(form.word_file),
                'has_excel': bool(form.excel_file),
                'uploaded_formats': uploaded_files,
                'total_size': format_size(total_size),
                'download_url': request.build_absolute_uri(reverse('forms:download_form', kwargs={'pk': form.pk})),
                'detail_url': request.build_absolute_uri(reverse('forms:form_detail', kwargs={'pk': form.pk})),
                'admin_url': request.build_absolute_uri(reverse('admin:forms_taxform_change', args=[form.pk])),
            })
            
        except Exception as e:
            return JsonResponse({
                'success': False,
                'error': str(e)
            })
    
    # GET request - show upload form
    context = {
        'categories': categories,
    }
    return render(request, 'forms/upload_form.html', context)


def popular_forms_view(request):
    """Display most downloaded forms"""
    forms = TaxForm.objects.filter(
        is_active=True,
        download_count__gt=0
    ).order_by('-download_count')[:50]
    
    # Pagination
    paginator = Paginator(forms, 20)
    page_number = request.GET.get('page')
    forms_page = paginator.get_page(page_number)
    
    context = {
        'forms': forms_page,
        'title': 'Most Popular Forms',
        'description': 'Forms with the highest download counts'
    }
    return render(request, 'forms/popular_forms.html', context)


def recent_forms_view(request):
    """Display recently added forms"""
    forms = TaxForm.objects.filter(
        is_active=True
    ).order_by('-created_at')[:50]
    
    # Pagination
    paginator = Paginator(forms, 20)
    page_number = request.GET.get('page')
    forms_page = paginator.get_page(page_number)
    
    context = {
        'forms': forms_page,
        'title': 'Recently Added Forms',
        'description': 'Latest forms added to our collection'
    }
    return render(request, 'forms/recent_forms.html', context)



def recent_forms_view(request):
    """Display recently added forms"""
    forms = TaxForm.objects.filter(
        is_active=True
    ).order_by('-created_at')[:50]
    
    # Pagination
    paginator = Paginator(forms, 20)
    page_number = request.GET.get('page')
    forms_page = paginator.get_page(page_number)
    
    context = {
        'forms': forms_page,
        'title': 'Recently Added Forms',
        'description': 'Latest forms added to our collection'
    }
    return render(request, 'forms/recent_forms.html', context)

def forms_by_year_view(request, year):
    """Display forms by assessment year"""
    forms_queryset = TaxForm.objects.filter(
        assessment_year=year, 
        is_active=True
    ).select_related('category')
    
    # Group by category
    forms_by_category = {}
    for form in forms_queryset:
        category_name = form.category.name
        if category_name not in forms_by_category:
            forms_by_category[category_name] = []
        forms_by_category[category_name].append(form)
    
    context = {
        'year': year,
        'forms_by_category': forms_by_category,
        'total_forms': forms_queryset.count()
    }
    return render(request, 'forms/forms_by_year.html', context)


# Template filter to highlight search terms
from django import template
from django.utils.safestring import mark_safe
import re

register = template.Library()

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
    highlighted = pattern.sub(r'<mark class="bg-warning">\1</mark>', str(text))
    
    return mark_safe(highlighted)



# Add these views to your views.py file

import json
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from django.utils.text import slugify

def manage_categories_view(request):
    """Category management page"""
    categories = Category.objects.all().order_by('order', 'name')
    
    context = {
        'categories': categories,
    }
    return render(request, 'forms/manage_categories.html', context)

@require_http_methods(["POST"])
def add_category_view(request):
    """Add new category via AJAX"""
    try:
        name = request.POST.get('name')
        slug = request.POST.get('slug')
        description = request.POST.get('description', '')
        order = int(request.POST.get('order', 1))
        is_active = request.POST.get('is_active') == 'on'
        
        # Auto-generate slug if not provided
        if not slug:
            slug = slugify(name)
        
        # Check if slug already exists
        if Category.objects.filter(slug=slug).exists():
            return JsonResponse({
                'success': False,
                'error': f'A category with slug "{slug}" already exists'
            })
        
        # Create category
        category = Category.objects.create(
            name=name,
            slug=slug,
            description=description,
            order=order,
            is_active=is_active
        )
        
        return JsonResponse({
            'success': True,
            'category': {
                'id': category.id,
                'name': category.name,
                'slug': category.slug,
                'description': category.description,
                'order': category.order,
                'is_active': category.is_active
            }
        })
        
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': str(e)
        })

def get_category_view(request, category_id):
    """Get category data for editing"""
    try:
        category = Category.objects.get(id=category_id)
        return JsonResponse({
            'success': True,
            'category': {
                'id': category.id,
                'name': category.name,
                'slug': category.slug,
                'description': category.description,
                'order': category.order,
                'is_active': category.is_active
            }
        })
    except Category.DoesNotExist:
        return JsonResponse({
            'success': False,
            'error': 'Category not found'
        })

@require_http_methods(["POST"])
def update_category_view(request):
    """Update category via AJAX"""
    try:
        category_id = request.POST.get('category_id')
        name = request.POST.get('name')
        slug = request.POST.get('slug')
        description = request.POST.get('description', '')
        order = int(request.POST.get('order', 1))
        is_active = request.POST.get('is_active') == 'on'
        
        category = Category.objects.get(id=category_id)
        
        # Check if slug already exists (excluding current category)
        if Category.objects.filter(slug=slug).exclude(id=category_id).exists():
            return JsonResponse({
                'success': False,
                'error': f'A category with slug "{slug}" already exists'
            })
        
        # Update category
        category.name = name
        category.slug = slug
        category.description = description
        category.order = order
        category.is_active = is_active
        category.save()
        
        return JsonResponse({
            'success': True,
            'message': 'Category updated successfully'
        })
        
    except Category.DoesNotExist:
        return JsonResponse({
            'success': False,
            'error': 'Category not found'
        })
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': str(e)
        })

@require_http_methods(["POST"])
def delete_category_view(request):
    """Delete category via AJAX"""
    try:
        data = json.loads(request.body)
        category_id = data.get('category_id')
        
        category = Category.objects.get(id=category_id)
        
        # Check if category has forms
        if category.forms.exists():
            return JsonResponse({
                'success': False,
                'error': f'Cannot delete category "{category.name}" because it contains {category.forms.count()} forms. Please move or delete the forms first.'
            })
        
        category.delete()
        
        return JsonResponse({
            'success': True,
            'message': 'Category deleted successfully'
        })
        
    except Category.DoesNotExist:
        return JsonResponse({
            'success': False,
            'error': 'Category not found'
        })
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': str(e)
        })

@require_http_methods(["POST"])
def reorder_categories_view(request):
    """Reorder categories via AJAX"""
    try:
        data = json.loads(request.body)
        order_list = data.get('order', [])
        
        # Update order for each category
        for index, category_id in enumerate(order_list, 1):
            Category.objects.filter(id=category_id).update(order=index)
        
        return JsonResponse({
            'success': True,
            'message': 'Category order updated successfully'
        })
        
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': str(e)
        })

def manage_forms_view(request):
    """Forms management page (placeholder)"""
    category_id = request.GET.get('category')
    
    forms_queryset = TaxForm.objects.all()
    if category_id:
        forms_queryset = forms_queryset.filter(category_id=category_id)
    
    categories = Category.objects.filter(is_active=True)
    
    # Pagination
    paginator = Paginator(forms_queryset, 20)
    page_number = request.GET.get('page')
    forms = paginator.get_page(page_number)
    
    context = {
        'forms': forms,
        'categories': categories,
        'selected_category': category_id
    }
    return render(request, 'forms/manage_forms.html', context)


def download_specific_file_view(request, pk, file_type):
    """Download specific file type (PDF, Word, Excel)"""
    form = get_object_or_404(TaxForm, pk=pk, is_active=True)
    
    # Validate file type
    if file_type not in ['pdf', 'word', 'excel']:
        messages.error(request, 'Invalid file type requested.')
        return redirect('forms:form_detail', pk=form.pk)
    
    # Track download
    FormDownload.objects.create(
        form=form,
        download_type=file_type,
        ip_address=get_client_ip(request),
        user_agent=request.META.get('HTTP_USER_AGENT', ''),
        referrer=request.META.get('HTTP_REFERER', '')
    )
    
    # Increment download counter
    form.increment_download_count(file_type)
    
    # Get file URL
    file_url = form.get_file_url(file_type)
    
    if file_url:
        return redirect(file_url)
    else:
        messages.error(request, f'{file_type.upper()} version not available for this form.')
        return redirect('forms:form_detail', pk=form.pk)
    



# Add these views to your existing views.py file

def edit_form_view(request, pk):
    """Form edit page"""
    form = get_object_or_404(TaxForm, pk=pk)
    categories = Category.objects.filter(is_active=True)
    
    if request.method == 'POST':
        try:
            # Update basic information
            form.form_number = request.POST.get('form_number')
            form.title = request.POST.get('title')
            form.assessment_year = request.POST.get('assessment_year')
            form.financial_year = request.POST.get('financial_year')
            form.description = request.POST.get('description')
            form.external_url = request.POST.get('external_url')
            form.meta_title = request.POST.get('meta_title')
            form.meta_description = request.POST.get('meta_description')
            form.is_active = request.POST.get('is_active') == 'on'
            form.is_featured = request.POST.get('is_featured') == 'on'
            form.order = int(request.POST.get('order', 0))
            
            # Update category
            category_id = request.POST.get('category')
            if category_id:
                form.category = Category.objects.get(id=category_id)
            
            # Handle new file uploads
            if 'new_pdf_file' in request.FILES:
                form.pdf_file = request.FILES['new_pdf_file']
            
            if 'new_word_file' in request.FILES:
                form.word_file = request.FILES['new_word_file']
            
            if 'new_excel_file' in request.FILES:
                form.excel_file = request.FILES['new_excel_file']
            
            form.save()
            
            return JsonResponse({
                'success': True,
                'message': 'Form updated successfully'
            })
            
        except Exception as e:
            return JsonResponse({
                'success': False,
                'error': str(e)
            })
    
    # GET request - show edit form
    context = {
        'form': form,
        'categories': categories,
    }
    return render(request, 'forms/edit_form.html', context)

@require_http_methods(["POST"])
def remove_file_view(request):
    """Remove specific file from form"""
    try:
        data = json.loads(request.body)
        form_id = data.get('form_id')
        file_type = data.get('file_type')
        
        form = TaxForm.objects.get(id=form_id)
        
        if file_type == 'pdf' and form.pdf_file:
            form.pdf_file.delete()
            form.pdf_file = None
        elif file_type == 'word' and form.word_file:
            form.word_file.delete()
            form.word_file = None
        elif file_type == 'excel' and form.excel_file:
            form.excel_file.delete()
            form.excel_file = None
        else:
            return JsonResponse({
                'success': False,
                'error': f'File type {file_type} not found or invalid'
            })
        
        form.save()
        
        return JsonResponse({
            'success': True,
            'message': f'{file_type.upper()} file removed successfully'
        })
        
    except TaxForm.DoesNotExist:
        return JsonResponse({
            'success': False,
            'error': 'Form not found'
        })
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': str(e)
        })

@require_http_methods(["POST"])
def duplicate_form_view(request):
    """Duplicate an existing form"""
    try:
        data = json.loads(request.body)
        form_id = data.get('form_id')
        
        original_form = TaxForm.objects.get(id=form_id)
        
        # Create duplicate
        duplicate = TaxForm.objects.create(
            form_number=f"{original_form.form_number}-copy",
            title=f"{original_form.title} (Copy)",
            description=original_form.description,
            category=original_form.category,
            assessment_year=original_form.assessment_year,
            financial_year=original_form.financial_year,
            external_url=original_form.external_url,
            meta_title=original_form.meta_title,
            meta_description=original_form.meta_description,
            is_active=False,  # Set to inactive by default
            is_featured=False,
            order=original_form.order + 1
        )
        
        # Copy files if they exist
        if original_form.pdf_file:
            duplicate.pdf_file = original_form.pdf_file
        if original_form.word_file:
            duplicate.word_file = original_form.word_file
        if original_form.excel_file:
            duplicate.excel_file = original_form.excel_file
            
        duplicate.save()
        
        return JsonResponse({
            'success': True,
            'message': 'Form duplicated successfully',
            'edit_url': reverse('forms:edit_form', kwargs={'pk': duplicate.pk})
        })
        
    except TaxForm.DoesNotExist:
        return JsonResponse({
            'success': False,
            'error': 'Form not found'
        })
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': str(e)
        })

@require_http_methods(["POST"])
def delete_form_view(request):
    """Delete a form"""
    try:
        data = json.loads(request.body)
        form_id = data.get('form_id')
        
        form = TaxForm.objects.get(id=form_id)
        
        # Delete associated files
        if form.pdf_file:
            form.pdf_file.delete()
        if form.word_file:
            form.word_file.delete()
        if form.excel_file:
            form.excel_file.delete()
        
        # Delete the form
        form.delete()
        
        return JsonResponse({
            'success': True,
            'message': 'Form deleted successfully'
        })
        
    except TaxForm.DoesNotExist:
        return JsonResponse({
            'success': False,
            'error': 'Form not found'
        })
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': str(e)
        })

@require_http_methods(["POST"])
def toggle_form_status_view(request):
    """Toggle form active/inactive status"""
    try:
        data = json.loads(request.body)
        form_id = data.get('form_id')
        is_active = data.get('is_active')
        
        form = TaxForm.objects.get(id=form_id)
        form.is_active = is_active
        form.save()
        
        return JsonResponse({
            'success': True,
            'message': f'Form {"activated" if is_active else "deactivated"} successfully'
        })
        
    except TaxForm.DoesNotExist:
        return JsonResponse({
            'success': False,
            'error': 'Form not found'
        })
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': str(e)
        })
    



from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from django.views.decorators.csrf import csrf_exempt
from django.shortcuts import get_object_or_404
from django.urls import reverse
from .models import Category, TaxForm

# Secret key
API_SECRET_KEY = "Rahul@121005"

def validate_api_key(request):
    print("🔐 Checking Secret Key...")
    print("ALL HEADERS:", request.META)

    secret_key = request.META.get('HTTP_SECRET_KEY')
    print("🔑 Found:", secret_key)

    return secret_key == API_SECRET_KEY


def get_file_absolute_url(request, file_field):
    """Helper function to get absolute URL for file fields"""
    if file_field and hasattr(file_field, 'url'):
        return request.build_absolute_uri(file_field.url)
    return None


@csrf_exempt
@require_http_methods(["GET"])
def api_category_forms_secure(request, category_slug):
    """
    Secure API to get all forms by category with file URLs
    URL: /api/category/<slug>/forms/
    Headers: Secret-Key: Rahul@121005
    """

    if not validate_api_key(request):
        return JsonResponse({
            'success': False,
            'error': 'Unauthorized Access',
            'message': 'Valid Secret-Key header is required for API access',
            'code': 'INVALID_SECRET_KEY'
        }, status=401)

    try:
        category = get_object_or_404(Category, slug=category_slug, is_active=True)
        forms = TaxForm.objects.filter(category=category, is_active=True).order_by('-created_at')

        forms_data = []
        for form in forms:
            # Get file URLs using the helper function
            pdf_url = get_file_absolute_url(request, form.pdf_file)
            word_url = get_file_absolute_url(request, form.word_file)
            excel_url = get_file_absolute_url(request, form.excel_file)
            
            # Get file sizes in human readable format
            pdf_size = form.get_file_size_display('pdf') if form.pdf_file else None
            word_size = form.get_file_size_display('word') if form.word_file else None
            excel_size = form.get_file_size_display('excel') if form.excel_file else None
            
            form_data = {
                'id': form.id,
                'form_number': form.form_number,
                'title': form.title,
                'description': form.description,
                'assessment_year': form.assessment_year,
                'financial_year': form.financial_year,
                'download_count': form.download_count,
                'is_featured': form.is_featured,
                'created_at': form.created_at.isoformat(),
                'updated_at': form.updated_at.isoformat(),
                
                # File availability flags
                'has_pdf': bool(form.pdf_file),
                'has_word': bool(form.word_file),
                'has_excel': bool(form.excel_file),
                'has_external_url': bool(form.external_url),
                
                # Direct file URLs
                'pdf_url': pdf_url,
                'word_url': word_url,
                'excel_url': excel_url,
                'external_url': form.external_url,
                
                # File sizes
                'pdf_size': pdf_size,
                'word_size': word_size,
                'excel_size': excel_size,
                'total_size': form.get_file_size_display('total'),
                
                # Available formats
                'available_formats': form.get_available_formats(),
                'file_type': form.file_type,
                'has_multiple_formats': form.has_multiple_formats(),
                'primary_file_url': get_file_absolute_url(request, getattr(form, f'{form.file_type}_file', None)) if form.file_type != 'external' else form.external_url,
                
                # Download statistics
                'download_stats': form.get_download_stats(),
                'most_popular_format': form.get_most_popular_format(),
                
                # Django URLs (for web interface)
                'detail_url': request.build_absolute_uri(
                    reverse('forms:form_detail', kwargs={'pk': form.pk})
                ),
                'download_url': request.build_absolute_uri(
                    reverse('forms:download_form', kwargs={'pk': form.pk})
                ),
                'pdf_download_url': request.build_absolute_uri(
                    reverse('forms:download_specific_file', kwargs={'pk': form.pk, 'file_type': 'pdf'})
                ) if form.pdf_file else None,
                'word_download_url': request.build_absolute_uri(
                    reverse('forms:download_specific_file', kwargs={'pk': form.pk, 'file_type': 'word'})
                ) if form.word_file else None,
                'excel_download_url': request.build_absolute_uri(
                    reverse('forms:download_specific_file', kwargs={'pk': form.pk, 'file_type': 'excel'})
                ) if form.excel_file else None,
                
                # SEO
                'meta_title': form.meta_title,
                'meta_description': form.meta_description,
                
                # Category info
                'category': {
                    'id': category.id,
                    'name': category.name,
                    'slug': category.slug
                }
            }
            
            forms_data.append(form_data)

        return JsonResponse({
            'success': True,
            'category': {
                'id': category.id,
                'name': category.name,
                'slug': category.slug,
                'description': category.description,
                'total_forms': len(forms_data)
            },
            'forms': forms_data,
            'total_count': len(forms_data),
            'meta': {
                'total_pdf_forms': sum(1 for f in forms_data if f['has_pdf']),
                'total_word_forms': sum(1 for f in forms_data if f['has_word']),
                'total_excel_forms': sum(1 for f in forms_data if f['has_excel']),
                'total_external_forms': sum(1 for f in forms_data if f['has_external_url']),
            }
        }, status=200)

    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': 'Server Error',
            'message': str(e),
            'code': 'SERVER_ERROR'
        }, status=500)


@csrf_exempt
@require_http_methods(["GET"])
def api_categories_secure(request):
    """
    Secure API to get all active categories
    URL: /api/categories/
    Headers: Secret-Key: Rahul@121005
    """

    if not validate_api_key(request):
        return JsonResponse({
            'success': False,
            'error': 'Unauthorized Access',
            'message': 'Valid Secret-Key header is required for API access',
            'code': 'INVALID_SECRET_KEY'
        }, status=401)

    try:
        categories = Category.objects.filter(is_active=True).order_by('order', 'name')
        data = []
        for cat in categories:
            # Get forms statistics for this category
            forms_qs = cat.forms.filter(is_active=True)
            
            category_data = {
                'id': cat.id,
                'name': cat.name,
                'slug': cat.slug,
                'description': cat.description,
                'order': cat.order,
                'forms_count': forms_qs.count(),
                'api_url': request.build_absolute_uri(
                    reverse('forms:api_category_forms_secure', kwargs={'category_slug': cat.slug})
                ),
                'stats': {
                    'total_forms': forms_qs.count(),
                    'pdf_forms': forms_qs.exclude(pdf_file__isnull=True).exclude(pdf_file__exact='').count(),
                    'word_forms': forms_qs.exclude(word_file__isnull=True).exclude(word_file__exact='').count(),
                    'excel_forms': forms_qs.exclude(excel_file__isnull=True).exclude(excel_file__exact='').count(),
                    'external_forms': forms_qs.exclude(external_url__isnull=True).exclude(external_url__exact='').count(),
                    'featured_forms': forms_qs.filter(is_featured=True).count(),
                    'total_downloads': sum(form.download_count for form in forms_qs),
                }
            }
            
            data.append(category_data)

        return JsonResponse({
            'success': True,
            'categories': data,
            'total_count': len(data),
            'meta': {
                'total_categories': len(data),
                'total_forms': sum(cat['forms_count'] for cat in data),
                'total_downloads': sum(cat['stats']['total_downloads'] for cat in data),
            }
        }, status=200)

    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': 'Server Error',
            'message': str(e),
            'code': 'SERVER_ERROR'
        }, status=500)


@csrf_exempt
@require_http_methods(["GET"])
def api_form_detail_secure(request, form_id):
    """
    Secure API to get detailed information about a specific form
    URL: /api/form/<id>/
    Headers: Secret-Key: Rahul@121005
    """

    if not validate_api_key(request):
        return JsonResponse({
            'success': False,
            'error': 'Unauthorized Access',
            'message': 'Valid Secret-Key header is required for API access',
            'code': 'INVALID_SECRET_KEY'
        }, status=401)

    try:
        form = get_object_or_404(TaxForm, id=form_id, is_active=True)
        
        # Get file URLs
        pdf_url = get_file_absolute_url(request, form.pdf_file)
        word_url = get_file_absolute_url(request, form.word_file)
        excel_url = get_file_absolute_url(request, form.excel_file)
        
        # Get related links
        related_links = []
        for link in form.related_links.filter(is_active=True):
            related_links.append({
                'title': link.title,
                'url': link.url,
                'type': link.link_type,
                'description': link.description
            })
        
        # Get additional files
        additional_files = []
        for file_obj in form.additional_files.filter(is_active=True):
            additional_files.append({
                'file_name': file_obj.file_name,
                'file_url': get_file_absolute_url(request, file_obj.file),
                'file_type': file_obj.file_type,
                'file_size': file_obj.get_file_size_display(),
                'description': file_obj.description,
                'download_count': file_obj.download_count
            })
        
        form_data = {
            'id': form.id,
            'form_number': form.form_number,
            'title': form.title,
            'description': form.description,
            'assessment_year': form.assessment_year,
            'financial_year': form.financial_year,
            'download_count': form.download_count,
            'is_featured': form.is_featured,
            'created_at': form.created_at.isoformat(),
            'updated_at': form.updated_at.isoformat(),
            
            # File information
            'has_pdf': bool(form.pdf_file),
            'has_word': bool(form.word_file),
            'has_excel': bool(form.excel_file),
            'has_external_url': bool(form.external_url),
            
            # Direct file URLs
            'pdf_url': pdf_url,
            'word_url': word_url,
            'excel_url': excel_url,
            'external_url': form.external_url,
            
            # File sizes
            'pdf_size': form.get_file_size_display('pdf') if form.pdf_file else None,
            'word_size': form.get_file_size_display('word') if form.word_file else None,
            'excel_size': form.get_file_size_display('excel') if form.excel_file else None,
            'total_size': form.get_file_size_display('total'),
            
            # File metadata
            'available_formats': form.get_available_formats(),
            'file_type': form.file_type,
            'has_multiple_formats': form.has_multiple_formats(),
            'primary_file_url': get_file_absolute_url(request, getattr(form, f'{form.file_type}_file', None)) if form.file_type != 'external' else form.external_url,
            
            # Download statistics
            'download_stats': form.get_download_stats(),
            'most_popular_format': form.get_most_popular_format(),
            
            # Category information
            'category': {
                'id': form.category.id,
                'name': form.category.name,
                'slug': form.category.slug,
                'description': form.category.description
            },
            
            # Related content
            'related_links': related_links,
            'additional_files': additional_files,
            
            # SEO
            'meta_title': form.meta_title,
            'meta_description': form.meta_description,
            
            # URLs for web interface
            'detail_url': request.build_absolute_uri(form.get_absolute_url()),
            'download_url': request.build_absolute_uri(
                reverse('forms:download_form', kwargs={'pk': form.pk})
            ),
        }

        return JsonResponse({
            'success': True,
            'form': form_data
        }, status=200)

    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': 'Server Error',
            'message': str(e),
            'code': 'SERVER_ERROR'
        }, status=500)


@csrf_exempt
@require_http_methods(["GET"])
def api_search_forms_secure(request):
    """
    Secure API to search forms
    URL: /api/search/?q=<query>&category=<slug>&format=<format>
    Headers: Secret-Key: Rahul@121005
    """

    if not validate_api_key(request):
        return JsonResponse({
            'success': False,
            'error': 'Unauthorized Access',
            'message': 'Valid Secret-Key header is required for API access',
            'code': 'INVALID_SECRET_KEY'
        }, status=401)

    try:
        query = request.GET.get('q', '').strip()
        category_slug = request.GET.get('category', '').strip()
        file_format = request.GET.get('format', '').strip()
        
        # Start with all active forms
        forms = TaxForm.objects.filter(is_active=True)
        
        # Apply search filters
        if query:
            forms = forms.filter(
                models.Q(title__icontains=query) |
                models.Q(form_number__icontains=query) |
                models.Q(description__icontains=query)
            )
        
        if category_slug:
            forms = forms.filter(category__slug=category_slug)
        
        if file_format:
            if file_format == 'pdf':
                forms = forms.exclude(pdf_file__isnull=True).exclude(pdf_file__exact='')
            elif file_format == 'word':
                forms = forms.exclude(word_file__isnull=True).exclude(word_file__exact='')
            elif file_format == 'excel':
                forms = forms.exclude(excel_file__isnull=True).exclude(excel_file__exact='')
            elif file_format == 'external':
                forms = forms.exclude(external_url__isnull=True).exclude(external_url__exact='')
        
        forms = forms.order_by('-is_featured', '-download_count', '-created_at')
        
        # Build response data
        forms_data = []
        for form in forms:
            pdf_url = get_file_absolute_url(request, form.pdf_file)
            word_url = get_file_absolute_url(request, form.word_file)
            excel_url = get_file_absolute_url(request, form.excel_file)
            
            forms_data.append({
                'id': form.id,
                'form_number': form.form_number,
                'title': form.title,
                'description': form.description,
                'assessment_year': form.assessment_year,
                'financial_year': form.financial_year,
                'download_count': form.download_count,
                'is_featured': form.is_featured,
                'created_at': form.created_at.isoformat(),
                'updated_at': form.updated_at.isoformat(),
                
                # File availability
                'has_pdf': bool(form.pdf_file),
                'has_word': bool(form.word_file),
                'has_excel': bool(form.excel_file),
                'has_external_url': bool(form.external_url),
                
                # Direct file URLs
                'pdf_url': pdf_url,
                'word_url': word_url,
                'excel_url': excel_url,
                'external_url': form.external_url,
                
                # File metadata
                'available_formats': form.get_available_formats(),
                'file_type': form.file_type,
                'primary_file_url': get_file_absolute_url(request, getattr(form, f'{form.file_type}_file', None)) if form.file_type != 'external' else form.external_url,
                
                # Category
                'category': {
                    'id': form.category.id,
                    'name': form.category.name,
                    'slug': form.category.slug
                },
                
                # URLs
                'detail_url': request.build_absolute_uri(form.get_absolute_url()),
            })

        return JsonResponse({
            'success': True,
            'forms': forms_data,
            'total_count': len(forms_data),
            'search_params': {
                'query': query,
                'category': category_slug,
                'format': file_format
            }
        }, status=200)

    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': 'Server Error',
            'message': str(e),
            'code': 'SERVER_ERROR'
        }, status=500)