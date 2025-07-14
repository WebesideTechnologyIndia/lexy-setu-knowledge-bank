from django.shortcuts import render

# Create your views here.
# rules/views.py - CONVERTED FROM ACTS TO RULES

from django.shortcuts import render, get_object_or_404, redirect
from django.http import JsonResponse, Http404
from django.db.models import Q, Count
from django.core.paginator import Paginator
from django.views.generic import ListView, DetailView
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from django.contrib import messages
from django.contrib.auth.decorators import login_required
import json

from .models import (
    Category, SubCategory, Rule, Chapter, RuleSection, SubRule, 
    Form, Notification, SearchHistory, Bookmark
)

from .forms import (
    CategoryForm, SubCategoryForm, RuleForm, ChapterForm, 
    RuleSectionForm, SubRuleForm, FormForm, NotificationForm
)

def home_view(request):
    """Home page with all categories and featured content"""
    try:
        # Get categories with CORRECT prefetch relationships
        categories = Category.objects.filter(
            is_active=True
        ).prefetch_related(
            'subcategories__chapters__rules'  # Updated path for rules
        ).order_by('order', 'name')
        
        # Get featured rules from all categories
        featured_rules = Rule.objects.filter(
            is_featured=True, 
            is_active=True
        ).select_related(
            'chapter__subcategory__category'
        )[:6]
        
        # Get recent notifications
        recent_notifications = Notification.objects.filter(
            is_active=True
        ).select_related('rule__chapter__subcategory__category')[:5]
        
        # Debug information
        print(f"DEBUG: Found {categories.count()} categories")
        print(f"DEBUG: Found {featured_rules.count()} featured rules")
        print(f"DEBUG: Categories list: {[cat.name for cat in categories]}")
        
        context = {
            'categories': categories,
            'featured_rules': featured_rules,
            'recent_notifications': recent_notifications,
        }
        return render(request, 'rules/home.html', context)
        
    except Exception as e:
        print(f"ERROR in home_view: {e}")
        import traceback
        traceback.print_exc()
        
        # Return empty context on error
        context = {
            'categories': Category.objects.filter(is_active=True),
            'featured_rules': [],
            'recent_notifications': [],
        }
        return render(request, 'rules/home.html', context)


def category_detail_view(request, slug):
    """Display category details with subcategories and all rules"""
    try:
        category = get_object_or_404(
            Category.objects.prefetch_related(
                'subcategories__chapters__rules'
            ),
            slug=slug,
            is_active=True
        )
        
        # Get subcategories
        subcategories = category.subcategories.filter(
            is_active=True
        ).order_by('order', 'name')
        
        # Get ALL rules under this category (through hierarchy)
        all_rules = []
        for subcategory in subcategories:
            for chapter in subcategory.chapters.filter(is_active=True):
                for rule in chapter.rules.filter(is_active=True):
                    all_rules.append(rule)
        
        # Sort rules by name
        all_rules = sorted(all_rules, key=lambda x: x.name)
        
        # Get featured rules from all rules under this category
        featured_rules = [rule for rule in all_rules if rule.is_featured]
        
        # Get recent rules (sorted by creation date)
        recent_rules = sorted(all_rules, key=lambda x: x.created_at, reverse=True)
        
        # Debug information
        print(f"DEBUG: Category: {category.name}")
        print(f"DEBUG: SubCategories: {subcategories.count()}")
        print(f"DEBUG: All Rules found: {len(all_rules)}")
        print(f"DEBUG: Featured Rules: {len(featured_rules)}")
        for rule in all_rules:
            print(f"  - {rule.name} (Chapter: {rule.chapter.name}, SubCat: {rule.chapter.subcategory.name})")
        
        context = {
            'category': category,
            'subcategories': subcategories,
            'all_rules': all_rules,
            'featured_rules': featured_rules,
            'recent_rules': recent_rules,
            'breadcrumbs': [
                {'name': 'Home', 'url': '/'},
                {'name': 'Rules', 'url': '/rules/'},
                {'name': category.name, 'url': None}
            ]
        }
        
        return render(request, 'rules/category_detail.html', context)
        
    except Category.DoesNotExist:
        raise Http404("Category not found")
    except Exception as e:
        print(f"ERROR in category_detail_view: {e}")
        import traceback
        traceback.print_exc()
        messages.error(request, "Error loading category details.")
        return redirect('rules:home')


def subcategory_detail_view(request, category_slug, slug):
    """Display subcategory details with chapters"""
    try:
        subcategory = get_object_or_404(
            SubCategory.objects.select_related('category').prefetch_related(
                'chapters__rules__sections'
            ),
            slug=slug,
            category__slug=category_slug,
            is_active=True
        )
        
        # Get hierarchy objects
        category = subcategory.category
        
        # Get chapters under this subcategory
        chapters = subcategory.chapters.filter(is_active=True).order_by('order', 'chapter_number')
        
        # Debug information
        print(f"DEBUG: SubCategory: {subcategory.name}")
        print(f"DEBUG: Chapters in subcategory: {chapters.count()}")
        for chapter in chapters:
            print(f"  - Chapter: {chapter.name} ({chapter.rules.count()} rules)")
        
        context = {
            'subcategory': subcategory,
            'category': category,
            'chapters': chapters,
            'breadcrumbs': [
                {'name': 'Home', 'url': '/'},
                {'name': 'Rules', 'url': '/rules/'},
                {'name': category.name, 'url': f'/rules/category/{category.slug}/'},
                {'name': subcategory.name, 'url': None}
            ]
        }
        
        return render(request, 'rules/subcategory_detail.html', context)
        
    except SubCategory.DoesNotExist:
        raise Http404("SubCategory not found")
    except Exception as e:
        print(f"ERROR in subcategory_detail_view: {e}")
        import traceback
        traceback.print_exc()
        messages.error(request, "Error loading subcategory details.")
        return redirect('rules:home')


def chapter_detail_view(request, category_slug, subcategory_slug, slug):
    """Display chapter details with rules"""
    try:
        chapter = get_object_or_404(
            Chapter.objects.select_related(
                'subcategory__category'
            ).prefetch_related(
                'rules__sections',
                'rules__subrules',
                'rules__forms',
                'sub_chapters'
            ),
            slug=slug,
            subcategory__slug=subcategory_slug,
            subcategory__category__slug=category_slug,
            is_active=True
        )
        
        # Get hierarchy objects
        subcategory = chapter.subcategory
        category = subcategory.category
        
        # Get rules under this chapter
        rules = chapter.rules.filter(is_active=True).order_by('order', 'name')
        
        # Get sub-chapters if any
        sub_chapters = chapter.sub_chapters.filter(is_active=True).order_by('order', 'chapter_number')
        
        # Debug information
        print(f"DEBUG: Chapter: {chapter.name}")
        print(f"DEBUG: Rules in chapter: {rules.count()}")
        print(f"DEBUG: Sub-chapters: {sub_chapters.count()}")
        
        context = {
            'chapter': chapter,
            'subcategory': subcategory,
            'category': category,
            'rules': rules,
            'sub_chapters': sub_chapters,
            'breadcrumbs': [
                {'name': 'Home', 'url': '/'},
                {'name': 'Rules', 'url': '/rules/'},
                {'name': category.name, 'url': f'/rules/category/{category.slug}/'},
                {'name': subcategory.name, 'url': f'/rules/category/{category.slug}/subcategory/{subcategory.slug}/'},
                {'name': chapter.name, 'url': None}
            ]
        }
        
        return render(request, 'rules/chapter_detail.html', context)
        
    except Chapter.DoesNotExist:
        raise Http404("Chapter not found")
    except Exception as e:
        print(f"ERROR in chapter_detail_view: {e}")
        import traceback
        traceback.print_exc()
        messages.error(request, "Error loading chapter details.")
        return redirect('rules:home')


