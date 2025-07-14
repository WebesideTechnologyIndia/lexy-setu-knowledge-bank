# acts/views.py - FIXED IMPORT ERROR

from django.shortcuts import render, get_object_or_404, redirect
from django.http import JsonResponse
from django.db.models import Q, Count
from django.core.paginator import Paginator
from django.views.generic import ListView, DetailView
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from django.contrib import messages
from django.contrib.auth.decorators import login_required
import json

from .models import (
    Category,
    SubCategory,
    Act,
    Chapter,
    Section,
    Rule,
    Form,
    Notification,
    SearchHistory,
    Bookmark,
)

# FIXED IMPORT - Changed FormDocumentForm to FormForm
from .forms import (
    CategoryForm,
    SubCategoryForm,
    ActForm,
    ChapterForm,
    SectionForm,
    RuleForm,
    FormForm,
    NotificationForm,
)


def home_view(request):
    """Home page with all categories and featured content"""
    try:
        # Get categories with CORRECT prefetch relationships
        categories = (
            Category.objects.filter(is_active=True)
            .prefetch_related("subcategories__chapters__acts")  # This is CORRECT path
            .order_by("order", "name")
        )

        # Get featured acts from all categories
        featured_acts = Act.objects.filter(
            is_featured=True, is_active=True
        ).select_related("chapter__subcategory__category")[:6]

        # Get recent notifications
        recent_notifications = Notification.objects.filter(
            is_active=True
        ).select_related("act__chapter__subcategory__category")[:5]

        # Debug information
        print(f"DEBUG: Found {categories.count()} categories")
        print(f"DEBUG: Found {featured_acts.count()} featured acts")
        print(f"DEBUG: Categories list: {[cat.name for cat in categories]}")

        context = {
            "categories": categories,
            "featured_acts": featured_acts,
            "recent_notifications": recent_notifications,
        }
        return render(request, "acts/home.html", context)

    except Exception as e:
        print(f"ERROR in home_view: {e}")
        import traceback

        traceback.print_exc()

        # Return empty context on error
        context = {
            "categories": Category.objects.filter(is_active=True),
            "featured_acts": [],
            "recent_notifications": [],
        }
        return render(request, "acts/home.html", context)


# Fixed category_detail_view in views.py


def category_detail_view(request, slug):
    """Display category details with subcategories and all acts"""
    try:
        category = get_object_or_404(
            Category.objects.prefetch_related("subcategories__chapters__acts"),
            slug=slug,
            is_active=True,
        )

        # Get subcategories
        subcategories = category.subcategories.filter(is_active=True).order_by(
            "order", "name"
        )

        # Get ALL acts under this category (through hierarchy)
        all_acts = []
        for subcategory in subcategories:
            for chapter in subcategory.chapters.filter(is_active=True):
                for act in chapter.acts.filter(is_active=True):
                    all_acts.append(act)

        # Sort acts by name
        all_acts = sorted(all_acts, key=lambda x: x.name)

        # Get featured acts from all acts under this category
        featured_acts = [act for act in all_acts if act.is_featured]

        # Get recent acts (sorted by creation date)
        recent_acts = sorted(all_acts, key=lambda x: x.created_at, reverse=True)

        # Debug information
        print(f"DEBUG: Category: {category.name}")
        print(f"DEBUG: SubCategories: {subcategories.count()}")
        print(f"DEBUG: All Acts found: {len(all_acts)}")
        print(f"DEBUG: Featured Acts: {len(featured_acts)}")
        for act in all_acts:
            print(
                f"  - {act.name} (Chapter: {act.chapter.name}, SubCat: {act.chapter.subcategory.name})"
            )

        context = {
            "category": category,
            "subcategories": subcategories,
            "all_acts": all_acts,
            "featured_acts": featured_acts,
            "recent_acts": recent_acts,
            "breadcrumbs": [
                {"name": "Home", "url": "/"},
                {"name": "Acts", "url": "/acts/"},
                {"name": category.name, "url": None},
            ],
        }

        return render(request, "acts/category_detail.html", context)

    except Category.DoesNotExist:
        raise Http404("Category not found")
    except Exception as e:
        print(f"ERROR in category_detail_view: {e}")
        import traceback

        traceback.print_exc()
        messages.error(request, "Error loading category details.")
        return redirect("acts:home")


# Also replace/add your subcategory_detail_view function in views.py:


# CHAPTER DIKH RHE H ISESE --------------------------------------------------------------------------------------------------------------
# CHAPTER DIKH RHE H ISESE --------------------------------------------------------------------------------------------------------------
# CHAPTER DIKH RHE H ISESE --------------------------------------------------------------------------------------------------------------
# CHAPTER DIKH RHE H ISESE --------------------------------------------------------------------------------------------------------------


def subcategory_detail_view(request, category_slug, slug):
    """Display subcategory details with chapters"""
    try:
        subcategory = get_object_or_404(
            SubCategory.objects.select_related("category").prefetch_related(
                "chapters__acts__sections"
            ),
            slug=slug,
            category__slug=category_slug,
            is_active=True,
        )

        # Get hierarchy objects
        category = subcategory.category

        # Get chapters under this subcategory
        chapters = subcategory.chapters.filter(is_active=True).order_by(
            "order", "chapter_number"
        )

        # Debug information
        print(f"DEBUG: SubCategory: {subcategory.name}")
        print(f"DEBUG: Chapters in subcategory: {chapters.count()}")
        for chapter in chapters:
            print(f"  - Chapter: {chapter.name} ({chapter.acts.count()} acts)")

        context = {
            "subcategory": subcategory,
            "category": category,
            "chapters": chapters,
            "breadcrumbs": [
                {"name": "Home", "url": "/"},
                {"name": "Acts", "url": "/acts/"},
                {"name": category.name, "url": f"/acts/category/{category.slug}/"},
                {"name": subcategory.name, "url": None},
            ],
        }

        return render(request, "acts/subcategory_detail.html", context)

    except SubCategory.DoesNotExist:
        raise Http404("SubCategory not found")
    except Exception as e:
        print(f"ERROR in subcategory_detail_view: {e}")
        import traceback

        traceback.print_exc()
        messages.error(request, "Error loading subcategory details.")
        return redirect("acts:home")


