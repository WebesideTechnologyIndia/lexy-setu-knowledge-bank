# views.py

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.core.paginator import Paginator
from django.db.models import Q
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
import json
from .models import Notification, NotificationCategory
from .forms import NotificationForm

# =============================================================================
# EXISTING WEB VIEWS (Template Rendering) - YE SAME RAHENGE
# =============================================================================

def notification_list(request):
    """Display all notifications with category filter - WEB VERSION"""
    category_filter = request.GET.get('category')
    search_query = request.GET.get('search')
    
    notifications = Notification.objects.filter(is_active=True)
    
    if category_filter:
        notifications = notifications.filter(category__name=category_filter)
    
    if search_query:
        notifications = notifications.filter(
            Q(title__icontains=search_query) | 
            Q(content__icontains=search_query)
        )
    
    # Pagination
    paginator = Paginator(notifications, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    categories = NotificationCategory.objects.all()
    
    context = {
        'notifications': page_obj,
        'categories': categories,
        'selected_category': category_filter,
        'search_query': search_query,
    }
    return render(request, 'notifications/notification_list.html', context)

def notification_detail(request, pk):
    """Display detailed notification - WEB VERSION"""
    notification = get_object_or_404(Notification, pk=pk, is_active=True)
    return render(request, 'notifications/notification_detail.html', {'notification': notification})

def add_notification(request):
    """Add new notification - WEB VERSION"""
    if request.method == 'POST':
        form = NotificationForm(request.POST)
        if form.is_valid():
            notification = form.save()
            messages.success(request, f'Notification "{notification.title}" successfully added!')
            return redirect('notification_list')
        else:
            messages.error(request, 'Please correct the errors below.')
    else:
        form = NotificationForm()
    
    categories = NotificationCategory.objects.prefetch_related('subcategories')
    return render(request, 'notifications/add_notification.html', {  # Yeh line check karo
        'form': form,
        'categories': categories
    })

def edit_notification(request, pk):
    notification = get_object_or_404(Notification, pk=pk)

    if request.method == 'POST':
        form = NotificationForm(request.POST, request.FILES, instance=notification)  # ✅ Added request.FILES
        if form.is_valid():
            notification = form.save()
            messages.success(request, f'Notification "{notification.title}" successfully updated!')
            return redirect('notification_detail', pk=notification.pk)
        else:
            print(form.errors)  # ✅ Debug print
            messages.error(request, 'Please correct the errors below.')
    else:
        form = NotificationForm(instance=notification)

    return render(request, 'notifications/edit_notification.html', {
        'form': form,
        'notification': notification
    })


def delete_notification(request, pk):
    """Delete notification (soft delete) - WEB VERSION"""
    notification = get_object_or_404(Notification, pk=pk)
    
    if request.method == 'POST':
        notification.is_active = False
        notification.save()
        messages.success(request, f'Notification "{notification.title}" successfully deleted!')
        return redirect('notification_list')
    
    return render(request, 'notifications/delete_notification.html', {'notification': notification})

def category_notifications(request, category_name):
    """Display notifications by category - WEB VERSION"""
    category = get_object_or_404(NotificationCategory, name=category_name)
    notifications = Notification.objects.filter(category=category, is_active=True)
    
    # Pagination
    paginator = Paginator(notifications, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'notifications': page_obj,
        'category': category,
    }
    return render(request, 'notifications/category_notifications.html', context)

# =============================================================================
# NEW API VIEWS (JSON Response) - YE NAYE BANAYE HAIN
# =============================================================================

# Secret key for API authentication
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


@csrf_exempt
@require_http_methods(["GET"])
def api_notification_list(request):
    """API: Get all notifications with filters"""
    if not check_auth(request):
        return unauthorized_response()
    
    try:
        category_filter = request.GET.get('category')
        search_query = request.GET.get('search')
        page_number = request.GET.get('page', 1)
        
        notifications = Notification.objects.filter(is_active=True).select_related('category')
        
        if category_filter:
            notifications = notifications.filter(category__name=category_filter)
        
        if search_query:
            notifications = notifications.filter(
                Q(title__icontains=search_query) | 
                Q(content__icontains=search_query) |
                Q(notification_number__icontains=search_query)
            )
        
        # Order by latest first
        notifications = notifications.order_by('-created_at')
        
        # Pagination
        paginator = Paginator(notifications, 10)
        page_obj = paginator.get_page(page_number)
        
        # Serialize notifications
        notifications_data = []
        for notification in page_obj:
            notifications_data.append({
                'id': notification.pk,
                'title': notification.title,
                'content': notification.content[:300] + '...' if len(notification.content) > 300 else notification.content,
                'category': notification.category.name if notification.category else None,
                'notification_number': getattr(notification, 'notification_number', ''),
                'notification_date': getattr(notification, 'notification_date', notification.created_at).strftime('%Y-%m-%d') if hasattr(notification, 'notification_date') or hasattr(notification, 'created_at') else '',
                'created_at': notification.created_at.isoformat() if hasattr(notification, 'created_at') else None,
            })
        
        # Get categories
        categories = list(NotificationCategory.objects.values('id', 'name'))
        
        data = {
            'notifications': notifications_data,
            'pagination': {
                'current_page': page_obj.number,
                'total_pages': paginator.num_pages,
                'total_items': paginator.count,
                'has_next': page_obj.has_next(),
                'has_previous': page_obj.has_previous(),
            },
            'categories': categories,
        }
        
        return api_response(data=data, message="Notifications retrieved successfully")
        
    except Exception as e:
        return api_response(success=False, message=str(e), status=500)


@csrf_exempt
@require_http_methods(["GET"])
def api_notification_detail(request, pk):
    """API: Get notification detail"""
    if not check_auth(request):
        return unauthorized_response()
    
    try:
        notification = get_object_or_404(Notification, pk=pk, is_active=True)
        
        data = {
            'id': notification.pk,
            'title': notification.title,
            'content': notification.content,
            'category': {
                'id': notification.category.pk if notification.category else None,
                'name': notification.category.name if notification.category else 'No Category',
            },
            'notification_number': getattr(notification, 'notification_number', ''),
            'notification_date': getattr(notification, 'notification_date', notification.created_at).strftime('%Y-%m-%d') if hasattr(notification, 'notification_date') or hasattr(notification, 'created_at') else '',
            'created_at': notification.created_at.isoformat() if hasattr(notification, 'created_at') else None,
        }
        
        return api_response(data=data, message="Notification retrieved successfully")
        
    except Exception as e:
        return api_response(success=False, message=str(e), status=404)



@csrf_exempt
@require_http_methods(["POST"])
def api_add_notification(request):
    """API: Add new notification"""
    if not check_auth(request):
        return unauthorized_response()
    
    try:
        json_data = json.loads(request.body)
        form = NotificationForm(json_data)
        
        if form.is_valid():
            notification = form.save()
            
            data = {
                'id': notification.pk,
                'title': notification.title,
                'content': notification.content,
                'category': notification.category.name if notification.category else None,
            }
            
            return api_response(
                data=data, 
                message=f'Notification "{notification.title}" successfully added!',
                status=201
            )
        else:
            return api_response(
                success=False, 
                message="Validation errors", 
                data={'errors': form.errors},
                status=400
            )
            
    except json.JSONDecodeError:
        return api_response(success=False, message="Invalid JSON data", status=400)
    except Exception as e:
        return api_response(success=False, message=str(e), status=500)

@csrf_exempt
@require_http_methods(["PUT", "PATCH"])
def api_edit_notification(request, pk):
    """API: Edit existing notification"""
    if not check_auth(request):
        return unauthorized_response()
    
    try:
        notification = get_object_or_404(Notification, pk=pk)
        json_data = json.loads(request.body)
        form = NotificationForm(json_data, instance=notification)
        
        if form.is_valid():
            notification = form.save()
            
            data = {
                'id': notification.pk,
                'title': notification.title,
                'content': notification.content,
                'category': notification.category.name if notification.category else None,
            }
            
            return api_response(
                data=data, 
                message=f'Notification "{notification.title}" successfully updated!'
            )
        else:
            return api_response(
                success=False, 
                message="Validation errors", 
                data={'errors': form.errors},
                status=400
            )
            
    except json.JSONDecodeError:
        return api_response(success=False, message="Invalid JSON data", status=400)
    except Exception as e:
        return api_response(success=False, message=str(e), status=500)

@csrf_exempt
@require_http_methods(["DELETE"])
def api_delete_notification(request, pk):
    """API: Delete notification (soft delete)"""
    if not check_auth(request):
        return unauthorized_response()
    
    try:
        notification = get_object_or_404(Notification, pk=pk)
        notification.is_active = False
        notification.save()
        
        return api_response(message=f'Notification "{notification.title}" successfully deleted!')
        
    except Exception as e:
        return api_response(success=False, message=str(e), status=404)

@csrf_exempt
@require_http_methods(["GET"])
def api_category_notifications(request, category_name):
    """API: Get notifications by category"""
    if not check_auth(request):
        return unauthorized_response()
    
    try:
        category = get_object_or_404(NotificationCategory, name=category_name)
        notifications = Notification.objects.filter(category=category, is_active=True)
        
        page_number = request.GET.get('page', 1)
        paginator = Paginator(notifications, 10)
        page_obj = paginator.get_page(page_number)
        
        notifications_data = []
        for notification in page_obj:
            notifications_data.append({
                'id': notification.pk,
                'title': notification.title,
                'content': notification.content,
                'category': notification.category.name,
                'created_at': notification.created_at.isoformat() if hasattr(notification, 'created_at') else None,
            })
        
        data = {
            'notifications': notifications_data,
            'category': {
                'id': category.pk,
                'name': category.name,
            },
            'pagination': {
                'current_page': page_obj.number,
                'total_pages': paginator.num_pages,
                'total_items': paginator.count,
            },
        }
        
        return api_response(data=data, message="Category notifications retrieved successfully")
        
    except Exception as e:
        return api_response(success=False, message=str(e), status=404)
    

def spa_view(request):
    """Single Page Application view"""
    return render(request, 'notifications_spa.html')