def rule_detail_view(request, category_slug, subcategory_slug, chapter_slug, slug):
    """Display rule details with its sections"""
    try:
        # Get the rule with proper hierarchy
        rule = get_object_or_404(
            Rule.objects.select_related(
                'chapter__subcategory__category'
            ).prefetch_related(
                'sections__sub_sections',
                'subrules',
                'forms',
                'notifications'
            ),
            slug=slug,
            chapter__slug=chapter_slug,
            chapter__subcategory__slug=subcategory_slug,
            chapter__subcategory__category__slug=category_slug,
            is_active=True
        )
        
        # Get hierarchy objects
        chapter = rule.chapter
        subcategory = chapter.subcategory
        category = subcategory.category
        
        # Get sections for this rule (only parent sections)
        sections = rule.sections.filter(
            is_active=True, 
            parent_section__isnull=True
        ).order_by('order', 'section_number')
        
        # Get related content
        subrules = rule.subrules.filter(is_active=True).order_by('order', 'subrule_number')
        forms = rule.forms.filter(is_active=True).order_by('order', 'form_number')
        notifications = rule.notifications.filter(is_active=True).order_by('-notification_date')
        
        # Get related rules in the same chapter
        related_rules = Rule.objects.filter(
            chapter=chapter,
            is_active=True
        ).exclude(id=rule.id).order_by('order', 'name')[:5]
        
        context = {
            'rule': rule,
            'chapter': chapter,
            'subcategory': subcategory,
            'category': category,
            'sections': sections,
            'subrules': subrules,
            'forms': forms,
            'notifications': notifications,
            'related_rules': related_rules,
            'breadcrumbs': [
                {'name': 'Home', 'url': '/'},
                {'name': 'Rules', 'url': '/rules/'},
                {'name': category.name, 'url': f'/rules/category/{category.slug}/'},
                {'name': subcategory.name, 'url': f'/rules/category/{category.slug}/subcategory/{subcategory.slug}/'},
                {'name': chapter.name, 'url': f'/rules/category/{category.slug}/subcategory/{subcategory.slug}/chapter/{chapter.slug}/'},
                {'name': rule.name, 'url': None}
            ]
        }
        
        return render(request, 'rules/rule_detail.html', context)
        
    except Rule.DoesNotExist:
        raise Http404("Rule not found")
    except Exception as e:
        print(f"ERROR in rule_detail_view: {e}")
        messages.error(request, "Error loading rule details.")
        return redirect('rules:home')


def rule_section_detail_view(request, category_slug, subcategory_slug, chapter_slug, rule_slug, slug):
    """Display rule section details"""
    try:
        rule_section = get_object_or_404(
            RuleSection.objects.select_related(
                'rule__chapter__subcategory__category',
                'parent_section'
            ).prefetch_related(
                'sub_sections',
                'subrules',
                'forms'
            ),
            slug=slug,
            rule__slug=rule_slug,
            rule__chapter__subcategory__category__slug=category_slug,
            is_active=True
        )
        
        # Get sub-sections
        sub_sections = rule_section.sub_sections.filter(is_active=True).order_by('order', 'section_number')
        
        # Get related content
        subrules = rule_section.subrules.filter(is_active=True).order_by('order', 'subrule_number')
        forms = rule_section.forms.filter(is_active=True).order_by('order', 'form_number')
        
        # Navigation context
        rule = rule_section.rule
        chapter = rule.chapter
        subcategory = chapter.subcategory
        category = subcategory.category
        
        context = {
            'rule_section': rule_section,
            'sub_sections': sub_sections,
            'subrules': subrules,
            'forms': forms,
            'rule': rule,
            'chapter': chapter,
            'subcategory': subcategory,
            'category': category,
            'breadcrumbs': [
                {'name': 'Home', 'url': '/'},
                {'name': 'Rules', 'url': '/rules/'},
                {'name': category.name, 'url': f'/rules/category/{category.slug}/'},
                {'name': subcategory.name, 'url': f'/rules/category/{category.slug}/subcategory/{subcategory.slug}/'},
                {'name': chapter.name, 'url': f'/rules/category/{category.slug}/subcategory/{subcategory.slug}/chapter/{chapter.slug}/'},
                {'name': rule.name, 'url': f'/rules/category/{category.slug}/subcategory/{subcategory.slug}/chapter/{chapter.slug}/rule/{rule.slug}/'},
                {'name': f'Section {rule_section.section_number}', 'url': None}
            ]
        }
        
        return render(request, 'rules/rule_section_detail.html', context)
        
    except RuleSection.DoesNotExist:
        raise Http404("Rule Section not found")


def search_view(request):
    """Global search functionality"""
    query = request.GET.get('q', '').strip()
    results = []
    total_results = 0
    
    if query and len(query) >= 2:
        rule_results = Rule.objects.filter(
            Q(name__icontains=query) | 
            Q(full_name__icontains=query) | 
            Q(short_description__icontains=query) |
            Q(rule_number__icontains=query),
            is_active=True
        ).select_related('chapter__subcategory__category')[:20]
        
        section_results = RuleSection.objects.filter(
            Q(name__icontains=query) | 
            Q(content__icontains=query) |
            Q(section_number__icontains=query),
            is_active=True
        ).select_related('rule__chapter__subcategory__category')[:20]
        
        chapter_results = Chapter.objects.filter(
            Q(name__icontains=query) |
            Q(content__icontains=query) |
            Q(chapter_number__icontains=query),
            is_active=True
        ).select_related('subcategory__category')[:20]
        
        subrule_results = SubRule.objects.filter(
            Q(name__icontains=query) |
            Q(content__icontains=query) |
            Q(subrule_number__icontains=query),
            is_active=True
        ).select_related('rule__chapter__subcategory__category')[:10]
        
        form_results = Form.objects.filter(
            Q(name__icontains=query) |
            Q(description__icontains=query) |
            Q(form_number__icontains=query),
            is_active=True
        ).select_related('rule__chapter__subcategory__category')[:10]
        
        results = {
            'rules': rule_results,
            'sections': section_results,
            'chapters': chapter_results,
            'subrules': subrule_results,
            'forms': form_results,
        }
        
        total_results = sum([
            len(rule_results), len(section_results), len(chapter_results),
            len(subrule_results), len(form_results)
        ])
        
        SearchHistory.objects.create(
            query=query,
            results_count=total_results,
            ip_address=request.META.get('REMOTE_ADDR')
        )
    
    context = {
        'query': query,
        'results': results,
        'total_results': total_results,
        'breadcrumb': [
            {'name': 'Home', 'url': '/rules/'},
            {'name': 'Search Results', 'url': ''}
        ]
    }
    return render(request, 'rules/search_results.html', context)