from django.http import JsonResponse, HttpResponseForbidden
from django.views.decorators.http import require_http_methods
from django.views.decorators.csrf import csrf_exempt
from django.shortcuts import get_object_or_404
from acts.models import SubCategory  # adjust import as needed
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from django.http import JsonResponse, HttpResponseForbidden
from django.shortcuts import get_object_or_404
from .models import Category  # or wherever your Category/SubCategory models are
@csrf_exempt
@require_http_methods(["GET"])
def api_subcategory_full_detail(request, subcategory_slug):
    """API: Return subcategory + its category + chapters, acts, and sections"""

    # Secret Key Validation
    secret_key = request.headers.get("secret-key")
    if secret_key != "Rahul@121005":
        return HttpResponseForbidden("Access Denied: Invalid Secret Key.")

    try:
        subcategory = get_object_or_404(
            SubCategory.objects.select_related("category").prefetch_related("chapters__acts__sections"),
            slug=subcategory_slug,
            is_active=True
        )

        data = {
            "subcategory": {
                "id": subcategory.id,
                "name": subcategory.name,
                "slug": subcategory.slug,
            },
            "category": {
                "id": subcategory.category.id,
                "name": subcategory.category.name,
                "slug": subcategory.category.slug,
            },
            "chapters": [],
        }

        for chapter in subcategory.chapters.filter(is_active=True).order_by("order", "chapter_number"):
            chapter_data = {
                "id": chapter.id,
                "name": chapter.name,
                "chapter_number": chapter.chapter_number,
                "acts": [],
            }

            for act in chapter.acts.all():
                act_data = {
                    "id": act.id,
                    "name": act.name,
                    "slug": act.slug,
                    "full_name": act.full_name,
                    "act_number": act.act_number,
                    "year": act.year,
                    "short_description": act.short_description,
                    "long_description": act.long_description,
                    "amendments": act.amendments,
                    "last_amended_date": act.last_amended_date,
                    "enacted_date": act.enacted_date,
                    "effective_date": act.effective_date,
                    "is_featured": act.is_featured,
                    "sections": [],
                }

                for section in act.sections.all():
                    act_data["sections"].append({
                        "id": section.id,
                        "title": section.title,
                        "section_number": section.section_number,
                        "content": section.content,
                    })

                chapter_data["acts"].append(act_data)

            data["chapters"].append(chapter_data)

        return JsonResponse(data, safe=False, json_dumps_params={"indent": 2})

    except Exception as e:
        import traceback
        traceback.print_exc()
        return JsonResponse(
            {"error": "Error loading subcategory details.", "detail": str(e)},
            status=500,
        )

# --------------------------------------------------------------------------------------------------------------------------------
# --------------------------------------------------------------------------------------------------------------------------------
# --------------------------------------------------------------------------------------------------------------------------------
# --------------------------------------------------------------------------------------------------------------------------------
# --------------------------------------------------------------------------------------------------------------------------------
# --------------------------------------------------------------------------------------------------------------------------------


# Fixed act_detail_view in views.py


def act_detail_view(request, category_slug, subcategory_slug, chapter_slug, slug):
    """Display act details with its sections"""
    try:
        # Get the act with proper hierarchy
        act = get_object_or_404(
            Act.objects.select_related(
                "chapter__subcategory__category"
            ).prefetch_related(
                "sections__sub_sections", "rules", "forms", "notifications"
            ),
            slug=slug,
            chapter__slug=chapter_slug,
            chapter__subcategory__slug=subcategory_slug,
            chapter__subcategory__category__slug=category_slug,
            is_active=True,
        )

        # Get hierarchy objects
        chapter = act.chapter
        subcategory = chapter.subcategory
        category = subcategory.category

        # Get sections for this act (only parent sections)
        sections = act.sections.filter(
            is_active=True, parent_section__isnull=True
        ).order_by("order", "section_number")

        # Get related content
        rules = act.rules.filter(is_active=True).order_by("order", "rule_number")
        forms = act.forms.filter(is_active=True).order_by("order", "form_number")
        notifications = act.notifications.filter(is_active=True).order_by(
            "-notification_date"
        )

        # Get related acts in the same chapter
        related_acts = (
            Act.objects.filter(chapter=chapter, is_active=True)
            .exclude(id=act.id)
            .order_by("order", "name")[:5]
        )

        context = {
            "act": act,
            "chapter": chapter,
            "subcategory": subcategory,
            "category": category,
            "sections": sections,
            "rules": rules,
            "forms": forms,
            "notifications": notifications,
            "related_acts": related_acts,
            "breadcrumbs": [
                {"name": "Home", "url": "/"},
                {"name": "Acts", "url": "/acts/"},
                {"name": category.name, "url": f"/acts/category/{category.slug}/"},
                {
                    "name": subcategory.name,
                    "url": f"/acts/category/{category.slug}/subcategory/{subcategory.slug}/",
                },
                {
                    "name": chapter.name,
                    "url": f"/acts/category/{category.slug}/subcategory/{subcategory.slug}/chapter/{chapter.slug}/",
                },
                {"name": act.name, "url": None},
            ],
        }

        return render(request, "acts/act_detail.html", context)

    except Act.DoesNotExist:
        raise Http404("Act not found")
    except Exception as e:
        print(f"ERROR in act_detail_view: {e}")
        messages.error(request, "Error loading act details.")
        return redirect("acts:home")


# Replace your chapter_detail_view function in views.py with this:


def chapter_detail_view(request, category_slug, subcategory_slug, slug):
    """Display chapter details with acts"""
    try:
        chapter = get_object_or_404(
            Chapter.objects.select_related("subcategory__category").prefetch_related(
                "acts__sections", "acts__rules", "acts__forms", "sub_chapters"
            ),
            slug=slug,
            subcategory__slug=subcategory_slug,
            subcategory__category__slug=category_slug,
            is_active=True,
        )

        # Get hierarchy objects
        subcategory = chapter.subcategory
        category = subcategory.category

        # Get acts under this chapter
        acts = chapter.acts.filter(is_active=True).order_by("order", "name")

        # Get sub-chapters if any
        sub_chapters = chapter.sub_chapters.filter(is_active=True).order_by(
            "order", "chapter_number"
        )

        # Debug information
        print(f"DEBUG: Chapter: {chapter.name}")
        print(f"DEBUG: Acts in chapter: {acts.count()}")
        print(f"DEBUG: Sub-chapters: {sub_chapters.count()}")

        context = {
            "chapter": chapter,
            "subcategory": subcategory,
            "category": category,
            "acts": acts,
            "sub_chapters": sub_chapters,
            "breadcrumbs": [
                {"name": "Home", "url": "/"},
                {"name": "Acts", "url": "/acts/"},
                {"name": category.name, "url": f"/acts/category/{category.slug}/"},
                {
                    "name": subcategory.name,
                    "url": f"/acts/category/{category.slug}/subcategory/{subcategory.slug}/",
                },
                {"name": chapter.name, "url": None},
            ],
        }

        return render(request, "acts/chapter_detail.html", context)

    except Chapter.DoesNotExist:
        raise Http404("Chapter not found")
    except Exception as e:
        print(f"ERROR in chapter_detail_view: {e}")
        import traceback

        traceback.print_exc()
        messages.error(request, "Error loading chapter details.")
        return redirect("acts:home")


