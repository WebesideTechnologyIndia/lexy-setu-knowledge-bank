# views.py
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from django.core.paginator import Paginator
from django.db.models import Q, Count
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from .models import Utility, Category
from .forms import UtilityForm, CategoryForm

# Utility Views
def utility_list(request):
    utilities = Utility.objects.select_related('category').filter(is_published=True)
    categories = Category.objects.filter(is_active=True, parent=None).prefetch_related('subcategories')
    
    # Filter by category
    category_id = request.GET.get('category')
    if category_id:
        utilities = utilities.filter(category_id=category_id)
    
    # Search functionality
    search_query = request.GET.get('search')
    if search_query:
        utilities = utilities.filter(
            Q(title__icontains=search_query) | 
            Q(content__icontains=search_query) |
            Q(tags__icontains=search_query)
        )
    
    # Filter by priority
    priority = request.GET.get('priority')
    if priority:
        utilities = utilities.filter(priority=priority)
    
    # Pagination
    paginator = Paginator(utilities, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'utilities': page_obj,
        'categories': categories,
        'selected_category': category_id,
        'search_query': search_query,
        'selected_priority': priority,
        'priority_choices': Utility.PRIORITY_CHOICES,
    }
    return render(request, 'utilities/utility_list.html', context)

def utility_detail(request, pk):
    # Add debug prints
    print(f"=== DEBUG: utility_detail called with pk={pk} ===")
    
    try:
        utility = get_object_or_404(Utility, pk=pk, is_published=True)
        print(f"Found utility: {utility.title}")
        print(f"Utility ID: {utility.pk}")
        print(f"Category: {utility.category}")
        print(f"Is Published: {utility.is_published}")
    except Exception as e:
        print(f"Error finding utility: {e}")
        raise
    
    related_utilities = Utility.objects.filter(
        category=utility.category, 
        is_published=True
    ).exclude(pk=pk)[:5]
    
    print(f"Related utilities count: {related_utilities.count()}")
    
    # Calculate category stats
    category_utilities = utility.category.utilities.filter(is_published=True)
    category_stats = {
        'total_utilities': category_utilities.count(),
        'featured_count': category_utilities.filter(is_featured=True).count(),
        'urgent_count': category_utilities.filter(priority='urgent').count(),
        'high_count': category_utilities.filter(priority='high').count(),
        'medium_count': category_utilities.filter(priority='medium').count(),
        'low_count': category_utilities.filter(priority='low').count(),
    }
    
    print(f"Category stats: {category_stats}")
    
    context = {
        'utility': utility,
        'related_utilities': related_utilities,
        'category_stats': category_stats,
    }
    
    print(f"Context keys: {context.keys()}")
    print("=== DEBUG END ===")
    
    return render(request, 'utilities/utility_detail.html', context)

def utility_add(request):
    if request.method == 'POST':
        form = UtilityForm(request.POST)
        if form.is_valid():
            utility = form.save()
            messages.success(request, f'Utility "{utility.title}" has been created successfully!')
            return redirect('utility_detail', pk=utility.pk)
        else:
            messages.error(request, 'Please correct the errors below.')
    else:
        form = UtilityForm()
    
    categories = Category.objects.filter(is_active=True)
    context = {
        'form': form,
        'categories': categories,
    }
    return render(request, 'utilities/utility_add.html', context)

def utility_edit(request, pk):
    utility = get_object_or_404(Utility, pk=pk)
    
    if request.method == 'POST':
        form = UtilityForm(request.POST, instance=utility)
        if form.is_valid():
            utility = form.save()
            messages.success(request, f'Utility "{utility.title}" has been updated successfully!')
            return redirect('utility_detail', pk=utility.pk)
        else:
            messages.error(request, 'Please correct the errors below.')
    else:
        form = UtilityForm(instance=utility)
    
    categories = Category.objects.filter(is_active=True)
    context = {
        'form': form,
        'utility': utility,
        'categories': categories,
    }
    return render(request, 'utilities/utility_edit.html', context)

@require_http_methods(["DELETE"])
def utility_delete(request, pk):
    utility = get_object_or_404(Utility, pk=pk)
    utility.delete()
    return JsonResponse({'success': True})

# Category Views
def category_list(request):
    categories = Category.objects.annotate(
        utility_count=Count('utilities')
    ).filter(is_active=True)
    
    context = {
        'categories': categories,
    }
    return render(request, 'utilities/category_list.html', context)

def category_add(request):
    if request.method == 'POST':
        form = CategoryForm(request.POST)
        if form.is_valid():
            category = form.save()
            messages.success(request, f'Category "{category.display_name}" has been created successfully!')
            return redirect('category_list')
        else:
            messages.error(request, 'Please correct the errors below.')
    else:
        form = CategoryForm()
    
    context = {
        'form': form,
    }
    return render(request, 'utilities/category_add.html', context)

def category_utilities(request, pk):
    category = get_object_or_404(Category, pk=pk, is_active=True)
    utilities = Utility.objects.filter(category=category, is_published=True)
    
    # Search within category
    search_query = request.GET.get('search')
    if search_query:
        utilities = utilities.filter(
            Q(title__icontains=search_query) | 
            Q(content__icontains=search_query)
        )
    
    # Pagination
    paginator = Paginator(utilities, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'category': category,
        'utilities': page_obj,
        'search_query': search_query,
    }
    return render(request, 'utilities/category_utilities.html', context)