def ajax_search_view(request):
    """AJAX search for autocomplete/suggestions"""
    if request.method == 'POST':
        data = json.loads(request.body)
        query = data.get('query', '').strip()
        
        suggestions = []
        
        if query and len(query) >= 2:
            rules = Rule.objects.filter(
                Q(name__icontains=query) | Q(rule_number__icontains=query),
                is_active=True
            ).values('name', 'slug', 'chapter__subcategory__category__slug')[:5]
            
            for rule in rules:
                suggestions.append({
                    'title': rule['name'],
                    'type': 'Rule',
                    'url': f"/rules/category/{rule['chapter__subcategory__category__slug']}/rule/{rule['slug']}/"
                })
            
            sections = RuleSection.objects.filter(
                Q(name__icontains=query) | Q(section_number__icontains=query),
                is_active=True
            ).select_related('rule__chapter__subcategory__category')[:5]
            
            for section in sections:
                suggestions.append({
                    'title': f"Section {section.section_number}: {section.name}",
                    'type': 'Section',
                    'url': section.get_absolute_url()
                })
        
        return JsonResponse({'suggestions': suggestions})
    
    return JsonResponse({'suggestions': []})


def get_navigation_data(request):
    """API endpoint for navigation data"""
    try:
        categories = Category.objects.filter(
            is_active=True
        ).prefetch_related(
            'subcategories__chapters__rules'
        ).order_by('order', 'name')
        
        navigation_data = []
        for category in categories:
            category_data = {
                'id': category.id,
                'name': category.name,
                'slug': category.slug,
                'icon': category.icon or 'fas fa-folder',
                'subcategories': []
            }
            
            # Add subcategories and their hierarchy
            for subcategory in category.subcategories.filter(is_active=True):
                subcategory_data = {
                    'id': subcategory.id,
                    'name': subcategory.name,
                    'slug': subcategory.slug,
                    'chapters': []
                }
                
                for chapter in subcategory.chapters.filter(is_active=True):
                    chapter_data = {
                        'id': chapter.id,
                        'name': chapter.name,
                        'slug': chapter.slug,
                        'chapter_number': chapter.chapter_number,
                        'rules': []
                    }
                    
                    for rule in chapter.rules.filter(is_active=True):
                        rule_data = {
                            'id': rule.id,
                            'name': rule.name,
                            'slug': rule.slug,
                            'year': rule.year,
                            'rule_number': rule.rule_number
                        }
                        chapter_data['rules'].append(rule_data)
                    
                    subcategory_data['chapters'].append(chapter_data)
                
                category_data['subcategories'].append(subcategory_data)
            
            navigation_data.append(category_data)
        
        return JsonResponse({
            'success': True,
            'data': navigation_data
        })
        
    except Exception as e:
        print(f"ERROR in get_navigation_data: {e}")
        return JsonResponse({
            'success': False,
            'error': 'Navigation data error'
        }, status=500)


def bookmark_toggle_view(request):
    """Toggle bookmark for any content"""
    if request.method == 'POST':
        data = json.loads(request.body)
        content_type = data.get('content_type')
        object_id = data.get('object_id')
        title = data.get('title')
        url = data.get('url')
        
        session_key = request.session.session_key
        if not session_key:
            request.session.create()
            session_key = request.session.session_key
        
        bookmark, created = Bookmark.objects.get_or_create(
            user_session=session_key,
            content_type=content_type,
            object_id=object_id,
            defaults={'title': title, 'url': url}
        )
        
        if not created:
            bookmark.delete()
            return JsonResponse({'bookmarked': False})
        
        return JsonResponse({'bookmarked': True})
    
    return JsonResponse({'error': 'Invalid request'})


def user_bookmarks_view(request):
    """Show user's bookmarks"""
    session_key = request.session.session_key
    bookmarks = []
    
    if session_key:
        bookmarks = Bookmark.objects.filter(user_session=session_key).order_by('-created_at')
    
    context = {
        'bookmarks': bookmarks,
        'breadcrumb': [
            {'name': 'Home', 'url': '/rules/'},
            {'name': 'My Bookmarks', 'url': ''}
        ]
    }
    return render(request, 'rules/bookmarks.html', context)


# ===========================================
# LIST VIEWS FOR SUBRULES/FORMS/NOTIFICATIONS
# ===========================================

def sub_rules_list_view(request, category_slug, subcategory_slug, chapter_slug, rule_slug):
    """List all sub-rules for a rule"""
    try:
        rule = get_object_or_404(
            Rule.objects.select_related('chapter__subcategory__category'),
            slug=rule_slug,
            chapter__subcategory__category__slug=category_slug,
            is_active=True
        )
        
        subrules = rule.subrules.filter(is_active=True).order_by('order', 'subrule_number')
        
        paginator = Paginator(subrules, 20)
        page_number = request.GET.get('page')
        subrules_page = paginator.get_page(page_number)
        
        context = {
            'category': rule.chapter.subcategory.category,
            'subcategory': rule.chapter.subcategory,
            'chapter': rule.chapter,
            'rule': rule,
            'subrules': subrules_page,
            'breadcrumbs': [
                {'name': 'Home', 'url': '/'},
                {'name': 'Rules', 'url': '/rules/'},
                {'name': rule.chapter.subcategory.category.name, 'url': f'/rules/category/{rule.chapter.subcategory.category.slug}/'},
                {'name': rule.chapter.subcategory.name, 'url': f'/rules/category/{rule.chapter.subcategory.category.slug}/subcategory/{rule.chapter.subcategory.slug}/'},
                {'name': rule.chapter.name, 'url': f'/rules/category/{rule.chapter.subcategory.category.slug}/subcategory/{rule.chapter.subcategory.slug}/chapter/{rule.chapter.slug}/'},
                {'name': rule.name, 'url': f'/rules/category/{rule.chapter.subcategory.category.slug}/subcategory/{rule.chapter.subcategory.slug}/chapter/{rule.chapter.slug}/rule/{rule.slug}/'},
                {'name': 'Sub-Rules', 'url': None}
            ]
        }
        return render(request, 'rules/sub_rules_list.html', context)
        
    except Rule.DoesNotExist:
        raise Http404("Rule not found")


def forms_list_view(request, category_slug, subcategory_slug, chapter_slug, rule_slug):
    """List all forms for a rule"""
    try:
        rule = get_object_or_404(
            Rule.objects.select_related('chapter__subcategory__category'),
            slug=rule_slug,
            chapter__subcategory__category__slug=category_slug,
            is_active=True
        )
        
        forms = rule.forms.filter(is_active=True).order_by('order', 'form_number')
        
        paginator = Paginator(forms, 20)
        page_number = request.GET.get('page')
        forms_page = paginator.get_page(page_number)
        
        context = {
            'category': rule.chapter.subcategory.category,
            'subcategory': rule.chapter.subcategory,
            'chapter': rule.chapter,
            'rule': rule,
            'forms': forms_page,
            'breadcrumbs': [
                {'name': 'Home', 'url': '/'},
                {'name': 'Rules', 'url': '/rules/'},
                {'name': rule.chapter.subcategory.category.name, 'url': f'/rules/category/{rule.chapter.subcategory.category.slug}/'},
                {'name': rule.chapter.subcategory.name, 'url': f'/rules/category/{rule.chapter.subcategory.category.slug}/subcategory/{rule.chapter.subcategory.slug}/'},
                {'name': rule.chapter.name, 'url': f'/rules/category/{rule.chapter.subcategory.category.slug}/subcategory/{rule.chapter.subcategory.slug}/chapter/{rule.chapter.slug}/'},
                {'name': rule.name, 'url': f'/rules/category/{rule.chapter.subcategory.category.slug}/subcategory/{rule.chapter.subcategory.slug}/chapter/{rule.chapter.slug}/rule/{rule.slug}/'},
                {'name': 'Forms', 'url': None}
            ]
        }
        return render(request, 'rules/forms_list.html', context)
        
    except Rule.DoesNotExist:
        raise Http404("Rule not found")