def section_detail_view(request, category_slug, act_slug, chapter_slug, slug):
    """Display section details"""
    try:
        section = get_object_or_404(
            Section.objects.select_related(
                "act__category", "act__chapter__subcategory__category", "parent_section"
            ).prefetch_related("sub_sections", "rules", "forms"),
            slug=slug,
            act__slug=act_slug,
            act__category__slug=category_slug,
            is_active=True,
        )

        # Get sub-sections
        sub_sections = section.sub_sections.filter(is_active=True).order_by(
            "order", "section_number"
        )

        # Get related content
        rules = section.rules.filter(is_active=True).order_by("order", "rule_number")
        forms = section.forms.filter(is_active=True).order_by("order", "form_number")

        # Navigation context
        act = section.act
        chapter = act.chapter
        subcategory = chapter.subcategory
        category = act.category

        context = {
            "section": section,
            "sub_sections": sub_sections,
            "rules": rules,
            "forms": forms,
            "act": act,
            "chapter": chapter,
            "subcategory": subcategory,
            "category": category,
            "breadcrumbs": [
                {"name": "Home", "url": "/"},
                {"name": "Acts", "url": "/acts/"},
                {"name": category.name, "url": f"/acts/category/{category.slug}/"},
                {
                    "name": act.name,
                    "url": f"/acts/category/{category.slug}/act/{act.slug}/",
                },
                {"name": f"Section {section.section_number}", "url": None},
            ],
        }

        return render(request, "acts/section_detail.html", context)

    except Section.DoesNotExist:
        raise Http404("Section not found")


def search_view(request):
    """Global search functionality"""
    query = request.GET.get("q", "").strip()
    results = []
    total_results = 0

    if query and len(query) >= 2:
        act_results = Act.objects.filter(
            Q(name__icontains=query)
            | Q(full_name__icontains=query)
            | Q(short_description__icontains=query)
            | Q(act_number__icontains=query),
            is_active=True,
        ).select_related("category")[:20]

        section_results = Section.objects.filter(
            Q(name__icontains=query)
            | Q(content__icontains=query)
            | Q(section_number__icontains=query),
            is_active=True,
        ).select_related("chapter__act__category")[:20]

        chapter_results = Chapter.objects.filter(
            Q(name__icontains=query)
            | Q(content__icontains=query)
            | Q(chapter_number__icontains=query),
            is_active=True,
        ).select_related("act__category")[:20]

        rule_results = Rule.objects.filter(
            Q(name__icontains=query)
            | Q(content__icontains=query)
            | Q(rule_number__icontains=query),
            is_active=True,
        ).select_related("act__category")[:10]

        form_results = Form.objects.filter(
            Q(name__icontains=query)
            | Q(description__icontains=query)
            | Q(form_number__icontains=query),
            is_active=True,
        ).select_related("act__category")[:10]

        results = {
            "acts": act_results,
            "sections": section_results,
            "chapters": chapter_results,
            "rules": rule_results,
            "forms": form_results,
        }

        total_results = sum(
            [
                len(act_results),
                len(section_results),
                len(chapter_results),
                len(rule_results),
                len(form_results),
            ]
        )

        SearchHistory.objects.create(
            query=query,
            results_count=total_results,
            ip_address=request.META.get("REMOTE_ADDR"),
        )

    context = {
        "query": query,
        "results": results,
        "total_results": total_results,
        "breadcrumb": [
            {"name": "Home", "url": "/acts/"},
            {"name": "Search Results", "url": ""},
        ],
    }
    return render(request, "acts/search_results.html", context)


def ajax_search_view(request):
    """AJAX search for autocomplete/suggestions"""
    if request.method == "POST":
        data = json.loads(request.body)
        query = data.get("query", "").strip()

        suggestions = []

        if query and len(query) >= 2:
            acts = Act.objects.filter(
                Q(name__icontains=query) | Q(act_number__icontains=query),
                is_active=True,
            ).values("name", "slug", "category__slug")[:5]

            for act in acts:
                suggestions.append(
                    {
                        "title": act["name"],
                        "type": "Act",
                        "url": f"/acts/category/{act['category__slug']}/act/{act['slug']}/",
                    }
                )

            sections = Section.objects.filter(
                Q(name__icontains=query) | Q(section_number__icontains=query),
                is_active=True,
            ).select_related("chapter__act__category")[:5]

            for section in sections:
                suggestions.append(
                    {
                        "title": f"Section {section.section_number}: {section.name}",
                        "type": "Section",
                        "url": section.get_absolute_url(),
                    }
                )

        return JsonResponse({"suggestions": suggestions})

    return JsonResponse({"suggestions": []})


# In your views.py, replace the get_navigation_data function completely:


def get_navigation_data(request):
    """API endpoint for navigation data - COMPLETELY FIXED"""
    try:
        # Get categories with CORRECT prefetch (remove invalid 'acts' reference)
        categories = (
            Category.objects.filter(is_active=True)
            .prefetch_related(
                "subcategories__chapters__acts"  # This is the CORRECT path
            )
            .order_by("order", "name")
        )

        navigation_data = []
        for category in categories:
            category_data = {
                "id": category.id,
                "name": category.name,
                "slug": category.slug,
                "icon": category.icon or "fas fa-folder",
                "subcategories": [],
                # NO 'acts' field because Category doesn't have direct acts
            }

            # Add subcategories and their hierarchy
            for subcategory in category.subcategories.filter(is_active=True):
                subcategory_data = {
                    "id": subcategory.id,
                    "name": subcategory.name,
                    "slug": subcategory.slug,
                    "chapters": [],
                }

                for chapter in subcategory.chapters.filter(is_active=True):
                    chapter_data = {
                        "id": chapter.id,
                        "name": chapter.name,
                        "slug": chapter.slug,
                        "chapter_number": chapter.chapter_number,
                        "acts": [],
                    }

                    for act in chapter.acts.filter(is_active=True):
                        act_data = {
                            "id": act.id,
                            "name": act.name,
                            "slug": act.slug,
                            "year": act.year,
                            "act_number": act.act_number,
                        }
                        chapter_data["acts"].append(act_data)

                    subcategory_data["chapters"].append(chapter_data)

                category_data["subcategories"].append(subcategory_data)

            navigation_data.append(category_data)

        return JsonResponse({"success": True, "data": navigation_data})

    except Exception as e:
        print(f"ERROR in get_navigation_data: {e}")
        return JsonResponse(
            {"success": False, "error": "Navigation data error"}, status=500
        )


def bookmark_toggle_view(request):
    """Toggle bookmark for any content"""
    if request.method == "POST":
        data = json.loads(request.body)
        content_type = data.get("content_type")
        object_id = data.get("object_id")
        title = data.get("title")
        url = data.get("url")

        session_key = request.session.session_key
        if not session_key:
            request.session.create()
            session_key = request.session.session_key

        bookmark, created = Bookmark.objects.get_or_create(
            user_session=session_key,
            content_type=content_type,
            object_id=object_id,
            defaults={"title": title, "url": url},
        )

        if not created:
            bookmark.delete()
            return JsonResponse({"bookmarked": False})

        return JsonResponse({"bookmarked": True})

    return JsonResponse({"error": "Invalid request"})


def user_bookmarks_view(request):
    """Show user's bookmarks"""
    session_key = request.session.session_key
    bookmarks = []

    if session_key:
        bookmarks = Bookmark.objects.filter(user_session=session_key).order_by(
            "-created_at"
        )

    context = {
        "bookmarks": bookmarks,
        "breadcrumb": [
            {"name": "Home", "url": "/acts/"},
            {"name": "My Bookmarks", "url": ""},
        ],
    }
    return render(request, "acts/bookmarks.html", context)


