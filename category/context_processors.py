from .models import Category

def menu_links(request):
    return dict(links=Category.objects.all().order_by('category_name'))