def notifications_list_view(request, category_slug, subcategory_slug, chapter_slug, rule_slug):
    """List all notifications for a rule"""
    try:
        rule = get_object_or_404(
            Rule.objects.select_related('chapter__subcategory__category'),
            slug=rule_slug,
            chapter__subcategory__category__slug=category_slug,
            is_active=True
        )
        
        notifications = rule.notifications.filter(is_active=True).order_by('-notification_date')
        
        paginator = Paginator(notifications, 20)
        page_number = request.GET.get('page')
        notifications_page = paginator.get_page(page_number)
        
        context = {
            'category': rule.chapter.subcategory.category,
            'subcategory': rule.chapter.subcategory,
            'chapter': rule.chapter,
            'rule': rule,
            'notifications': notifications_page,
            'breadcrumbs': [
                {'name': 'Home', 'url': '/'},
                {'name': 'Rules', 'url': '/rules/'},
                {'name': rule.chapter.subcategory.category.name, 'url': f'/rules/category/{rule.chapter.subcategory.category.slug}/'},
                {'name': rule.chapter.subcategory.name, 'url': f'/rules/category/{rule.chapter.subcategory.category.slug}/subcategory/{rule.chapter.subcategory.slug}/'},
                {'name': rule.chapter.name, 'url': f'/rules/category/{rule.chapter.subcategory.category.slug}/subcategory/{rule.chapter.subcategory.slug}/chapter/{rule.chapter.slug}/'},
                {'name': rule.name, 'url': f'/rules/category/{rule.chapter.subcategory.category.slug}/subcategory/{rule.chapter.subcategory.slug}/chapter/{rule.chapter.slug}/rule/{rule.slug}/'},
                {'name': 'Notifications', 'url': None}
            ]
        }
        return render(request, 'rules/notifications_list.html', context)
        
    except Rule.DoesNotExist:
        raise Http404("Rule not found")


# ===========================================
# INDIVIDUAL DETAIL VIEWS
# ===========================================

def sub_rule_detail_view(request, category_slug, subcategory_slug, chapter_slug, rule_slug, slug):
    """Display sub-rule details"""
    try:
        sub_rule = get_object_or_404(
            SubRule.objects.select_related(
                'rule__chapter__subcategory__category',
                'section'
            ),
            slug=slug,
            rule__slug=rule_slug,
            rule__chapter__subcategory__category__slug=category_slug,
            is_active=True
        )
        
        # Navigation context
        rule = sub_rule.rule
        chapter = rule.chapter
        subcategory = chapter.subcategory
        category = subcategory.category
        
        context = {
            'sub_rule': sub_rule,
            'rule': rule,
            'chapter': chapter,
            'subcategory': subcategory,
            'category': category,
            'breadcrumbs': [
                {'name': 'Home', 'url': '/'},
                {'name': 'Rules', 'url': '/rules/'},
                {'name': category.name, 'url': f'/rules/category/{category.slug}/'},
                {'name': subcategory.name, 'url': f'/rules/category/{category.slug}/subcategory/{subcategory.slug}/'},
                {'name': chapter.name, 'url': f'/rules/category/{category.slug}/subcategory/{subcategory.slug}/chapter/{chapter.slug}/'},
                {'name': rule.name, 'url': f'/rules/category/{category.slug}/subcategory/{subcategory.slug}/chapter/{chapter.slug}/rule/{rule.slug}/'},
                {'name': f'Sub-Rule {sub_rule.subrule_number}', 'url': None}
            ]
        }
        
        return render(request, 'rules/sub_rule_detail.html', context)
        
    except SubRule.DoesNotExist:
        raise Http404("Sub-Rule not found")


def form_detail_view(request, category_slug, subcategory_slug, chapter_slug, rule_slug, slug):
    """Display form details"""
    try:
        form_doc = get_object_or_404(
            Form.objects.select_related(
                'rule__chapter__subcategory__category',
                'section'
            ),
            slug=slug,
            rule__slug=rule_slug,
            rule__chapter__subcategory__category__slug=category_slug,
            is_active=True
        )
        
        # Navigation context
        rule = form_doc.rule
        chapter = rule.chapter
        subcategory = chapter.subcategory
        category = subcategory.category
        
        context = {
            'form': form_doc,
            'rule': rule,
            'chapter': chapter,
            'subcategory': subcategory,
            'category': category,
            'breadcrumbs': [
                {'name': 'Home', 'url': '/'},
                {'name': 'Rules', 'url': '/rules/'},
                {'name': category.name, 'url': f'/rules/category/{category.slug}/'},
                {'name': subcategory.name, 'url': f'/rules/category/{category.slug}/subcategory/{subcategory.slug}/'},
                {'name': chapter.name, 'url': f'/rules/category/{category.slug}/subcategory/{subcategory.slug}/chapter/{chapter.slug}/'},
                {'name': rule.name, 'url': f'/rules/category/{category.slug}/subcategory/{subcategory.slug}/chapter/{chapter.slug}/rule/{rule.slug}/'},
                {'name': f'Form {form_doc.form_number}', 'url': None}
            ]
        }
        
        return render(request, 'rules/form_detail.html', context)
        
    except Form.DoesNotExist:
        raise Http404("Form not found")


def notification_detail_view(request, category_slug, subcategory_slug, chapter_slug, rule_slug, slug):
    """Display notification details"""
    try:
        notification = get_object_or_404(
            Notification.objects.select_related(
                'rule__chapter__subcategory__category'
            ),
            slug=slug,
            rule__slug=rule_slug,
            rule__chapter__subcategory__category__slug=category_slug,
            is_active=True
        )
        
        # Navigation context
        rule = notification.rule
        chapter = rule.chapter
        subcategory = chapter.subcategory
        category = subcategory.category
        
        context = {
            'notification': notification,
            'rule': rule,
            'chapter': chapter,
            'subcategory': subcategory,
            'category': category,
            'breadcrumbs': [
                {'name': 'Home', 'url': '/'},
                {'name': 'Rules', 'url': '/rules/'},
                {'name': category.name, 'url': f'/rules/category/{category.slug}/'},
                {'name': subcategory.name, 'url': f'/rules/category/{category.slug}/subcategory/{subcategory.slug}/'},
                {'name': chapter.name, 'url': f'/rules/category/{category.slug}/subcategory/{subcategory.slug}/chapter/{chapter.slug}/'},
                {'name': rule.name, 'url': f'/rules/category/{category.slug}/subcategory/{subcategory.slug}/chapter/{chapter.slug}/rule/{rule.slug}/'},
                {'name': f'Notification {notification.notification_number}', 'url': None}
            ]
        }
        
        return render(request, 'rules/notification_detail.html', context)
        
    except Notification.DoesNotExist:
        raise Http404("Notification not found")


