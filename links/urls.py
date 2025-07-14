# urls.py (in your links app)

from django.urls import path
from . import views

app_name = "links"

urlpatterns = [
    # Main pages
    path("", views.HomeView.as_view(), name="home"),
    path(
        "category/<slug:slug>/",
        views.CategoryDetailView.as_view(),
        name="category_detail",
    ),
    path(
        "category/<slug:category_slug>/<slug:slug>/",
        views.SubCategoryDetailView.as_view(),
        name="subcategory_detail",
    ),
    # Link redirect (for tracking clicks)
    path("link/<int:link_id>/", views.link_redirect, name="link_redirect"),
    # Search
    path("search/", views.search_links, name="search"),
    # Add forms (HTML forms)
    path("add-category/", views.add_category, name="add_category"),
    path("add-subcategory/", views.add_subcategory, name="add_subcategory"),
    path("add-link/", views.add_link, name="add_link"),
    path("quick-add/", views.quick_add_page, name="quick_add"),
    # API endpoints
    path("api/categories/", views.api_categories, name="api_categories"),
]
