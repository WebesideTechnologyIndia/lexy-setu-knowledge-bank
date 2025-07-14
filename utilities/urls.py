from django.urls import path
from . import views

urlpatterns = [
    # Utility HTML Views
    path('', views.utility_list, name='utility_list'),
    path('utility/<int:pk>/', views.utility_detail, name='utility_detail'),
    path('utility/add/', views.utility_add, name='utility_add'),
    path('utility/<int:pk>/edit/', views.utility_edit, name='utility_edit'),
    path('utility/<int:pk>/delete/', views.utility_delete, name='utility_delete'),

    # Category HTML Views
    path('categories/', views.category_list, name='category_list'),
    path('categories/add/', views.category_add, name='category_add'),
    path('category/<int:pk>/', views.category_utilities, name='category_utilities'),

    # API Endpoints
    path('api/utilities/', views.api_utility_list, name='api_utility_list'),
    path('api/utilities/<int:pk>/', views.api_utility_detail, name='api_utility_detail'),
    path('api/utilities/featured/', views.api_featured_utilities, name='api_featured_utilities'),
    path('api/utilities/search/', views.api_search_utilities, name='api_search_utilities'),
    path('api/utilities/stats/', views.api_utility_stats, name='api_utility_stats'),

    path('api/categories/', views.api_category_list, name='api_category_list'),
    path('api/categories/<int:pk>/utilities/', views.api_category_utilities, name='api_category_utilities'),

    # SPA View
    path('utilities-spa/', views.utilities_spa_view, name='utilities_spa_view'),
]