def rule_detail_simple(request, slug):
    """Simple rule detail view without full hierarchy"""
    try:
        rule = get_object_or_404(
            Rule.objects.select_related('chapter__subcategory__category'),
            slug=slug,
            is_active=True
        )
        
        # Redirect to the full hierarchical URL
        return redirect('rules:rule_detail', 
                       category_slug=rule.chapter.subcategory.category.slug,
                       subcategory_slug=rule.chapter.subcategory.slug,
                       chapter_slug=rule.chapter.slug,
                       slug=rule.slug)
        
    except Rule.DoesNotExist:
        raise Http404("Rule not found")


def rule_detail_simple_with_category(request, category_slug, slug):
    """Simple rule detail view with category"""
    try:
        rule = get_object_or_404(
            Rule.objects.select_related('chapter__subcategory__category'),
            slug=slug,
            chapter__subcategory__category__slug=category_slug,
            is_active=True
        )
        
        # Redirect to the full hierarchical URL
        return redirect('rules:rule_detail', 
                       category_slug=rule.chapter.subcategory.category.slug,
                       subcategory_slug=rule.chapter.subcategory.slug,
                       chapter_slug=rule.chapter.slug,
                       slug=rule.slug)
        
    except Rule.DoesNotExist:
        raise Http404("Rule not found")


# ===========================================
# ADD CONTENT VIEWS
# ===========================================

def add_content_home(request):
    """Content management dashboard"""
    try:
        context = {
            'categories_count': Category.objects.count(),
            'subcategories_count': SubCategory.objects.count(),
            'chapters_count': Chapter.objects.count(),
            'rules_count': Rule.objects.count(),
            'sections_count': RuleSection.objects.count(),
            'breadcrumb': [
                {'name': 'Home', 'url': '/rules/'},
                {'name': 'Add Content', 'url': ''}
            ]
        }
        return render(request, 'rules/add_content/dashboard.html', context)
    except Exception as e:
        print(f"ERROR in add_content_home: {e}")
        messages.error(request, "Error loading dashboard.")
        return render(request, 'rules/add_content/dashboard.html', {
            'categories_count': 0,
            'subcategories_count': 0,
            'chapters_count': 0,
            'rules_count': 0,
            'sections_count': 0,
            'breadcrumb': []
        })


def add_category(request):
    """Add new category"""
    if request.method == 'POST':
        form = CategoryForm(request.POST)
        if form.is_valid():
            try:
                category = form.save()
                messages.success(request, f'Category "{category.name}" created successfully!')
                return redirect('rules:add_content_home')
            except Exception as e:
                print(f"ERROR saving category: {e}")
                messages.error(request, "Error saving category. Please try again.")
        else:
            messages.error(request, "Please correct the errors below.")
    else:
        form = CategoryForm()
    
    context = {
        'form': form,
        'title': 'Add New Category',
        'breadcrumb': [
            {'name': 'Home', 'url': '/rules/'},
            {'name': 'Add Content', 'url': '/rules/add/'},
            {'name': 'Add Category', 'url': ''}
        ]
    }
    return render(request, 'rules/add_content/add_category.html', context)


def add_subcategory(request):
    """Add new subcategory"""
    if request.method == 'POST':
        form = SubCategoryForm(request.POST)
        if form.is_valid():
            try:
                subcategory = form.save()
                messages.success(request, f'Subcategory "{subcategory.name}" created successfully!')
                return redirect('rules:add_content_home')
            except Exception as e:
                print(f"ERROR saving subcategory: {e}")
                messages.error(request, "Error saving subcategory. Please try again.")
        else:
            messages.error(request, "Please correct the errors below.")
    else:
        form = SubCategoryForm()
    
    # Get categories for dropdown
    categories = Category.objects.filter(is_active=True).order_by('order', 'name')
    
    context = {
        'form': form,
        'categories': categories,
        'title': 'Add New Subcategory',
        'breadcrumb': [
            {'name': 'Home', 'url': '/rules/'},
            {'name': 'Add Content', 'url': '/rules/add/'},
            {'name': 'Add Subcategory', 'url': ''}
        ]
    }
    return render(request, 'rules/add_content/add_subcategory.html', context)


def add_chapter(request):
    """Add new chapter"""
    if request.method == 'POST':
        form = ChapterForm(request.POST)
        if form.is_valid():
            try:
                chapter = form.save()
                messages.success(request, f'Chapter "{chapter.name}" created successfully!')
                return redirect('rules:add_content_home')
            except Exception as e:
                print(f"ERROR saving chapter: {e}")
                messages.error(request, "Error saving chapter. Please try again.")
        else:
            messages.error(request, "Please correct the errors below.")
    else:
        form = ChapterForm()
    
    # Get categories for dropdowns
    categories = Category.objects.filter(is_active=True).order_by('order', 'name')
    
    context = {
        'form': form,
        'categories': categories,
        'title': 'Add New Chapter',
        'breadcrumb': [
            {'name': 'Home', 'url': '/rules/'},
            {'name': 'Add Content', 'url': '/rules/add/'},
            {'name': 'Add Chapter', 'url': ''}
        ]
    }
    return render(request, 'rules/add_content/add_chapter.html', context)


def add_rule(request):
    """Add new rule"""
    if request.method == 'POST':
        form = RuleForm(request.POST)
        if form.is_valid():
            try:
                rule = form.save()
                messages.success(request, f'Rule "{rule.name}" created successfully!')
                return redirect('rules:add_content_home')
            except Exception as e:
                print(f"ERROR saving rule: {e}")
                messages.error(request, "Error saving rule. Please try again.")
        else:
            messages.error(request, "Please correct the errors below.")
            # Print form errors for debugging
            for field, errors in form.errors.items():
                print(f"Form error in {field}: {errors}")
    else:
        form = RuleForm()
    
    # Get categories for dropdown (chapters will be loaded dynamically)
    categories = Category.objects.filter(is_active=True).order_by('order', 'name')
    
    context = {
        'form': form,
        'categories': categories,
        'title': 'Add New Rule',
        'breadcrumb': [
            {'name': 'Home', 'url': '/rules/'},
            {'name': 'Add Content', 'url': '/rules/add/'},
            {'name': 'Add Rule', 'url': ''}
        ]
    }
    return render(request, 'rules/add_content/add_rule.html', context)


def add_rule_section(request, rule_id=None):
    """Add new rule section"""
    rule = None
    if rule_id:
        rule = get_object_or_404(Rule, id=rule_id)
    
    if request.method == 'POST':
        form = RuleSectionForm(request.POST)
        if form.is_valid():
            rule_section = form.save()
            messages.success(request, f'Rule Section "{rule_section.name}" created successfully!')
            return redirect('rules:add_rule_section', rule_id=rule.id)
    else:
        form = RuleSectionForm()
        if rule:
            form.initial['rule'] = rule
    
    context = {
        'form': form,
        'rule': rule,
        'title': 'Add New Rule Section',
        'breadcrumb': [
            {'name': 'Home', 'url': '/rules/'},
            {'name': 'Add Content', 'url': '/rules/add/'},
            {'name': 'Add Rule Section', 'url': ''}
        ]
    }
    return render(request, 'rules/add_content/add_rule_section.html', context)