def notifications_list_view(request, category_slug, act_slug):
    """List all notifications for an act"""
    category = get_object_or_404(Category, slug=category_slug, is_active=True)
    act = get_object_or_404(Act, slug=act_slug, category=category, is_active=True)

    notifications = act.notifications.filter(is_active=True).order_by(
        "-notification_date"
    )

    paginator = Paginator(notifications, 20)
    page_number = request.GET.get("page")
    notifications_page = paginator.get_page(page_number)

    context = {
        "category": category,
        "act": act,
        "notifications": notifications_page,
        "breadcrumb": [
            {"name": "Home", "url": "/acts/"},
            {"name": category.name, "url": f"/acts/category/{category.slug}/"},
            {
                "name": act.name,
                "url": f"/acts/category/{category.slug}/act/{act.slug}/",
            },
            {"name": "Notifications", "url": ""},
        ],
    }
    return render(request, "acts/notifications_list.html", context)


def forms_list_view(request, category_slug, act_slug):
    """List all forms for an act"""
    category = get_object_or_404(Category, slug=category_slug, is_active=True)
    act = get_object_or_404(Act, slug=act_slug, category=category, is_active=True)

    forms = act.forms.filter(is_active=True).order_by("order", "form_number")

    paginator = Paginator(forms, 20)
    page_number = request.GET.get("page")
    forms_page = paginator.get_page(page_number)

    context = {
        "category": category,
        "act": act,
        "forms": forms_page,
        "breadcrumb": [
            {"name": "Home", "url": "/acts/"},
            {"name": category.name, "url": f"/acts/category/{category.slug}/"},
            {
                "name": act.name,
                "url": f"/acts/category/{category.slug}/act/{act.slug}/",
            },
            {"name": "Forms", "url": ""},
        ],
    }
    return render(request, "acts/forms_list.html", context)


def rules_list_view(request, category_slug, act_slug):
    """List all rules for an act"""
    category = get_object_or_404(Category, slug=category_slug, is_active=True)
    act = get_object_or_404(Act, slug=act_slug, category=category, is_active=True)

    rules = act.rules.filter(is_active=True).order_by("order", "rule_number")

    paginator = Paginator(rules, 20)
    page_number = request.GET.get("page")
    rules_page = paginator.get_page(page_number)

    context = {
        "category": category,
        "act": act,
        "rules": rules_page,
        "breadcrumb": [
            {"name": "Home", "url": "/acts/"},
            {"name": category.name, "url": f"/acts/category/{category.slug}/"},
            {
                "name": act.name,
                "url": f"/acts/category/{category.slug}/act/{act.slug}/",
            },
            {"name": "Rules", "url": ""},
        ],
    }
    return render(request, "acts/rules_list.html", context)


# ===========================================
# ADD CONTENT VIEWS - FIXED FORM REFERENCES
# ===========================================


def add_content_home(request):
    """Content management dashboard - FIXED"""
    try:
        context = {
            "categories_count": Category.objects.count(),
            "subcategories_count": SubCategory.objects.count(),
            "chapters_count": Chapter.objects.count(),
            "acts_count": Act.objects.count(),
            "sections_count": Section.objects.count(),
            "breadcrumb": [
                {"name": "Home", "url": "/acts/"},
                {"name": "Add Content", "url": ""},
            ],
        }
        return render(request, "acts/add_content/dashboard.html", context)
    except Exception as e:
        print(f"ERROR in add_content_home: {e}")
        messages.error(request, "Error loading dashboard.")
        return render(
            request,
            "acts/add_content/dashboard.html",
            {
                "categories_count": 0,
                "subcategories_count": 0,
                "chapters_count": 0,
                "acts_count": 0,
                "sections_count": 0,
                "breadcrumb": [],
            },
        )


def add_category(request):
    """Add new category - FIXED"""
    if request.method == "POST":
        form = CategoryForm(request.POST)
        if form.is_valid():
            try:
                category = form.save()
                messages.success(
                    request, f'Category "{category.name}" created successfully!'
                )
                return redirect("acts:add_content_home")
            except Exception as e:
                print(f"ERROR saving category: {e}")
                messages.error(request, "Error saving category. Please try again.")
        else:
            messages.error(request, "Please correct the errors below.")
    else:
        form = CategoryForm()

    context = {
        "form": form,
        "title": "Add New Category",
        "breadcrumb": [
            {"name": "Home", "url": "/acts/"},
            {"name": "Add Content", "url": "/acts/add/"},
            {"name": "Add Category", "url": ""},
        ],
    }
    return render(request, "acts/add_content/add_category.html", context)


def add_subcategory(request):
    """Add new subcategory - FIXED"""
    if request.method == "POST":
        form = SubCategoryForm(request.POST)
        if form.is_valid():
            try:
                subcategory = form.save()
                messages.success(
                    request, f'Subcategory "{subcategory.name}" created successfully!'
                )
                return redirect("acts:add_content_home")
            except Exception as e:
                print(f"ERROR saving subcategory: {e}")
                messages.error(request, "Error saving subcategory. Please try again.")
        else:
            messages.error(request, "Please correct the errors below.")
    else:
        form = SubCategoryForm()

    # Get categories for dropdown
    categories = Category.objects.filter(is_active=True).order_by("order", "name")

    context = {
        "form": form,
        "categories": categories,
        "title": "Add New Subcategory",
        "breadcrumb": [
            {"name": "Home", "url": "/acts/"},
            {"name": "Add Content", "url": "/acts/add/"},
            {"name": "Add Subcategory", "url": ""},
        ],
    }
    return render(request, "acts/add_content/add_subcategory.html", context)


# Update your add_act view in views.py


def add_act(request):
    """Add new act - FIXED to include chapter selection"""
    if request.method == "POST":
        form = ActForm(request.POST)
        if form.is_valid():
            try:
                act = form.save()
                messages.success(request, f'Act "{act.name}" created successfully!')
                return redirect("acts:add_content_home")
            except Exception as e:
                print(f"ERROR saving act: {e}")
                messages.error(request, "Error saving act. Please try again.")
        else:
            messages.error(request, "Please correct the errors below.")
            # Print form errors for debugging
            for field, errors in form.errors.items():
                print(f"Form error in {field}: {errors}")
    else:
        form = ActForm()

    # Get categories for dropdown (chapters will be loaded dynamically)
    categories = Category.objects.filter(is_active=True).order_by("order", "name")

    context = {
        "form": form,
        "categories": categories,
        "title": "Add New Act",
        "breadcrumb": [
            {"name": "Home", "url": "/acts/"},
            {"name": "Add Content", "url": "/acts/add/"},
            {"name": "Add Act", "url": ""},
        ],
    }
    return render(request, "acts/add_content/add_act.html", context)


def add_chapter(request):
    """Add new chapter - FIXED"""
    if request.method == "POST":
        form = ChapterForm(request.POST)
        if form.is_valid():
            try:
                chapter = form.save()
                messages.success(
                    request, f'Chapter "{chapter.name}" created successfully!'
                )
                return redirect("acts:add_content_home")
            except Exception as e:
                print(f"ERROR saving chapter: {e}")
                messages.error(request, "Error saving chapter. Please try again.")
        else:
            messages.error(request, "Please correct the errors below.")
    else:
        form = ChapterForm()

    # Get categories and subcategories for dropdowns
    categories = Category.objects.filter(is_active=True).order_by("order", "name")

    context = {
        "form": form,
        "categories": categories,
        "title": "Add New Chapter",
        "breadcrumb": [
            {"name": "Home", "url": "/acts/"},
            {"name": "Add Content", "url": "/acts/add/"},
            {"name": "Add Chapter", "url": ""},
        ],
    }
    return render(request, "acts/add_content/add_chapter.html", context)


