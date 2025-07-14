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





# Utilities GET APIs Only - For fetching data to HTML
from django.shortcuts import get_object_or_404
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from django.core.paginator import Paginator
from django.db.models import Q, Count

# Same secret key for API authentication
SECRET_KEY = "Rahul@121005"

def check_auth(request):
    """Check if request has valid secret key in headers"""
    auth_header = request.headers.get('X-Secret-Key')
    return auth_header == SECRET_KEY

def api_response(success=True, data=None, message="", status=200):
    """Standard API response format"""
    response_data = {
        'success': success,
        'message': message,
        'data': data
    }
    return JsonResponse(response_data, status=status)

def unauthorized_response():
    """Return unauthorized response"""
    return api_response(
        success=False, 
        message="Unauthorized: Invalid or missing secret key", 
        status=401
    )

# ============= UTILITIES GET APIs =============

from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from django.core.paginator import Paginator
from django.db.models import Q
from django.http import JsonResponse

from .models import Utility, Category
from utilities.utils import check_auth, unauthorized_response, api_response


@csrf_exempt
@require_http_methods(["GET"])
def api_utility_list(request):
    """API: Get all utilities with filters"""
    if not check_auth(request):
        return unauthorized_response()

    try:
        category_slug = request.GET.get('category')
        search_query = request.GET.get('search')
        priority_filter = request.GET.get('priority')
        is_featured = request.GET.get('featured')
        page_number = request.GET.get('page', 1)

        # Base queryset
        utilities = Utility.objects.filter(is_published=True).select_related('category')

        # Category filter by slug
        if category_slug:
            try:
                category_obj = Category.objects.get(slug=category_slug, is_active=True)
                utilities = utilities.filter(category=category_obj)
            except Category.DoesNotExist:
                return api_response(
                    success=False, 
                    message=f"Category '{category_slug}' not found",
                    status=404
                )

        # Search filter
        if search_query:
            utilities = utilities.filter(
                Q(title__icontains=search_query) |
                Q(content__icontains=search_query) |
                Q(tags__icontains=search_query)
            )

        # Priority filter
        if priority_filter:
            utilities = utilities.filter(priority=priority_filter)

        # Featured filter
        if is_featured:
            is_featured_bool = is_featured.lower() == 'true'
            utilities = utilities.filter(is_featured=is_featured_bool)

        # Ordering
        utilities = utilities.order_by('-created_at')

        # Pagination
        paginator = Paginator(utilities, 10)
        page_obj = paginator.get_page(page_number)

        # Serialize utilities
        utilities_data = []
        for utility in page_obj:
            utilities_data.append({
                'id': utility.pk,
                'title': utility.title,
                'content': utility.content[:300] + '...' if len(utility.content) > 300 else utility.content,
                'category': {
                    'id': utility.category.pk if utility.category else None,
                    'name': utility.category.display_name if utility.category else None,
                    'slug': utility.category.slug if utility.category else None,
                } if utility.category else None,
                'priority': utility.priority,
                'priority_display': utility.get_priority_display(),
                'is_featured': utility.is_featured,
                'tags': utility.tags,
                'created_at': utility.created_at.isoformat() if hasattr(utility, 'created_at') else None,
                'updated_at': utility.updated_at.isoformat() if hasattr(utility, 'updated_at') else None,
            })

        # Categories list
        categories = list(Category.objects.filter(is_active=True).values('id', 'slug', 'display_name'))

        # Priority choices
        priority_choices = [{'value': val, 'display': label} for val, label in Utility.PRIORITY_CHOICES]

        # Final response
        data = {
            'utilities': utilities_data,
            'pagination': {
                'current_page': page_obj.number,
                'total_pages': paginator.num_pages,
                'total_items': paginator.count,
                'has_next': page_obj.has_next(),
                'has_previous': page_obj.has_previous(),
            },
            'categories': categories,
            'priority_choices': priority_choices,
        }

        return api_response(data=data, message="Utilities retrieved successfully")

    except Exception as e:
        return api_response(success=False, message=str(e), status=500)