def add_sub_rule(request, rule_id=None):
    """Add new sub-rule"""
    rule = None
    if rule_id:
        rule = get_object_or_404(Rule, id=rule_id)
    
    if request.method == 'POST':
        form = SubRuleForm(request.POST)
        if form.is_valid():
            sub_rule = form.save()
            messages.success(request, f'Sub-Rule "{sub_rule.name}" created successfully!')
            return redirect('rules:add_sub_rule', rule_id=rule.id)
    else:
        form = SubRuleForm()
        if rule:
            form.initial['rule'] = rule
    
    context = {
        'form': form,
        'rule': rule,
        'title': 'Add New Sub-Rule',
        'breadcrumb': [
            {'name': 'Home', 'url': '/rules/'},
            {'name': 'Add Content', 'url': '/rules/add/'},
            {'name': 'Add Sub-Rule', 'url': ''}
        ]
    }
    return render(request, 'rules/add_content/add_sub_rule.html', context)


def add_form(request, rule_id=None):
    """Add new form"""
    rule = None
    if rule_id:
        rule = get_object_or_404(Rule, id=rule_id)
    
    if request.method == 'POST':
        form = FormForm(request.POST, request.FILES)
        if form.is_valid():
            form_doc = form.save()
            messages.success(request, f'Form "{form_doc.name}" created successfully!')
            return redirect('rules:add_form', rule_id=rule.id)
    else:
        form = FormForm()
        if rule:
            form.initial['rule'] = rule
    
    context = {
        'form': form,
        'rule': rule,
        'title': 'Add New Form',
        'breadcrumb': [
            {'name': 'Home', 'url': '/rules/'},
            {'name': 'Add Content', 'url': '/rules/add/'},
            {'name': 'Add Form', 'url': ''}
        ]
    }
    return render(request, 'rules/add_content/add_form.html', context)


def add_notification(request, rule_id=None):
    """Add new notification"""
    rule = None
    if rule_id:
        rule = get_object_or_404(Rule, id=rule_id)
    
    if request.method == 'POST':
        form = NotificationForm(request.POST, request.FILES)
        if form.is_valid():
            notification = form.save()
            messages.success(request, f'Notification "{notification.title}" created successfully!')
            return redirect('rules:add_notification', rule_id=rule.id)
    else:
        form = NotificationForm()
        if rule:
            form.initial['rule'] = rule
    
    context = {
        'form': form,
        'rule': rule,
        'title': 'Add New Notification',
        'breadcrumb': [
            {'name': 'Home', 'url': '/rules/'},
            {'name': 'Add Content', 'url': '/rules/add/'},
            {'name': 'Add Notification', 'url': ''}
        ]
    }
    return render(request, 'rules/add_content/add_notification.html', context)


# ===========================================
# AJAX VIEWS FOR DYNAMIC DROPDOWNS
# ===========================================

def get_subcategories_ajax(request):
    """AJAX: Get subcategories for a category"""
    try:
        category_id = request.GET.get('category_id')
        if not category_id:
            return JsonResponse({'error': 'Category ID required'}, status=400)
        
        subcategories = SubCategory.objects.filter(
            category_id=category_id, 
            is_active=True
        ).order_by('order', 'name')
        
        data = [
            {
                'id': sub.id,
                'name': sub.name,
                'slug': sub.slug
            }
            for sub in subcategories
        ]
        
        return JsonResponse({'subcategories': data})
        
    except Exception as e:
        print(f"ERROR in get_subcategories_ajax: {e}")
        return JsonResponse({'error': 'Server error'}, status=500)


def get_chapters_ajax(request):
    """AJAX: Get chapters for a subcategory"""
    try:
        subcategory_id = request.GET.get('subcategory_id')
        if not subcategory_id:
            return JsonResponse({'error': 'Subcategory ID required'}, status=400)
        
        chapters = Chapter.objects.filter(
            subcategory_id=subcategory_id, 
            is_active=True
        ).order_by('order', 'chapter_number')
        
        data = [
            {
                'id': chapter.id,
                'name': f"Chapter {chapter.chapter_number}: {chapter.name}",
                'chapter_number': chapter.chapter_number,
                'slug': chapter.slug
            }
            for chapter in chapters
        ]
        
        return JsonResponse({'chapters': data})
        
    except Exception as e:
        print(f"ERROR in get_chapters_ajax: {e}")
        return JsonResponse({'error': 'Server error'}, status=500)


def get_rules_ajax(request):
    """AJAX: Get rules for a chapter"""
    try:
        chapter_id = request.GET.get('chapter_id')
        if not chapter_id:
            return JsonResponse({'error': 'Chapter ID required'}, status=400)
        
        rules = Rule.objects.filter(
            chapter_id=chapter_id, 
            is_active=True
        ).order_by('order', 'name')
        
        data = [
            {
                'id': rule.id,
                'name': rule.name,
                'slug': rule.slug,
                'year': rule.year,
                'rule_number': rule.rule_number
            }
            for rule in rules
        ]
        
        return JsonResponse({'rules': data})
        
    except Exception as e:
        print(f"ERROR in get_rules_ajax: {e}")
        return JsonResponse({'error': 'Server error'}, status=500)


def get_rule_sections_ajax(request):
    """AJAX: Get rule sections for a rule"""
    try:
        rule_id = request.GET.get('rule_id')
        if not rule_id:
            return JsonResponse({'error': 'Rule ID required'}, status=400)
        
        sections = RuleSection.objects.filter(
            rule_id=rule_id, 
            is_active=True,
            parent_section__isnull=True  # Only get top-level sections
        ).order_by('order', 'section_number')
        
        data = [
            {
                'id': section.id,
                'name': f"Section {section.section_number}: {section.name}",
                'section_number': section.section_number,
                'slug': section.slug
            }
            for section in sections
        ]
        
        return JsonResponse({'rule_sections': data})
        
    except Exception as e:
        print(f"ERROR in get_rule_sections_ajax: {e}")
        return JsonResponse({'error': 'Server error'}, status=500)


# ===========================================
# API ENDPOINTS
# ===========================================

def get_subcategories_by_category(request, category_id):
    """API endpoint to get subcategories for a given category"""
    try:
        subcategories = SubCategory.objects.filter(
            category_id=category_id, 
            is_active=True
        ).order_by('order', 'name')
        
        data = [
            {
                'id': sub.id,
                'name': sub.name,
                'slug': sub.slug
            }
            for sub in subcategories
        ]
        return JsonResponse(data, safe=False)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=400)


def get_chapters_by_subcategory(request, subcategory_id):
    """API endpoint to get chapters for a given subcategory"""
    try:
        chapters = Chapter.objects.filter(
            subcategory_id=subcategory_id, 
            is_active=True
        ).order_by('order', 'chapter_number')
        
        data = [
            {
                'id': chapter.id,
                'name': chapter.name,
                'chapter_number': chapter.chapter_number,
                'slug': chapter.slug
            }
            for chapter in chapters
        ]
        return JsonResponse(data, safe=False)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=400)