def add_section(request, chapter_id=None):
    """Add new section"""
    chapter = None
    if chapter_id:
        chapter = get_object_or_404(Chapter, id=chapter_id)

    if request.method == "POST":
        form = SectionForm(request.POST)
        if form.is_valid():
            section = form.save()
            messages.success(request, f'Section "{section.name}" created successfully!')
            return redirect("acts:add_section", chapter_id=chapter.id)
    else:
        form = SectionForm()
        if chapter:
            form.initial["chapter"] = chapter

    context = {
        "form": form,
        "chapter": chapter,
        "title": "Add New Section",
        "breadcrumb": [
            {"name": "Home", "url": "/acts/"},
            {"name": "Add Content", "url": "/acts/add/"},
            {"name": "Add Section", "url": ""},
        ],
    }
    return render(request, "acts/add_content/add_section.html", context)


def add_rule(request, act_id=None):
    """Add new rule"""
    act = None
    if act_id:
        act = get_object_or_404(Act, id=act_id)

    if request.method == "POST":
        form = RuleForm(request.POST)
        if form.is_valid():
            rule = form.save()
            messages.success(request, f'Rule "{rule.name}" created successfully!')
            return redirect("acts:add_rule", act_id=act.id)
    else:
        form = RuleForm()
        if act:
            form.initial["act"] = act

    context = {
        "form": form,
        "act": act,
        "title": "Add New Rule",
        "breadcrumb": [
            {"name": "Home", "url": "/acts/"},
            {"name": "Add Content", "url": "/acts/add/"},
            {"name": "Add Rule", "url": ""},
        ],
    }
    return render(request, "acts/add_content/add_rule.html", context)


def add_form(request, act_id=None):
    """Add new form"""
    act = None
    if act_id:
        act = get_object_or_404(Act, id=act_id)

    if request.method == "POST":
        # FIXED: Changed FormDocumentForm to FormForm
        form = FormForm(request.POST, request.FILES)
        if form.is_valid():
            form_doc = form.save()
            messages.success(request, f'Form "{form_doc.name}" created successfully!')
            return redirect("acts:add_form", act_id=act.id)
    else:
        # FIXED: Changed FormDocumentForm to FormForm
        form = FormForm()
        if act:
            form.initial["act"] = act

    context = {
        "form": form,
        "act": act,
        "title": "Add New Form",
        "breadcrumb": [
            {"name": "Home", "url": "/acts/"},
            {"name": "Add Content", "url": "/acts/add/"},
            {"name": "Add Form", "url": ""},
        ],
    }
    return render(request, "acts/add_content/add_form.html", context)


def add_notification(request, act_id=None):
    """Add new notification"""
    act = None
    if act_id:
        act = get_object_or_404(Act, id=act_id)

    if request.method == "POST":
        form = NotificationForm(request.POST, request.FILES)
        if form.is_valid():
            notification = form.save()
            messages.success(
                request, f'Notification "{notification.title}" created successfully!'
            )
            return redirect("acts:add_notification", act_id=act.id)
    else:
        form = NotificationForm()
        if act:
            form.initial["act"] = act

    context = {
        "form": form,
        "act": act,
        "title": "Add New Notification",
        "breadcrumb": [
            {"name": "Home", "url": "/acts/"},
            {"name": "Add Content", "url": "/acts/add/"},
            {"name": "Add Notification", "url": ""},
        ],
    }
    return render(request, "acts/add_content/add_notification.html", context)


# AJAX Views for dynamic dropdowns


def get_subcategories_ajax(request):
    """AJAX: Get subcategories for a category"""
    try:
        category_id = request.GET.get("category_id")
        if not category_id:
            return JsonResponse({"error": "Category ID required"}, status=400)

        subcategories = SubCategory.objects.filter(
            category_id=category_id, is_active=True
        ).order_by("order", "name")

        data = [
            {"id": sub.id, "name": sub.name, "slug": sub.slug} for sub in subcategories
        ]

        return JsonResponse({"subcategories": data})

    except Exception as e:
        print(f"ERROR in get_subcategories_ajax: {e}")
        return JsonResponse({"error": "Server error"}, status=500)


def get_acts(request):
    """Get acts for a category"""
    category_id = request.GET.get("category_id")
    acts = Act.objects.filter(category_id=category_id, is_active=True)
    data = [{"id": act.id, "name": act.name} for act in acts]
    return JsonResponse({"acts": data})


def get_chapters(request):
    """Get chapters for an act"""
    act_id = request.GET.get("act_id")
    chapters = Chapter.objects.filter(act_id=act_id, is_active=True)
    data = [
        {"id": chapter.id, "name": f"Chapter {chapter.chapter_number}: {chapter.name}"}
        for chapter in chapters
    ]
    return JsonResponse({"chapters": data})


def get_sections(request):
    """Get sections for a chapter"""
    chapter_id = request.GET.get("chapter_id")
    sections = Section.objects.filter(chapter_id=chapter_id, is_active=True)
    data = [
        {"id": section.id, "name": f"Section {section.section_number}: {section.name}"}
        for section in sections
    ]
    return JsonResponse({"sections": data})


# Add these views to your views.py file

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.http import JsonResponse
from .models import Category, SubCategory, Chapter, Act
from .forms import ChapterForm  # Make sure you have this form


def add_chapter_view(request):
    """View to add a new chapter"""
    if request.method == "POST":
        form = ChapterForm(request.POST)
        if form.is_valid():
            chapter = form.save(commit=False)

            # Get subcategory from the form data
            subcategory_id = request.POST.get("subcategory")
            if subcategory_id:
                subcategory = get_object_or_404(SubCategory, id=subcategory_id)
                chapter.subcategory = subcategory

            chapter.save()
            messages.success(
                request, f'Chapter "{chapter.name}" has been created successfully!'
            )
            return redirect("acts:add_content_home")  # or wherever you want to redirect
        else:
            messages.error(request, "Please correct the errors below.")
    else:
        form = ChapterForm()

    # Get all categories for the dropdown
    categories = Category.objects.filter(is_active=True).order_by("order", "name")

    context = {
        "form": form,
        "categories": categories,
    }
    return render(request, "acts/add_content/add_chapter.html", context)


# API views for dynamic loading
def get_subcategories_by_category(request, category_id):
    """API endpoint to get subcategories for a given category"""
    try:
        subcategories = SubCategory.objects.filter(
            category_id=category_id, is_active=True
        ).order_by("order", "name")

        data = [
            {"id": sub.id, "name": sub.name, "slug": sub.slug} for sub in subcategories
        ]
        return JsonResponse(data, safe=False)
    except Exception as e:
        return JsonResponse({"error": str(e)}, status=400)