@csrf_exempt
@require_http_methods(["GET"])
def api_utility_detail(request, pk):
    """API: Get utility detail"""
    if not check_auth(request):
        return unauthorized_response()
    
    try:
        utility = get_object_or_404(Utility, pk=pk, is_published=True)
        
        # Get related utilities
        related_utilities = Utility.objects.filter(
            category=utility.category, 
            is_published=True
        ).exclude(pk=pk)[:5]
        
        related_data = []
        for related in related_utilities:
            related_data.append({
                'id': related.pk,
                'title': related.title,
                'priority': related.priority,
                'priority_display': related.get_priority_display(),
                'is_featured': related.is_featured,
            })
        
        # Calculate category stats
        if utility.category:
            category_utilities = utility.category.utilities.filter(is_published=True)
            category_stats = {
                'total_utilities': category_utilities.count(),
                'featured_count': category_utilities.filter(is_featured=True).count(),
                'urgent_count': category_utilities.filter(priority='urgent').count(),
                'high_count': category_utilities.filter(priority='high').count(),
                'medium_count': category_utilities.filter(priority='medium').count(),
                'low_count': category_utilities.filter(priority='low').count(),
            }
        else:
            category_stats = {}
        
        data = {
            'id': utility.pk,
            'title': utility.title,
            'content': utility.content,
            'category': {
                'id': utility.category.pk if utility.category else None,
                'name': utility.category.display_name if utility.category else None,
            } if utility.category else None,
            'priority': utility.priority,
            'priority_display': utility.get_priority_display(),
            'is_featured': utility.is_featured,
            'tags': utility.tags,
            'created_at': utility.created_at.isoformat() if hasattr(utility, 'created_at') else None,
            'updated_at': utility.updated_at.isoformat() if hasattr(utility, 'updated_at') else None,
            'related_utilities': related_data,
            'category_stats': category_stats,
        }
        
        return api_response(data=data, message="Utility retrieved successfully")
        
    except Exception as e:
        return api_response(success=False, message=str(e), status=404)


# ============= CATEGORY GET APIs =============

@csrf_exempt
@require_http_methods(["GET"])
def api_category_list(request):
    """API: Get all categories"""
    if not check_auth(request):
        return unauthorized_response()
    
    try:
        categories = Category.objects.filter(is_active=True).annotate(
            utility_count=Count('utilities', filter=Q(utilities__is_published=True))
        )
        
        categories_data = []
        for category in categories:
            categories_data.append({
                'id': category.pk,
                'name': category.display_name,
                'description': getattr(category, 'description', ''),
                'utility_count': category.utility_count,
                'is_active': category.is_active,
                'created_at': category.created_at.isoformat() if hasattr(category, 'created_at') else None,
            })
        
        data = {
            'categories': categories_data,
        }
        
        return api_response(data=data, message="Categories retrieved successfully")
        
    except Exception as e:
        return api_response(success=False, message=str(e), status=500)


@csrf_exempt
@require_http_methods(["GET"])
def api_category_utilities(request, pk):
    """API: Get utilities by category"""
    if not check_auth(request):
        return unauthorized_response()
    
    try:
        category = get_object_or_404(Category, pk=pk, is_active=True)
        utilities = Utility.objects.filter(category=category, is_published=True)
        
        # Search within category
        search_query = request.GET.get('search')
        if search_query:
            utilities = utilities.filter(
                Q(title__icontains=search_query) | 
                Q(content__icontains=search_query)
            )
        
        # Priority filter
        priority_filter = request.GET.get('priority')
        if priority_filter:
            utilities = utilities.filter(priority=priority_filter)
        
        # Order by latest first
        utilities = utilities.order_by('-created_at')
        
        # Pagination
        page_number = request.GET.get('page', 1)
        paginator = Paginator(utilities, 10)
        page_obj = paginator.get_page(page_number)
        
        utilities_data = []
        for utility in page_obj:
            utilities_data.append({
                'id': utility.pk,
                'title': utility.title,
                'content': utility.content[:200] + '...' if len(utility.content) > 200 else utility.content,
                'priority': utility.priority,
                'priority_display': utility.get_priority_display(),
                'is_featured': utility.is_featured,
                'tags': utility.tags,
                'created_at': utility.created_at.isoformat() if hasattr(utility, 'created_at') else None,
            })
        
        data = {
            'utilities': utilities_data,
            'category': {
                'id': category.pk,
                'name': category.display_name,
            },
            'pagination': {
                'current_page': page_obj.number,
                'total_pages': paginator.num_pages,
                'total_items': paginator.count,
                'has_next': page_obj.has_next(),
                'has_previous': page_obj.has_previous(),
            },
        }
        
        return api_response(data=data, message="Category utilities retrieved successfully")
        
    except Exception as e:
        return api_response(success=False, message=str(e), status=404)


# ============= FEATURED UTILITIES API =============