def get_rules_by_chapter(request, chapter_id):
    """API endpoint to get rules for a given chapter"""
    try:
        rules = Rule.objects.filter(
            chapter_id=chapter_id, 
            is_active=True
        ).order_by('order', 'name')
        
        data = [
            {
                'id': rule.id,
                'name': rule.name,
                'slug': rule.slug,
                'year': rule.year,
                'rule_number': rule.rule_number
            }
            for rule in rules
        ]
        return JsonResponse(data, safe=False)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=400)


def get_rule_sections_by_rule(request, rule_id):
    """API endpoint to get rule sections for a given rule"""
    try:
        sections = RuleSection.objects.filter(
            rule_id=rule_id, 
            is_active=True
        ).order_by('order', 'section_number')
        
        data = [
            {
                'id': section.id,
                'name': section.name,
                'section_number': section.section_number,
                'slug': section.slug
            }
            for section in sections
        ]
        return JsonResponse(data, safe=False)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=400)
    

# Add these view functions to your existing rules/views.py file

from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.db.models import Q
from django.utils import timezone
from datetime import timedelta

def recent_rules_view(request):
    """Display recently viewed or updated rules"""
    try:
        # Get rules updated in the last 30 days
        recent_date = timezone.now() - timedelta(days=30)
        
        # Assuming you have a Rule model - adjust the import and query as needed
        # from .models import Rule
        # recent_rules = Rule.objects.filter(
        #     updated_at__gte=recent_date
        # ).order_by('-updated_at')[:20]
        
        # Placeholder for now - replace with actual query
        recent_rules = []
        
        context = {
            'recent_rules': recent_rules,
            'breadcrumb': [
                {'name': 'Home', 'url': '/rules/'},
                {'name': 'Recent Rules', 'url': None}
            ]
        }
        return render(request, 'rules/recent.html', context)
        
    except Exception as e:
        # Handle any errors gracefully
        context = {
            'recent_rules': [],
            'error': 'Unable to load recent rules',
            'breadcrumb': [
                {'name': 'Home', 'url': '/rules/'},
                {'name': 'Recent Rules', 'url': None}
            ]
        }
        return render(request, 'rules/recent.html', context)

@login_required
def favorites_view(request):
    """Display user's favorite rules"""
    try:
        # Get user's favorite rules
        # Assuming you have a favorites system - adjust as needed
        # from .models import UserFavorite
        # favorites = UserFavorite.objects.filter(
        #     user=request.user
        # ).select_related('rule').order_by('-created_at')
        
        # Placeholder for now - replace with actual query
        favorites = []
        
        context = {
            'favorites': favorites,
            'breadcrumb': [
                {'name': 'Home', 'url': '/rules/'},
                {'name': 'My Favorites', 'url': None}
            ]
        }
        return render(request, 'rules/favorites.html', context)
        
    except Exception as e:
        # Handle any errors gracefully
        context = {
            'favorites': [],
            'error': 'Unable to load favorites',
            'breadcrumb': [
                {'name': 'Home', 'url': '/rules/'},
                {'name': 'My Favorites', 'url': None}
            ]
        }
        return render(request, 'rules/favorites.html', context)
    



from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from django.shortcuts import get_object_or_404
from django.conf import settings
import traceback

# Import your models - UPDATE THESE IMPORTS ACCORDING TO YOUR APP STRUCTURE
from .models import SubCategory, Chapter, Rule, RuleSection, SubRule, Form, Notification
# OR if models are in different app:
# from your_app.models import SubCategory, Chapter, Rule, RuleSection, SubRule, Form, Notification

# Secret key for authentication
SECRET_KEY = "Rahul@121005"

def authenticate_request(request):
    """Check if the request has valid secret key in headers"""
    # Check both secret-key and secret_key for flexibility
    secret_key = request.headers.get('secret-key') or request.headers.get('secret_key')
    return secret_key == SECRET_KEY

