from django.shortcuts import render
from origin.models import News  # 使用 origin 应用中的 News 模型

def news_list(request):
    """新闻资讯列表页"""
    # 获取分类筛选
    category = request.GET.get('category', '')
    
    if category:
        news_list = News.objects.filter(category=category, is_hot=True).order_by('-created_at')[:12]
    else:
        news_list = News.objects.filter(is_hot=True).order_by('-created_at')[:12]
    
    context = {
        'news_list': news_list,
        'current_category': category,
    }
    return render(request, 'news/news_list.html', context)