def get_chapters_by_subcategory(request, subcategory_id):
    """API endpoint to get chapters for a given subcategory"""
    try:
        chapters = Chapter.objects.filter(
            subcategory_id=subcategory_id, is_active=True
        ).order_by("order", "chapter_number")

        data = [
            {
                "id": chapter.id,
                "name": chapter.name,
                "chapter_number": chapter.chapter_number,
                "slug": chapter.slug,
            }
            for chapter in chapters
        ]
        return JsonResponse(data, safe=False)
    except Exception as e:
        return JsonResponse({"error": str(e)}, status=400)


def get_subcategories_ajax(request):
    """AJAX: Get subcategories for a category"""
    try:
        category_id = request.GET.get("category_id")
        if not category_id:
            return JsonResponse({"error": "Category ID required"}, status=400)

        subcategories = SubCategory.objects.filter(
            category_id=category_id, is_active=True
        ).order_by("order", "name")

        data = [
            {"id": sub.id, "name": sub.name, "slug": sub.slug} for sub in subcategories
        ]

        return JsonResponse({"subcategories": data})

    except Exception as e:
        print(f"ERROR in get_subcategories_ajax: {e}")
        return JsonResponse({"error": "Server error"}, status=500)


def get_chapters_ajax(request):
    """AJAX: Get chapters for a subcategory"""
    try:
        subcategory_id = request.GET.get("subcategory_id")
        if not subcategory_id:
            return JsonResponse({"error": "Subcategory ID required"}, status=400)

        chapters = Chapter.objects.filter(
            subcategory_id=subcategory_id, is_active=True
        ).order_by("order", "chapter_number")

        data = [
            {
                "id": chapter.id,
                "name": f"Chapter {chapter.chapter_number}: {chapter.name}",
                "chapter_number": chapter.chapter_number,
                "slug": chapter.slug,
            }
            for chapter in chapters
        ]

        return JsonResponse({"chapters": data})

    except Exception as e:
        print(f"ERROR in get_chapters_ajax: {e}")
        return JsonResponse({"error": "Server error"}, status=500)


def get_acts_ajax(request):
    """AJAX: Get acts for a category"""
    try:
        category_id = request.GET.get("category_id")
        if not category_id:
            return JsonResponse({"error": "Category ID required"}, status=400)

        acts = Act.objects.filter(category_id=category_id, is_active=True).order_by(
            "order", "name"
        )

        data = [
            {
                "id": act.id,
                "name": act.name,
                "slug": act.slug,
                "year": act.year,
                "act_number": act.act_number,
            }
            for act in acts
        ]

        return JsonResponse({"acts": data})

    except Exception as e:
        print(f"ERROR in get_acts_ajax: {e}")
        return JsonResponse({"error": "Server error"}, status=500)


# ===========================================
# NAVIGATION AND SEARCH VIEWS
# ===========================================


def get_navigation_data(request):
    """API endpoint for navigation data - FIXED"""
    try:
        categories = (
            Category.objects.filter(is_active=True)
            .prefetch_related("subcategories__chapters__acts", "acts")
            .order_by("order", "name")
        )

        navigation_data = []
        for category in categories:
            category_data = {
                "id": category.id,
                "name": category.name,
                "slug": category.slug,
                "icon": category.icon,
                "subcategories": [],
                "acts": [],
            }

            # Add direct acts under category
            for act in category.acts.filter(is_active=True).order_by("order", "name"):
                act_data = {
                    "id": act.id,
                    "name": act.name,
                    "slug": act.slug,
                    "year": act.year,
                    "act_number": act.act_number,
                }
                category_data["acts"].append(act_data)

            # Add subcategories and their hierarchy
            for subcategory in category.subcategories.filter(is_active=True).order_by(
                "order", "name"
            ):
                subcategory_data = {
                    "id": subcategory.id,
                    "name": subcategory.name,
                    "slug": subcategory.slug,
                    "chapters": [],
                }

                for chapter in subcategory.chapters.filter(is_active=True).order_by(
                    "order", "chapter_number"
                ):
                    chapter_data = {
                        "id": chapter.id,
                        "name": chapter.name,
                        "slug": chapter.slug,
                        "chapter_number": chapter.chapter_number,
                        "acts": [],
                    }

                    for act in chapter.acts.filter(is_active=True).order_by(
                        "order", "name"
                    ):
                        act_data = {
                            "id": act.id,
                            "name": act.name,
                            "slug": act.slug,
                            "year": act.year,
                            "act_number": act.act_number,
                        }
                        chapter_data["acts"].append(act_data)

                    subcategory_data["chapters"].append(chapter_data)

                category_data["subcategories"].append(subcategory_data)

            navigation_data.append(category_data)

        return JsonResponse({"success": True, "data": navigation_data})

    except Exception as e:
        print(f"ERROR in get_navigation_data: {e}")
        return JsonResponse(
            {"success": False, "error": "Server error occurred"}, status=500
        )


def search_view(request):
    """Global search functionality - FIXED"""
    query = request.GET.get("q", "").strip()
    results = {}
    total_results = 0

    if query and len(query) >= 2:
        try:
            # Search acts
            act_results = Act.objects.filter(
                Q(name__icontains=query)
                | Q(full_name__icontains=query)
                | Q(short_description__icontains=query)
                | Q(act_number__icontains=query),
                is_active=True,
            ).select_related("category")[:20]

            # Search sections
            section_results = Section.objects.filter(
                Q(name__icontains=query)
                | Q(content__icontains=query)
                | Q(section_number__icontains=query),
                is_active=True,
            ).select_related("act__category")[:20]

            # Search chapters
            chapter_results = Chapter.objects.filter(
                Q(name__icontains=query)
                | Q(content__icontains=query)
                | Q(chapter_number__icontains=query),
                is_active=True,
            ).select_related("subcategory__category")[:20]

            results = {
                "acts": act_results,
                "sections": section_results,
                "chapters": chapter_results,
            }

            total_results = sum(
                [len(act_results), len(section_results), len(chapter_results)]
            )

            # Save search history
            SearchHistory.objects.create(
                query=query,
                results_count=total_results,
                ip_address=request.META.get("REMOTE_ADDR"),
            )

        except Exception as e:
            print(f"ERROR in search_view: {e}")
            messages.error(request, "Search error occurred. Please try again.")

    context = {
        "query": query,
        "results": results,
        "total_results": total_results,
        "breadcrumb": [
            {"name": "Home", "url": "/acts/"},
            {"name": "Search Results", "url": ""},
        ],
    }
    return render(request, "acts/search_results.html", context)


def get_sections_ajax(request):
    """AJAX: Get sections for an act"""
    try:
        act_id = request.GET.get("act_id")
        if not act_id:
            return JsonResponse({"error": "Act ID required"}, status=400)

        sections = Section.objects.filter(
            act_id=act_id,
            is_active=True,
            parent_section__isnull=True,  # Only get top-level sections
        ).order_by("order", "section_number")

        data = [
            {
                "id": section.id,
                "name": f"Section {section.section_number}: {section.name}",
                "section_number": section.section_number,
                "slug": section.slug,
            }
            for section in sections
        ]

        return JsonResponse({"sections": data})

    except Exception as e:
        print(f"ERROR in get_sections_ajax: {e}")
        return JsonResponse({"error": "Server error"}, status=500)


