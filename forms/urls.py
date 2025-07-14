# urls.py
from django.urls import path
from . import views

app_name = 'forms'

urlpatterns = [
    # Main pages
    path('', views.home_view, name='home'),
    path('search/', views.search_forms_view, name='search'),
    path('popular/', views.popular_forms_view, name='popular'),
    path('recent/', views.recent_forms_view, name='recent'),
    path('upload/', views.upload_form_view, name='upload_form'),  # Upload form page
    
    # Management pages
    path('manage/categories/', views.manage_categories_view, name='manage_categories'),
    path('manage/forms/', views.manage_forms_view, name='manage_forms'),
    
    # Category management AJAX endpoints
    path('ajax/add-category/', views.add_category_view, name='add_category'),
    path('ajax/get-category/<int:category_id>/', views.get_category_view, name='get_category'),
    path('ajax/update-category/', views.update_category_view, name='update_category'),
    path('ajax/delete-category/', views.delete_category_view, name='delete_category'),
    path('ajax/reorder-categories/', views.reorder_categories_view, name='reorder_categories'),
    
    # Category pages
    path('category/<slug:slug>/', views.category_forms_view, name='category_forms'),
    
    # Form pages
    path('form/<int:pk>/', views.form_detail_view, name='form_detail'),
    path('form/<int:pk>/edit/', views.edit_form_view, name='edit_form'),
    path('download/<int:pk>/', views.download_form_view, name='download_form'),
    path('download/<int:pk>/<str:file_type>/', views.download_specific_file_view, name='download_specific'),
    
    # Form management AJAX endpoints
    path('ajax/remove-file/', views.remove_file_view, name='remove_file'),
    path('ajax/duplicate-form/', views.duplicate_form_view, name='duplicate_form'),
    path('ajax/delete-form/', views.delete_form_view, name='delete_form'),
    path('ajax/toggle-status/', views.toggle_form_status_view, name='toggle_status'),
    
    # Year-based pages
    path('year/<str:year>/', views.forms_by_year_view, name='forms_by_year'),
    
    # AJAX endpoints
    path('ajax/search/', views.ajax_search_forms, name='ajax_search'),
    
    # API endpoints
    path('api/categories/', views.api_categories, name='api_categories'),
    path('api/category/<slug:category_slug>/', views.api_forms_by_category, name='api_forms_by_category'),
    
    # api drf
    # api drf
    # api drf
    # api drf
    # api drf
    # api drf


    # path('form/<int:pk>/', views.form_detail, name='form_detail'),
    # path('category/<slug:slug>/', views.category_forms, name='category_forms'),
    # path('download/<int:pk>/', views.download_form, name='download_form'),
    # path('download/<int:pk>/<str:file_type>/', views.download_specific_file, name='download_specific_file'),
    
    # API endpoints (secured with secret key)
    path('api/get-categories/', views.api_categories_secure, name='api_categories_secure'),
    path('api/category/<slug:category_slug>/forms/', views.api_category_forms_secure, name='api_category_forms_secure'),
    path('api/form/<int:form_id>/', views.api_form_detail_secure, name='api_form_detail_secure'),
    path('api/search/', views.api_search_forms_secure, name='api_search_forms_secure'),
    ]