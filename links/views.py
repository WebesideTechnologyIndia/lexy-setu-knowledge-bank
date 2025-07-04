from django.shortcuts import render

# Create your views here.
# views.py

from django.shortcuts import render, get_object_or_404, redirect
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.generic import ListView, DetailView
from .models import Category, SubCategory, Link, LinkClick

def get_client_ip(request):
    """Get client IP address"""
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0]
    else:
        ip = request.META.get('REMOTE_ADDR')
    return ip

class HomeView(ListView):
    """Homepage showing all categories"""
    model = Category
    template_name = 'links/home.html'
    context_object_name = 'categories'
    
    def get_queryset(self):
        return Category.objects.filter(is_active=True).prefetch_related('subcategories__links')

class CategoryDetailView(DetailView):
    """Category detail page showing subcategories"""
    model = Category
    template_name = 'links/category_detail.html'
    context_object_name = 'category'
    slug_field = 'slug'
    slug_url_kwarg = 'slug'
    
    def get_queryset(self):
        return Category.objects.filter(is_active=True)

class SubCategoryDetailView(DetailView):
    """Subcategory detail page showing links"""
    model = SubCategory
    template_name = 'links/subcategory_detail.html'
    context_object_name = 'subcategory'
    
    def get_object(self):
        return get_object_or_404(
            SubCategory.objects.select_related('category'),
            category__slug=self.kwargs['category_slug'],
            slug=self.kwargs['slug'],
            is_active=True
        )

def link_redirect(request, link_id):
    """Redirect to external link and track click"""
    link = get_object_or_404(Link, id=link_id, is_active=True)
    
    # Track the click
    LinkClick.objects.create(
        link=link,
        ip_address=get_client_ip(request),
        user_agent=request.META.get('HTTP_USER_AGENT', '')[:500]
    )
    
    # Increment click count
    link.increment_click_count()
    
    return redirect(link.url)

def api_categories(request):
    """API endpoint for categories with subcategories"""
    categories = Category.objects.filter(is_active=True).prefetch_related(
        'subcategories__links'
    )
    
    data = []
    for category in categories:
        category_data = {
            'id': category.id,
            'name': category.name,
            'slug': category.slug,
            'subcategories': []
        }
        
        for subcategory in category.subcategories.filter(is_active=True):
            subcategory_data = {
                'id': subcategory.id,
                'name': subcategory.name,
                'slug': subcategory.slug,
                'links': []
            }
            
            for link in subcategory.links.filter(is_active=True):
                link_data = {
                    'id': link.id,
                    'title': link.title,
                    'url': f'/link/{link.id}/',  # Use redirect URL
                    'click_count': link.click_count
                }
                subcategory_data['links'].append(link_data)
            
            category_data['subcategories'].append(subcategory_data)
        
        data.append(category_data)
    
    return JsonResponse({'categories': data})

def search_links(request):
    """Search functionality for links"""
    query = request.GET.get('q', '').strip()
    
    if not query:
        return render(request, 'links/search.html', {'query': query, 'results': []})
    
    # Search in link titles and descriptions
    links = Link.objects.filter(
        is_active=True,
        subcategory__is_active=True,
        subcategory__category__is_active=True
    ).filter(
        title__icontains=query
    ).select_related('subcategory__category')[:50]
    
    results = []
    for link in links:
        results.append({
            'link': link,
            'category': link.subcategory.category.name,
            'subcategory': link.subcategory.name
        })
    
    return render(request, 'links/search.html', {
        'query': query,
        'results': results,
        'total_results': len(results)
    })

# Add these views to your views.py

from django.shortcuts import render, get_object_or_404, redirect
from django.http import JsonResponse
from django.contrib import messages
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST
from django.utils.text import slugify
from .models import Category, SubCategory, Link, LinkClick

@require_POST
def add_subcategory(request):
    """Add new subcategory via HTML form"""
    try:
        category_id = request.POST.get('category_id')
        name = request.POST.get('name')
        description = request.POST.get('description', '')
        
        if not category_id or not name:
            messages.error(request, 'Category and name are required!')
            return redirect('links:home')
        
        category = get_object_or_404(Category, id=category_id)
        
        # Create slug from name
        slug = slugify(name)
        
        # Check if subcategory already exists
        if SubCategory.objects.filter(category=category, slug=slug).exists():
            messages.error(request, f'Sub category "{name}" already exists in this category!')
        else:
            SubCategory.objects.create(
                category=category,
                name=name,
                slug=slug,
                description=description
            )
            messages.success(request, f'Sub category "{name}" added successfully!')
        
        return redirect('links:category_detail', slug=category.slug)
        
    except Exception as e:
        messages.error(request, f'Error adding sub category: {str(e)}')
        return redirect('links:home')

@require_POST
def add_link(request):
    """Add new link via HTML form"""
    try:
        subcategory_id = request.POST.get('subcategory_id')
        title = request.POST.get('title')
        url = request.POST.get('url')
        description = request.POST.get('description', '')
        
        if not subcategory_id or not title or not url:
            messages.error(request, 'Sub category, title and URL are required!')
            return redirect('links:home')
        
        subcategory = get_object_or_404(SubCategory, id=subcategory_id)
        
        # Check if link already exists
        if Link.objects.filter(subcategory=subcategory, title=title).exists():
            messages.error(request, f'Link "{title}" already exists in this sub category!')
        else:
            Link.objects.create(
                subcategory=subcategory,
                title=title,
                url=url,
                description=description
            )
            messages.success(request, f'Link "{title}" added successfully!')
        
        return redirect('links:subcategory_detail', 
                       category_slug=subcategory.category.slug, 
                       slug=subcategory.slug)
        
    except Exception as e:
        messages.error(request, f'Error adding link: {str(e)}')
        return redirect('links:home')

@require_POST
def add_category(request):
    """Add new category via HTML form"""
    try:
        name = request.POST.get('name')
        description = request.POST.get('description', '')
        
        if not name:
            messages.error(request, 'Category name is required!')
            return redirect('links:home')
        
        # Create slug from name
        slug = slugify(name)
        
        # Check if category already exists
        if Category.objects.filter(slug=slug).exists():
            messages.error(request, f'Category "{name}" already exists!')
        else:
            Category.objects.create(
                name=name,
                slug=slug,
                description=description
            )
            messages.success(request, f'Category "{name}" added successfully!')
        
        return redirect('links:home')
        
    except Exception as e:
        messages.error(request, f'Error adding category: {str(e)}')
        return redirect('links:home')

def quick_add_page(request):
    """Quick add page for bulk adding"""
    categories = Category.objects.filter(is_active=True)
    return render(request, 'links/quick_add.html', {'categories': categories})