@csrf_exempt
@require_http_methods(["GET"])
def api_featured_utilities(request):
    """API: Get featured utilities"""
    if not check_auth(request):
        return unauthorized_response()
    
    try:
        utilities = Utility.objects.filter(is_published=True, is_featured=True).select_related('category')
        
        # Limit to latest 10 featured utilities
        utilities = utilities.order_by('-created_at')[:10]
        
        utilities_data = []
        for utility in utilities:
            utilities_data.append({
                'id': utility.pk,
                'title': utility.title,
                'content': utility.content[:150] + '...' if len(utility.content) > 150 else utility.content,
                'category': {
                    'id': utility.category.pk if utility.category else None,
                    'name': utility.category.display_name if utility.category else None,
                } if utility.category else None,
                'priority': utility.priority,
                'priority_display': utility.get_priority_display(),
                'created_at': utility.created_at.isoformat() if hasattr(utility, 'created_at') else None,
            })
        
        data = {
            'utilities': utilities_data,
        }
        
        return api_response(data=data, message="Featured utilities retrieved successfully")
        
    except Exception as e:
        return api_response(success=False, message=str(e), status=500)


# ============= SEARCH API =============

@csrf_exempt
@require_http_methods(["GET"])
def api_search_utilities(request):
    """API: Search utilities across all categories"""
    if not check_auth(request):
        return unauthorized_response()
    
    try:
        search_query = request.GET.get('query', '').strip()
        
        if not search_query:
            return api_response(
                success=False, 
                message="Search query is required", 
                status=400
            )
        
        utilities = Utility.objects.filter(
            Q(title__icontains=search_query) | 
            Q(content__icontains=search_query) |
            Q(tags__icontains=search_query),
            is_published=True
        ).select_related('category')
        
        # Pagination
        page_number = request.GET.get('page', 1)
        paginator = Paginator(utilities, 10)
        page_obj = paginator.get_page(page_number)
        
        utilities_data = []
        for utility in page_obj:
            utilities_data.append({
                'id': utility.pk,
                'title': utility.title,
                'content': utility.content[:200] + '...' if len(utility.content) > 200 else utility.content,
                'category': {
                    'id': utility.category.pk if utility.category else None,
                    'name': utility.category.display_name if utility.category else None,
                } if utility.category else None,
                'priority': utility.priority,
                'priority_display': utility.get_priority_display(),
                'is_featured': utility.is_featured,
                'tags': utility.tags,
                'created_at': utility.created_at.isoformat() if hasattr(utility, 'created_at') else None,
            })
        
        data = {
            'utilities': utilities_data,
            'search_query': search_query,
            'pagination': {
                'current_page': page_obj.number,
                'total_pages': paginator.num_pages,
                'total_items': paginator.count,
                'has_next': page_obj.has_next(),
                'has_previous': page_obj.has_previous(),
            },
        }
        
        return api_response(data=data, message="Search results retrieved successfully")
        
    except Exception as e:
        return api_response(success=False, message=str(e), status=500)


# ============= STATS API =============

@csrf_exempt
@require_http_methods(["GET"])
def api_utility_stats(request):
    """API: Get utility statistics"""
    if not check_auth(request):
        return unauthorized_response()
    
    try:
        total_utilities = Utility.objects.filter(is_published=True).count()
        featured_utilities = Utility.objects.filter(is_published=True, is_featured=True).count()
        total_categories = Category.objects.filter(is_active=True).count()
        
        # Priority stats
        priority_stats = {}
        for priority_choice in Utility.PRIORITY_CHOICES:
            priority_key = priority_choice[0]
            priority_count = Utility.objects.filter(
                is_published=True, 
                priority=priority_key
            ).count()
            priority_stats[priority_key] = {
                'count': priority_count,
                'display': priority_choice[1]
            }
        
        # Category wise stats
        category_stats = []
        categories = Category.objects.filter(is_active=True).annotate(
            utility_count=Count('utilities', filter=Q(utilities__is_published=True))
        )
        
        for category in categories:
            category_stats.append({
                'id': category.pk,
                'name': category.display_name,
                'utility_count': category.utility_count,
            })
        
        data = {
            'total_utilities': total_utilities,
            'featured_utilities': featured_utilities,
            'total_categories': total_categories,
            'priority_stats': priority_stats,
            'category_stats': category_stats,
        }
        
        return api_response(data=data, message="Statistics retrieved successfully")
        
    except Exception as e:
        return api_response(success=False, message=str(e), status=500)


# ============= SINGLE PAGE APP VIEW =============

def utilities_spa_view(request):
    """Single Page Application view for utilities"""
    return render(request, 'utilities_spa.html')