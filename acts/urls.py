from django.urls import path
from . import views

app_name = 'acts'

urlpatterns = [
    # Home page
    path('', views.home_view, name='home'),
    
    # Search functionality
    path('search/', views.search_view, name='search'),
    path('ajax-search/', views.ajax_search_view, name='ajax_search'),
    
    # API endpoints
    path('api/navigation/', views.get_navigation_data, name='navigation_api'),
    
    # Bookmarks
    path('bookmarks/', views.user_bookmarks_view, name='bookmarks'),
    path('bookmark/toggle/', views.bookmark_toggle_view, name='bookmark_toggle'),
    
    # ===========================================
    # ADD CONTENT URLS - CORRECT HIERARCHY
    # Category → SubCategory → Chapter → Act → Section → Rule/Form/Notification
    # ===========================================
    path('add/', views.add_content_home, name='add_content_home'),
    
    # Step 1: Add Category
    path('add/category/', views.add_category, name='add_category'),
    
    # Step 2: Add SubCategory (requires Category)
    path('add/subcategory/', views.add_subcategory, name='add_subcategory'),
    
    # Step 3: Add Chapter (requires SubCategory)
    path('add/chapter/', views.add_chapter, name='add_chapter'),
    
    # Step 4: Add Act (requires Chapter)
    path('add/act/', views.add_act, name='add_act'),
    
    # Step 5: Add Section (requires Act)
    path('add/section/', views.add_section, name='add_section'),
    path('add/section/<int:act_id>/', views.add_section, name='add_section_with_act'),
    
    # Step 6: Add Rule/Form/Notification (requires Act/Section)
    path('add/rule/', views.add_rule, name='add_rule'),
    path('add/rule/<int:act_id>/', views.add_rule, name='add_rule_with_act'),
    path('add/form/', views.add_form, name='add_form'),
    path('add/form/<int:act_id>/', views.add_form, name='add_form_with_act'),
    path('add/notification/', views.add_notification, name='add_notification'),
    path('add/notification/<int:act_id>/', views.add_notification, name='add_notification_with_act'),
    
    # ===========================================
    # AJAX ENDPOINTS FOR DYNAMIC DROPDOWNS
    # ===========================================
    path('ajax/subcategories/', views.get_subcategories_ajax, name='get_subcategories_ajax'),
    path('ajax/chapters/', views.get_chapters_ajax, name='get_chapters_ajax'),
    path('ajax/acts/', views.get_acts_ajax, name='get_acts_ajax'),
    path('ajax/sections/', views.get_sections_ajax, name='get_sections_ajax'),
    
    # Alternative API endpoints
    path('api/subcategories/<int:category_id>/', views.get_subcategories_by_category, name='api_subcategories'),
    path('api/chapters/<int:subcategory_id>/', views.get_chapters_by_subcategory, name='api_chapters'),
    path('api/acts/<int:chapter_id>/', views.get_acts_by_chapter, name='api_acts'),
    
    # ===========================================
    # CONTENT DISPLAY URLS - CORRECT HIERARCHY
    # ===========================================
    
    # Category level: /acts/category/direct-tax/
    path('category/<slug:slug>/', views.category_detail_view, name='category_detail'),
    
    # SubCategory level: /acts/category/direct-tax/subcategory/income-tax/
    path('category/<slug:category_slug>/subcategory/<slug:slug>/', 
         views.subcategory_detail_view, name='subcategory_detail'),
    
    # Chapter level: /acts/category/direct-tax/subcategory/income-tax/chapter/chapter-1/
    path('category/<slug:category_slug>/subcategory/<slug:subcategory_slug>/chapter/<slug:slug>/', 
         views.chapter_detail_view, name='chapter_detail'),
    
    # Act level: /acts/category/direct-tax/subcategory/income-tax/chapter/chapter-1/act/income-tax-act/
    path('category/<slug:category_slug>/subcategory/<slug:subcategory_slug>/chapter/<slug:chapter_slug>/act/<slug:slug>/', 
         views.act_detail_view, name='act_detail'),
    
    # Section level: /acts/category/direct-tax/subcategory/income-tax/chapter/chapter-1/act/income-tax-act/section/section-1/
    path('category/<slug:category_slug>/subcategory/<slug:subcategory_slug>/chapter/<slug:chapter_slug>/act/<slug:act_slug>/section/<slug:slug>/', 
         views.section_detail_view, name='section_detail'),
    
    # ===========================================
    # RULE/FORM/NOTIFICATION LIST VIEWS
    # ===========================================
    
    # Rules list for an act
    path('category/<slug:category_slug>/subcategory/<slug:subcategory_slug>/chapter/<slug:chapter_slug>/act/<slug:act_slug>/rules/', 
         views.rules_list_view, name='rules_list'),
    
    # Forms list for an act
    path('category/<slug:category_slug>/subcategory/<slug:subcategory_slug>/chapter/<slug:chapter_slug>/act/<slug:act_slug>/forms/', 
         views.forms_list_view, name='forms_list'),
    
    # Notifications list for an act
    path('category/<slug:category_slug>/subcategory/<slug:subcategory_slug>/chapter/<slug:chapter_slug>/act/<slug:act_slug>/notifications/', 
         views.notifications_list_view, name='notifications_list'),
    
    # ===========================================
    # INDIVIDUAL RULE/FORM/NOTIFICATION DETAIL VIEWS
    # ===========================================
    
    # Individual rule detail
    path('category/<slug:category_slug>/subcategory/<slug:subcategory_slug>/chapter/<slug:chapter_slug>/act/<slug:act_slug>/rule/<slug:slug>/', 
         views.rule_detail_view, name='rule_detail'),
    
    # Individual form detail
    path('category/<slug:category_slug>/subcategory/<slug:subcategory_slug>/chapter/<slug:chapter_slug>/act/<slug:act_slug>/form/<slug:slug>/', 
         views.form_detail_view, name='form_detail'),
    
    # Individual notification detail
    path('category/<slug:category_slug>/subcategory/<slug:subcategory_slug>/chapter/<slug:chapter_slug>/act/<slug:act_slug>/notification/<slug:slug>/', 
         views.notification_detail_view, name='notification_detail'),
    
    # ===========================================
    # LEGACY URLS (for backward compatibility)
    # ===========================================
    
    # Simplified act access (if needed)
    path('act/<slug:slug>/', views.act_detail_simple, name='act_detail_simple'),
    
    # Direct category/act access (shortcut)
    path('category/<slug:category_slug>/act/<slug:slug>/', 
         views.act_detail_simple_with_category, name='act_detail_simple_with_category'),
     #     rest full api's
     #     rest full api's
    path('api/subcategory/<slug:subcategory_slug>/', views.api_subcategory_full_detail, name='api-subcategory-full-detail'),

]