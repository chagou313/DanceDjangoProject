from django.shortcuts import render, get_object_or_404, redirect
from .models import News, UserInteraction  # 使用 news 应用中的 News 模型
from django.db.models import Q
from django.contrib.auth.decorators import login_required
from django.contrib import messages

def news_list(request):
    """新闻资讯列表页"""
    # 获取筛选参数
    category = request.GET.get('category', '')
    keyword = request.GET.get('keyword', '').strip()
    
    # 构建查询
    news_query = News.objects.all()
    
    # 分类筛选
    if category:
        news_query = news_query.filter(category=category)
    
    # 关键字搜索（仅搜索标题和摘要）
    if keyword:
        news_query = news_query.filter(
            Q(title__icontains=keyword) |
            Q(summary__icontains=keyword)
        ).distinct()
    
    # 按时间排序
    news_query = news_query.order_by('-created_at')
    
    context = {
        'news_list': news_query,
        'current_category': category,
        'current_keyword': keyword,
    }
    return render(request, 'news/news_list.html', context)

def news_detail(request, news_id):
    """新闻资讯详情页"""
    news = get_object_or_404(News, id=news_id)
    
    # 增加浏览量
    news.views += 1
    news.save(update_fields=['views'])
    
    # 记录用户访问过的资讯 ID 到 session
    if 'visited_news' not in request.session:
        request.session['visited_news'] = []
    
    visited_news = request.session['visited_news']
    # 移除已存在的（避免重复）
    if news_id in visited_news:
        visited_news.remove(news_id)
    # 添加到开头
    visited_news.insert(0, news_id)
    # 只保留最近 20 个
    request.session['visited_news'] = visited_news[:20]
    request.session.modified = True
    
    # 检查用户是否已点赞/收藏
    user_liked = False
    user_collected = False
    if request.user.is_authenticated:
        user_liked = UserInteraction.objects.filter(user=request.user, news=news, interaction_type='like').exists()
        user_collected = UserInteraction.objects.filter(user=request.user, news=news, interaction_type='collect').exists()
    
    context = {
        'news': news,
        'user_liked': user_liked,
        'user_collected': user_collected,
    }
    return render(request, 'news/news_detail.html', context)

@login_required
def news_like(request, news_id):
    """点赞/取消点赞资讯"""
    news = get_object_or_404(News, id=news_id)
    
    interaction, created = UserInteraction.objects.get_or_create(
        user=request.user,
        news=news,
        interaction_type='like'
    )
    
    if not created:
        # 已点赞，取消点赞
        interaction.delete()
        news.likes = max(0, news.likes - 1)
    else:
        # 新点赞
        news.likes += 1
    
    news.save(update_fields=['likes'])
    
    # 如果是 AJAX 请求，返回 JSON
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        from django.http import JsonResponse
        return JsonResponse({
            'success': True,
            'liked': created,
            'likes_count': news.likes
        })
    
    return redirect('news_detail', news_id=news_id)

@login_required
def news_collect(request, news_id):
    """收藏/取消收藏资讯"""
    news = get_object_or_404(News, id=news_id)
    
    interaction, created = UserInteraction.objects.get_or_create(
        user=request.user,
        news=news,
        interaction_type='collect'
    )
    
    if not created:
        # 已收藏，取消收藏
        interaction.delete()
        news.collections = max(0, news.collections - 1)
    else:
        # 新收藏
        news.collections += 1
    
    news.save(update_fields=['collections'])
    
    # 如果是 AJAX 请求，返回 JSON
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        from django.http import JsonResponse
        return JsonResponse({
            'success': True,
            'collected': created,
            'collections_count': news.collections
        })
    
    return redirect('news_detail', news_id=news_id)