def get_acts_by_chapter(request, chapter_id):
    """API endpoint to get acts for a given chapter"""
    try:
        acts = Act.objects.filter(chapter_id=chapter_id, is_active=True).order_by(
            "order", "name"
        )

        data = [
            {
                "id": act.id,
                "name": act.name,
                "slug": act.slug,
                "year": act.year,
                "act_number": act.act_number,
            }
            for act in acts
        ]
        return JsonResponse(data, safe=False)
    except Exception as e:
        return JsonResponse({"error": str(e)}, status=400)


# Add these missing view functions to your acts/views.py file


def rule_detail_view(
    request, category_slug, subcategory_slug, chapter_slug, act_slug, slug
):
    """Display rule details"""
    try:
        rule = get_object_or_404(
            Rule.objects.select_related(
                "act__chapter__subcategory__category", "section"
            ),
            slug=slug,
            act__slug=act_slug,
            act__chapter__subcategory__category__slug=category_slug,
            is_active=True,
        )

        # Navigation context
        act = rule.act
        chapter = act.chapter
        subcategory = chapter.subcategory
        category = subcategory.category

        context = {
            "rule": rule,
            "act": act,
            "chapter": chapter,
            "subcategory": subcategory,
            "category": category,
            "breadcrumbs": [
                {"name": "Home", "url": "/"},
                {"name": "Acts", "url": "/acts/"},
                {"name": category.name, "url": f"/acts/category/{category.slug}/"},
                {
                    "name": subcategory.name,
                    "url": f"/acts/category/{category.slug}/subcategory/{subcategory.slug}/",
                },
                {
                    "name": chapter.name,
                    "url": f"/acts/category/{category.slug}/subcategory/{subcategory.slug}/chapter/{chapter.slug}/",
                },
                {
                    "name": act.name,
                    "url": f"/acts/category/{category.slug}/subcategory/{subcategory.slug}/chapter/{chapter.slug}/act/{act.slug}/",
                },
                {"name": f"Rule {rule.rule_number}", "url": None},
            ],
        }

        return render(request, "acts/rule_detail.html", context)

    except Rule.DoesNotExist:
        raise Http404("Rule not found")


def form_detail_view(
    request, category_slug, subcategory_slug, chapter_slug, act_slug, slug
):
    """Display form details"""
    try:
        form_doc = get_object_or_404(
            Form.objects.select_related(
                "act__chapter__subcategory__category", "section"
            ),
            slug=slug,
            act__slug=act_slug,
            act__chapter__subcategory__category__slug=category_slug,
            is_active=True,
        )

        # Navigation context
        act = form_doc.act
        chapter = act.chapter
        subcategory = chapter.subcategory
        category = subcategory.category

        context = {
            "form": form_doc,
            "act": act,
            "chapter": chapter,
            "subcategory": subcategory,
            "category": category,
            "breadcrumbs": [
                {"name": "Home", "url": "/"},
                {"name": "Acts", "url": "/acts/"},
                {"name": category.name, "url": f"/acts/category/{category.slug}/"},
                {
                    "name": subcategory.name,
                    "url": f"/acts/category/{category.slug}/subcategory/{subcategory.slug}/",
                },
                {
                    "name": chapter.name,
                    "url": f"/acts/category/{category.slug}/subcategory/{subcategory.slug}/chapter/{chapter.slug}/",
                },
                {
                    "name": act.name,
                    "url": f"/acts/category/{category.slug}/subcategory/{subcategory.slug}/chapter/{chapter.slug}/act/{act.slug}/",
                },
                {"name": f"Form {form_doc.form_number}", "url": None},
            ],
        }

        return render(request, "acts/form_detail.html", context)

    except Form.DoesNotExist:
        raise Http404("Form not found")


def notification_detail_view(
    request, category_slug, subcategory_slug, chapter_slug, act_slug, slug
):
    """Display notification details"""
    try:
        notification = get_object_or_404(
            Notification.objects.select_related("act__chapter__subcategory__category"),
            slug=slug,
            act__slug=act_slug,
            act__chapter__subcategory__category__slug=category_slug,
            is_active=True,
        )

        # Navigation context
        act = notification.act
        chapter = act.chapter
        subcategory = chapter.subcategory
        category = subcategory.category

        context = {
            "notification": notification,
            "act": act,
            "chapter": chapter,
            "subcategory": subcategory,
            "category": category,
            "breadcrumbs": [
                {"name": "Home", "url": "/"},
                {"name": "Acts", "url": "/acts/"},
                {"name": category.name, "url": f"/acts/category/{category.slug}/"},
                {
                    "name": subcategory.name,
                    "url": f"/acts/category/{category.slug}/subcategory/{subcategory.slug}/",
                },
                {
                    "name": chapter.name,
                    "url": f"/acts/category/{category.slug}/subcategory/{subcategory.slug}/chapter/{chapter.slug}/",
                },
                {
                    "name": act.name,
                    "url": f"/acts/category/{category.slug}/subcategory/{subcategory.slug}/chapter/{chapter.slug}/act/{act.slug}/",
                },
                {
                    "name": f"Notification {notification.notification_number}",
                    "url": None,
                },
            ],
        }

        return render(request, "acts/notification_detail.html", context)

    except Notification.DoesNotExist:
        raise Http404("Notification not found")


def act_detail_simple(request, slug):
    """Simple act detail view without full hierarchy"""
    try:
        act = get_object_or_404(
            Act.objects.select_related("chapter__subcategory__category"),
            slug=slug,
            is_active=True,
        )

        # Redirect to the full hierarchical URL
        return redirect(
            "acts:act_detail",
            category_slug=act.chapter.subcategory.category.slug,
            subcategory_slug=act.chapter.subcategory.slug,
            chapter_slug=act.chapter.slug,
            slug=act.slug,
        )

    except Act.DoesNotExist:
        raise Http404("Act not found")


def act_detail_simple_with_category(request, category_slug, slug):
    """Simple act detail view with category"""
    try:
        act = get_object_or_404(
            Act.objects.select_related("chapter__subcategory__category"),
            slug=slug,
            chapter__subcategory__category__slug=category_slug,
            is_active=True,
        )

        # Redirect to the full hierarchical URL
        return redirect(
            "acts:act_detail",
            category_slug=act.chapter.subcategory.category.slug,
            subcategory_slug=act.chapter.subcategory.slug,
            chapter_slug=act.chapter.slug,
            slug=act.slug,
        )

    except Act.DoesNotExist:
        raise Http404("Act not found")