@csrf_exempt
@require_http_methods(["GET"])
def get_subcategory_complete_data(request, subcategory_slug):
    """
    Single API endpoint to get complete hierarchical data for a subcategory
    Frontend ko bas subcategory slug bhejni hai with secret key in header
    
    URL: /api/subcategory/{subcategory_slug}/
    Headers: secret-key: Rahul@121005
    
    Returns: Complete nested data structure with chapters -> rules -> sections -> subrules + forms + notifications
    """
    
    # Check authentication
    if not authenticate_request(request):
        return JsonResponse({
            'success': False,
            'error': 'Unauthorized access. Invalid secret key.'
        }, status=401)
    
    try:
        # Get subcategory by slug with all fields
        subcategory = get_object_or_404(SubCategory, slug=subcategory_slug, is_active=True)
        
        # Get all chapters for this subcategory
        chapters = Chapter.objects.filter(
            subcategory_id=subcategory.id, 
            is_active=True
        ).order_by('order', 'chapter_number')
        
        chapters_data = []
        
        for chapter in chapters:
            # Get all rules for this chapter
            rules = Rule.objects.filter(
                chapter_id=chapter.id, 
                is_active=True
            ).order_by('order', 'name')
            
            rules_data = []
            
            for rule in rules:
                # Get all sections for this rule
                sections = RuleSection.objects.filter(
                    rule_id=rule.id, 
                    is_active=True
                ).order_by('order', 'section_number')
                
                sections_data = []
                
                for section in sections:
                    # Get all subrules for this section
                    subrules = SubRule.objects.filter(
                        section_id=section.id, 
                        is_active=True
                    ).order_by('order', 'subrule_number')
                    
                    subrules_data = [
                        {
                            'id': subrule.id,
                            'subrule_number': subrule.subrule_number,
                            'name': subrule.name,
                            'slug': subrule.slug,
                            'content': subrule.content,
                            'description': subrule.description,
                            'effective_date': subrule.effective_date.isoformat() if subrule.effective_date else None,
                            'amendments': subrule.amendments,
                            'order': subrule.order,
                            'is_active': subrule.is_active,
                            'created_at': subrule.created_at.isoformat() if subrule.created_at else None,
                            'updated_at': subrule.updated_at.isoformat() if subrule.updated_at else None
                        }
                        for subrule in subrules
                    ]
                    
                    # Get all forms for this section
                    forms = Form.objects.filter(
                        section_id=section.id, 
                        is_active=True
                    ).order_by('order', 'form_number')
                    
                    forms_data = [
                        {
                            'id': form.id,
                            'form_number': form.form_number,
                            'name': form.name,
                            'slug': form.slug,
                            'description': form.description,
                            'purpose': form.purpose,
                            'pdf_file': form.pdf_file.url if form.pdf_file else None,
                            'excel_file': form.excel_file.url if form.excel_file else None,
                            'effective_date': form.effective_date.isoformat() if form.effective_date else None,
                            'last_updated_date': form.last_updated_date.isoformat() if form.last_updated_date else None,
                            'order': form.order,
                            'is_active': form.is_active,
                            'created_at': form.created_at.isoformat() if form.created_at else None,
                            'updated_at': form.updated_at.isoformat() if form.updated_at else None
                        }
                        for form in forms
                    ]
                    
                    sections_data.append({
                        'id': section.id,
                        'section_number': section.section_number,
                        'name': section.name,
                        'full_name': section.full_name,
                        'slug': section.slug,
                        'content': section.content,
                        'short_description': section.short_description,
                        'notes': section.notes,
                        'amendments': section.amendments,
                        'effective_date': section.effective_date.isoformat() if section.effective_date else None,
                        'order': section.order,
                        'is_active': section.is_active,
                        'created_at': section.created_at.isoformat() if section.created_at else None,
                        'updated_at': section.updated_at.isoformat() if section.updated_at else None,
                        'subrules': subrules_data,
                        'forms': forms_data
                    })
                
                # Get all rule-level subrules (not associated with sections)
                rule_subrules = SubRule.objects.filter(
                    rule_id=rule.id, 
                    section__isnull=True,
                    is_active=True
                ).order_by('order', 'subrule_number')
                
                rule_subrules_data = [
                    {
                        'id': subrule.id,
                        'subrule_number': subrule.subrule_number,
                        'name': subrule.name,
                        'slug': subrule.slug,
                        'content': subrule.content,
                        'description': subrule.description,
                        'effective_date': subrule.effective_date.isoformat() if subrule.effective_date else None,
                        'amendments': subrule.amendments,
                        'order': subrule.order,
                        'is_active': subrule.is_active,
                        'created_at': subrule.created_at.isoformat() if subrule.created_at else None,
                        'updated_at': subrule.updated_at.isoformat() if subrule.updated_at else None
                    }
                    for subrule in rule_subrules
                ]
                
                # Get all rule-level forms (not associated with sections)
                rule_forms = Form.objects.filter(
                    rule_id=rule.id,
                    section__isnull=True,
                    is_active=True
                ).order_by('order', 'form_number')
                
                rule_forms_data = [
                    {
                        'id': form.id,
                        'form_number': form.form_number,
                        'name': form.name,
                        'slug': form.slug,
                        'description': form.description,
                        'purpose': form.purpose,
                        'pdf_file': form.pdf_file.url if form.pdf_file else None,
                        'excel_file': form.excel_file.url if form.excel_file else None,
                        'effective_date': form.effective_date.isoformat() if form.effective_date else None,
                        'last_updated_date': form.last_updated_date.isoformat() if form.last_updated_date else None,
                        'order': form.order,
                        'is_active': form.is_active,
                        'created_at': form.created_at.isoformat() if form.created_at else None,
                        'updated_at': form.updated_at.isoformat() if form.updated_at else None
                    }
                    for form in rule_forms
                ]
                
                # Get all notifications for this rule
                notifications = Notification.objects.filter(
                    rule_id=rule.id,
                    is_active=True
                ).order_by('-notification_date')
                
                notifications_data = [
                    {
                        'id': notification.id,
                        'notification_number': notification.notification_number,
                        'title': notification.title,
                        'slug': notification.slug,
                        'content': notification.content,
                        'summary': notification.summary,
                        'notification_date': notification.notification_date.isoformat() if notification.notification_date else None,
                        'effective_date': notification.effective_date.isoformat() if notification.effective_date else None,
                        'pdf_file': notification.pdf_file.url if notification.pdf_file else None,
                        'notification_type': notification.notification_type,
                        'is_active': notification.is_active,
                        'created_at': notification.created_at.isoformat() if notification.created_at else None,
                        'updated_at': notification.updated_at.isoformat() if notification.updated_at else None
                    }
                    for notification in notifications
                ]
                
                rules_data.append({
                    'id': rule.id,
                    'name': rule.name,
                    'full_name': rule.full_name,
                    'rule_number': rule.rule_number,
                    'year': rule.year,
                    'slug': rule.slug,
                    'short_description': rule.short_description,
                    'long_description': rule.long_description,
                    'amendments': rule.amendments,
                    'last_amended_date': rule.last_amended_date.isoformat() if rule.last_amended_date else None,
                    'enacted_date': rule.enacted_date.isoformat() if rule.enacted_date else None,
                    'effective_date': rule.effective_date.isoformat() if rule.effective_date else None,
                    'order': rule.order,
                    'is_active': rule.is_active,
                    'is_featured': rule.is_featured,
                    'created_at': rule.created_at.isoformat() if rule.created_at else None,
                    'updated_at': rule.updated_at.isoformat() if rule.updated_at else None,
                    'sections': sections_data,
                    'subrules': rule_subrules_data,
                    'forms': rule_forms_data,
                    'notifications': notifications_data
                })
            
            chapters_data.append({
                'id': chapter.id,
                'chapter_number': chapter.chapter_number,
                'name': chapter.name,
                'full_name': chapter.full_name,
                'slug': chapter.slug,
                'description': chapter.description,
                'content': chapter.content,
                'order': chapter.order,
                'is_active': chapter.is_active,
                'level': chapter.level,
                'created_at': chapter.created_at.isoformat() if chapter.created_at else None,
                'updated_at': chapter.updated_at.isoformat() if chapter.updated_at else None,
                'rules': rules_data
            })
        
        # Final response data with complete subcategory info
        response_data = {
            'success': True,
            'subcategory': {
                'id': subcategory.id,
                'name': subcategory.name,
                'slug': subcategory.slug,
                'description': subcategory.description,
                'order': subcategory.order,
                'is_active': subcategory.is_active,
                'created_at': subcategory.created_at.isoformat() if subcategory.created_at else None,
                'updated_at': subcategory.updated_at.isoformat() if subcategory.updated_at else None,
                'category': {
                    'id': subcategory.category.id,
                    'name': subcategory.category.name,
                    'slug': subcategory.category.slug,
                    'description': subcategory.category.description,
                    'icon': subcategory.category.icon
                }
            },
            'chapters': chapters_data,
            'total_chapters': len(chapters_data),
            'statistics': {
                'total_rules': sum(len(chapter['rules']) for chapter in chapters_data),
                'total_sections': sum(len(rule['sections']) for chapter in chapters_data for rule in chapter['rules']),
                'total_subrules': sum(len(rule['subrules']) for chapter in chapters_data for rule in chapter['rules']) + 
                                sum(len(section['subrules']) for chapter in chapters_data for rule in chapter['rules'] for section in rule['sections']),
                'total_forms': sum(len(rule['forms']) for chapter in chapters_data for rule in chapter['rules']) + 
                              sum(len(section['forms']) for chapter in chapters_data for rule in chapter['rules'] for section in rule['sections']),
                'total_notifications': sum(len(rule['notifications']) for chapter in chapters_data for rule in chapter['rules'])
            }
        }
        
        return JsonResponse(response_data, safe=False)
        
    except SubCategory.DoesNotExist:
        return JsonResponse({
            'success': False,
            'error': 'Subcategory not found with this slug'
        }, status=404)
    except Exception as e:
        # Print full traceback for debugging
        print("=" * 50)
        print("ERROR in get_subcategory_complete_data:")
        print(f"Subcategory slug: {subcategory_slug}")
        print(f"Error: {str(e)}")
        print("Traceback:")
        traceback.print_exc()
        print("=" * 50)
        
        return JsonResponse({
            'success': False,
            'error': f'Server error: {str(e)}',
            'debug_info': traceback.format_exc() if settings.DEBUG else None
        }, status=500)