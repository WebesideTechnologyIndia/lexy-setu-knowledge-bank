# urls.py
from django.urls import path
from . import views

urlpatterns = [
    # Utility URLs
    path('', views.utility_list, name='utility_list'),
    path('utility/<int:pk>/', views.utility_detail, name='utility_detail'),
    path('utility/add/', views.utility_add, name='utility_add'),
    path('utility/<int:pk>/edit/', views.utility_edit, name='utility_edit'),
    path('utility/<int:pk>/delete/', views.utility_delete, name='utility_delete'),
    
    # Category URLs
    path('categories/', views.category_list, name='category_list'),
    path('categories/add/', views.category_add, name='category_add'),
    path('category/<int:pk>/', views.category_utilities, name='category_utilities'),
]