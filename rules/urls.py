from django.urls import path
from . import views

app_name = 'rules'

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
    # Category → SubCategory → Chapter → Rule → RuleSection → SubRule/Form/Notification
    # ===========================================
    path('add/', views.add_content_home, name='add_content_home'),
    
    # Step 1: Add Category
    path('add/category/', views.add_category, name='add_category'),
    
    # Step 2: Add SubCategory (requires Category)
    path('add/subcategory/', views.add_subcategory, name='add_subcategory'),
    
    # Step 3: Add Chapter (requires SubCategory)
    path('add/chapter/', views.add_chapter, name='add_chapter'),
    
    # Step 4: Add Rule (requires Chapter)
    path('add/rule/', views.add_rule, name='add_rule'),
    
    # Step 5: Add RuleSection (requires Rule)
    path('add/rule-section/', views.add_rule_section, name='add_rule_section'),
    path('add/rule-section/<int:rule_id>/', views.add_rule_section, name='add_rule_section_with_rule'),
    
    # Step 6: Add SubRule/Form/Notification (requires Rule/RuleSection)
    path('add/sub-rule/', views.add_sub_rule, name='add_sub_rule'),
    path('add/sub-rule/<int:rule_id>/', views.add_sub_rule, name='add_sub_rule_with_rule'),
    path('add/form/', views.add_form, name='add_form'),
    path('add/form/<int:rule_id>/', views.add_form, name='add_form_with_rule'),
    path('add/notification/', views.add_notification, name='add_notification'),
    path('add/notification/<int:rule_id>/', views.add_notification, name='add_notification_with_rule'),
    
    # ===========================================
    # AJAX ENDPOINTS FOR DYNAMIC DROPDOWNS
    # ===========================================
    path('ajax/subcategories/', views.get_subcategories_ajax, name='get_subcategories_ajax'),
    path('ajax/chapters/', views.get_chapters_ajax, name='get_chapters_ajax'),
    path('ajax/rules/', views.get_rules_ajax, name='get_rules_ajax'),
    path('ajax/rule-sections/', views.get_rule_sections_ajax, name='get_rule_sections_ajax'),
    
    # Alternative API endpoints
    path('api/subcategories/<int:category_id>/', views.get_subcategories_by_category, name='api_subcategories'),
    path('api/chapters/<int:subcategory_id>/', views.get_chapters_by_subcategory, name='api_chapters'),
    path('api/rules/<int:chapter_id>/', views.get_rules_by_chapter, name='api_rules'),
    path('api/rule-sections/<int:rule_id>/', views.get_rule_sections_by_rule, name='api_rule_sections'),
    
    # ===========================================
    # CONTENT DISPLAY URLS - CORRECT HIERARCHY
    # ===========================================
    
    # Category level: /rules/category/direct-tax/
    path('category/<slug:slug>/', views.category_detail_view, name='category_detail'),
    
    # SubCategory level: /rules/category/direct-tax/subcategory/income-tax/
    path('category/<slug:category_slug>/subcategory/<slug:slug>/', 
         views.subcategory_detail_view, name='subcategory_detail'),
    
    # Chapter level: /rules/category/direct-tax/subcategory/income-tax/chapter/chapter-1/
    path('category/<slug:category_slug>/subcategory/<slug:subcategory_slug>/chapter/<slug:slug>/', 
         views.chapter_detail_view, name='chapter_detail'),
    
    # Rule level: /rules/category/direct-tax/subcategory/income-tax/chapter/chapter-1/rule/income-tax-rules/
    path('category/<slug:category_slug>/subcategory/<slug:subcategory_slug>/chapter/<slug:chapter_slug>/rule/<slug:slug>/', 
         views.rule_detail_view, name='rule_detail'),
    
    # RuleSection level: /rules/category/direct-tax/subcategory/income-tax/chapter/chapter-1/rule/income-tax-rules/section/section-1/
    path('category/<slug:category_slug>/subcategory/<slug:subcategory_slug>/chapter/<slug:chapter_slug>/rule/<slug:rule_slug>/section/<slug:slug>/', 
         views.rule_section_detail_view, name='rule_section_detail'),
    
    # ===========================================
    # SUBRULE/FORM/NOTIFICATION LIST VIEWS
    # ===========================================
    
    # SubRules list for a rule
    path('category/<slug:category_slug>/subcategory/<slug:subcategory_slug>/chapter/<slug:chapter_slug>/rule/<slug:rule_slug>/sub-rules/', 
         views.sub_rules_list_view, name='sub_rules_list'),
    
    # Forms list for a rule
    path('category/<slug:category_slug>/subcategory/<slug:subcategory_slug>/chapter/<slug:chapter_slug>/rule/<slug:rule_slug>/forms/', 
         views.forms_list_view, name='forms_list'),
    
    # Notifications list for a rule
    path('category/<slug:category_slug>/subcategory/<slug:subcategory_slug>/chapter/<slug:chapter_slug>/rule/<slug:rule_slug>/notifications/', 
         views.notifications_list_view, name='notifications_list'),
    
    # ===========================================
    # INDIVIDUAL SUBRULE/FORM/NOTIFICATION DETAIL VIEWS
    # ===========================================
    
    # Individual sub-rule detail
    path('category/<slug:category_slug>/subcategory/<slug:subcategory_slug>/chapter/<slug:chapter_slug>/rule/<slug:rule_slug>/sub-rule/<slug:slug>/', 
         views.sub_rule_detail_view, name='sub_rule_detail'),
    
    # Individual form detail
    path('category/<slug:category_slug>/subcategory/<slug:subcategory_slug>/chapter/<slug:chapter_slug>/rule/<slug:rule_slug>/form/<slug:slug>/', 
         views.form_detail_view, name='form_detail'),
    
    # Individual notification detail
    path('category/<slug:category_slug>/subcategory/<slug:subcategory_slug>/chapter/<slug:chapter_slug>/rule/<slug:rule_slug>/notification/<slug:slug>/', 
         views.notification_detail_view, name='notification_detail'),
    
    # ===========================================
    # LEGACY URLS (for backward compatibility)
    # ===========================================
    
    # Simplified rule access (if needed)
    path('rule/<slug:slug>/', views.rule_detail_simple, name='rule_detail_simple'),
    
    # Direct category/rule access (shortcut)
    path('category/<slug:category_slug>/rule/<slug:slug>/', 
         views.rule_detail_simple_with_category, name='rule_detail_simple_with_category'),
         path('recent/', views.recent_rules_view, name='recent'),
path('favorites/', views.favorites_view, name='favorites'),


     # drf api 
     # drf api 
     # drf api 
     # drf api 
     # drf api 
     # drf api 
     # drf api 
    path('api/subcategory/<str:subcategory_slug>/', views.get_subcategory_complete_data, name='subcategory_data'),

]