# Fix the existing section_detail_view (the current one has wrong parameters)
def section_detail_view(
    request, category_slug, subcategory_slug, chapter_slug, act_slug, slug
):
    """Display section details"""
    try:
        section = get_object_or_404(
            Section.objects.select_related(
                "act__chapter__subcategory__category", "parent_section"
            ).prefetch_related("sub_sections", "rules", "forms"),
            slug=slug,
            act__slug=act_slug,
            act__chapter__subcategory__category__slug=category_slug,
            is_active=True,
        )

        # Get sub-sections
        sub_sections = section.sub_sections.filter(is_active=True).order_by(
            "order", "section_number"
        )

        # Get related content
        rules = section.rules.filter(is_active=True).order_by("order", "rule_number")
        forms = section.forms.filter(is_active=True).order_by("order", "form_number")

        # Navigation context
        act = section.act
        chapter = act.chapter
        subcategory = chapter.subcategory
        category = subcategory.category

        context = {
            "section": section,
            "sub_sections": sub_sections,
            "rules": rules,
            "forms": forms,
            "act": act,
            "chapter": chapter,
            "subcategory": subcategory,
            "category": category,
            "breadcrumbs": [
                {"name": "Home", "url": "/"},
                {"name": "Acts", "url": "/acts/"},
                {"name": category.name, "url": f"/acts/category/{category.slug}/"},
                {
                    "name": subcategory.name,
                    "url": f"/acts/category/{category.slug}/subcategory/{subcategory.slug}/",
                },
                {
                    "name": chapter.name,
                    "url": f"/acts/category/{category.slug}/subcategory/{subcategory.slug}/chapter/{chapter.slug}/",
                },
                {
                    "name": act.name,
                    "url": f"/acts/category/{category.slug}/subcategory/{subcategory.slug}/chapter/{chapter.slug}/act/{act.slug}/",
                },
                {"name": f"Section {section.section_number}", "url": None},
            ],
        }

        return render(request, "acts/section_detail.html", context)

    except Section.DoesNotExist:
        raise Http404("Section not found")


# Fix the list views to match the URL patterns
def rules_list_view(request, category_slug, subcategory_slug, chapter_slug, act_slug):
    """List all rules for an act"""
    try:
        act = get_object_or_404(
            Act.objects.select_related("chapter__subcategory__category"),
            slug=act_slug,
            chapter__subcategory__category__slug=category_slug,
            is_active=True,
        )

        rules = act.rules.filter(is_active=True).order_by("order", "rule_number")

        paginator = Paginator(rules, 20)
        page_number = request.GET.get("page")
        rules_page = paginator.get_page(page_number)

        context = {
            "category": act.chapter.subcategory.category,
            "subcategory": act.chapter.subcategory,
            "chapter": act.chapter,
            "act": act,
            "rules": rules_page,
            "breadcrumbs": [
                {"name": "Home", "url": "/"},
                {"name": "Acts", "url": "/acts/"},
                {
                    "name": act.chapter.subcategory.category.name,
                    "url": f"/acts/category/{act.chapter.subcategory.category.slug}/",
                },
                {
                    "name": act.chapter.subcategory.name,
                    "url": f"/acts/category/{act.chapter.subcategory.category.slug}/subcategory/{act.chapter.subcategory.slug}/",
                },
                {
                    "name": act.chapter.name,
                    "url": f"/acts/category/{act.chapter.subcategory.category.slug}/subcategory/{act.chapter.subcategory.slug}/chapter/{act.chapter.slug}/",
                },
                {
                    "name": act.name,
                    "url": f"/acts/category/{act.chapter.subcategory.category.slug}/subcategory/{act.chapter.subcategory.slug}/chapter/{act.chapter.slug}/act/{act.slug}/",
                },
                {"name": "Rules", "url": None},
            ],
        }
        return render(request, "acts/rules_list.html", context)

    except Act.DoesNotExist:
        raise Http404("Act not found")


def forms_list_view(request, category_slug, subcategory_slug, chapter_slug, act_slug):
    """List all forms for an act"""
    try:
        act = get_object_or_404(
            Act.objects.select_related("chapter__subcategory__category"),
            slug=act_slug,
            chapter__subcategory__category__slug=category_slug,
            is_active=True,
        )

        forms = act.forms.filter(is_active=True).order_by("order", "form_number")

        paginator = Paginator(forms, 20)
        page_number = request.GET.get("page")
        forms_page = paginator.get_page(page_number)

        context = {
            "category": act.chapter.subcategory.category,
            "subcategory": act.chapter.subcategory,
            "chapter": act.chapter,
            "act": act,
            "forms": forms_page,
            "breadcrumbs": [
                {"name": "Home", "url": "/"},
                {"name": "Acts", "url": "/acts/"},
                {
                    "name": act.chapter.subcategory.category.name,
                    "url": f"/acts/category/{act.chapter.subcategory.category.slug}/",
                },
                {
                    "name": act.chapter.subcategory.name,
                    "url": f"/acts/category/{act.chapter.subcategory.category.slug}/subcategory/{act.chapter.subcategory.slug}/",
                },
                {
                    "name": act.chapter.name,
                    "url": f"/acts/category/{act.chapter.subcategory.category.slug}/subcategory/{act.chapter.subcategory.slug}/chapter/{act.chapter.slug}/",
                },
                {
                    "name": act.name,
                    "url": f"/acts/category/{act.chapter.subcategory.category.slug}/subcategory/{act.chapter.subcategory.slug}/chapter/{act.chapter.slug}/act/{act.slug}/",
                },
                {"name": "Forms", "url": None},
            ],
        }
        return render(request, "acts/forms_list.html", context)

    except Act.DoesNotExist:
        raise Http404("Act not found")


def notifications_list_view(
    request, category_slug, subcategory_slug, chapter_slug, act_slug
):
    """List all notifications for an act"""
    try:
        act = get_object_or_404(
            Act.objects.select_related("chapter__subcategory__category"),
            slug=act_slug,
            chapter__subcategory__category__slug=category_slug,
            is_active=True,
        )

        notifications = act.notifications.filter(is_active=True).order_by(
            "-notification_date"
        )

        paginator = Paginator(notifications, 20)
        page_number = request.GET.get("page")
        notifications_page = paginator.get_page(page_number)

        context = {
            "category": act.chapter.subcategory.category,
            "subcategory": act.chapter.subcategory,
            "chapter": act.chapter,
            "act": act,
            "notifications": notifications_page,
            "breadcrumbs": [
                {"name": "Home", "url": "/"},
                {"name": "Acts", "url": "/acts/"},
                {
                    "name": act.chapter.subcategory.category.name,
                    "url": f"/acts/category/{act.chapter.subcategory.category.slug}/",
                },
                {
                    "name": act.chapter.subcategory.name,
                    "url": f"/acts/category/{act.chapter.subcategory.category.slug}/subcategory/{act.chapter.subcategory.slug}/",
                },
                {
                    "name": act.chapter.name,
                    "url": f"/acts/category/{act.chapter.subcategory.category.slug}/subcategory/{act.chapter.subcategory.slug}/chapter/{act.chapter.slug}/",
                },
                {
                    "name": act.name,
                    "url": f"/acts/category/{act.chapter.subcategory.category.slug}/subcategory/{act.chapter.subcategory.slug}/chapter/{act.chapter.slug}/act/{act.slug}/",
                },
                {"name": "Notifications", "url": None},
            ],
        }
        return render(request, "acts/notifications_list.html", context)

    except Act.DoesNotExist:
        raise Http404("Act not found")
