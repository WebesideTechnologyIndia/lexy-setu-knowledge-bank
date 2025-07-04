# urls.py
from django.urls import path
from . import views

urlpatterns = [
    # =============================================================================
    # WEB ROUTES (Template Rendering) - PURANE SAME RAHENGE
    # =============================================================================
    path('', views.notification_list, name='notification_list'),
    path('add/', views.add_notification, name='add_notification'),
    path('<int:pk>/', views.notification_detail, name='notification_detail'),
    path('<int:pk>/edit/', views.edit_notification, name='edit_notification'),
    path('<int:pk>/delete/', views.delete_notification, name='delete_notification'),
    path('category/<str:category_name>/', views.category_notifications, name='category_notifications'),
    
    # =============================================================================
    # API ROUTES (JSON Response) - YE NAYE BANAYE HAIN
    # =============================================================================
    path('api/notifications/', views.api_notification_list, name='api_notification_list'),
    path('api/notifications/<int:pk>/', views.api_notification_detail, name='api_notification_detail'),
    path('api/notifications/add/', views.api_add_notification, name='api_add_notification'),
    path('api/notifications/<int:pk>/edit/', views.api_edit_notification, name='api_edit_notification'),
    path('api/notifications/<int:pk>/delete/', views.api_delete_notification, name='api_delete_notification'),
    path('api/notifications/category/<str:category_name>/', views.api_category_notifications, name='api_category_notifications'),
]