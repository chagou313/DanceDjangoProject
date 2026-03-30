from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Count, Q
from django.core.paginator import Paginator
from .models import Post, Comment, PostLike, PostCollection, Topic

def community_posts(request):
    """交流社区首页 - 显示所有帖子"""
    print("\n=== Community View Debug ===")
    print(f"Request path: {request.path}")
    print(f"User: {request.user}")
    print(f"User is authenticated: {request.user.is_authenticated}")
    
    # 获取筛选参数
    topic_id = request.GET.get('topic')
    order_by = request.GET.get('order', 'latest')  # latest, hot, featured
    
    # 基础查询集：已发布的帖子
    posts = Post.objects.filter(status='published').select_related('author', 'topic')
    
    # 话题筛选
    if topic_id:
        posts = posts.filter(topic_id=topic_id)
        print(f"Filtered by topic: {topic_id}")
    
    # 排序
    if order_by == 'hot':
        # 热门：按浏览量降序
        posts = posts.order_by('-views', '-created_at')
    elif order_by == 'featured':
        # 精华：按点赞 + 收藏的总数量降序
        from django.db.models import F
        posts = posts.annotate(
            total_score=F('likes') + F('collections')
        ).order_by('-total_score', '-is_featured', '-created_at')
    else:
        # 最新：按时间倒序
        posts = posts.order_by('-created_at')
    
    # 分页
    paginator = Paginator(posts, 12)  # 每页 12 个帖子
    page = request.GET.get('page')
    posts = paginator.get_page(page)
    
    # 获取所有话题
    topics = Topic.objects.all()
    
    # 打印调试信息
    print(f"✓ Found {posts.paginator.count} total posts in database")
    print(f"✓ Showing page {posts.number} of {posts.paginator.num_pages}")
    if posts:
        print(f"✓ First post on this page: {posts[0].title} (by {posts[0].author.username})")
    
    context = {
        'posts': posts,
        'topics': topics,
        'current_topic': int(topic_id) if topic_id else None,
        'order_by': order_by,
    }
    
    print("==========================\n")
    return render(request, 'community/community_posts.html', context)

@login_required
def post_detail(request, post_id):
    """帖子详情页"""
    post = get_object_or_404(Post, id=post_id)
    
    # 增加浏览量
    post.views += 1
    post.save(update_fields=['views'])
    
    # 记录用户访问过的帖子 ID 到 session，用于返回列表页时更新显示
    if 'visited_posts' not in request.session:
        request.session['visited_posts'] = {}
    
    # 存储帖子 ID 和新的浏览量
    request.session['visited_posts'][str(post_id)] = post.views
    # 标记为已修改，确保保存 session
    request.session.modified = True
    
    # 获取评论
    comments = post.comments.filter(parent=None, is_deleted=False)
    
    # 检查用户是否已点赞
    user_liked = False
    user_collected = False
    if request.user.is_authenticated:
        user_liked = PostLike.objects.filter(post=post, user=request.user).exists()
        user_collected = PostCollection.objects.filter(post=post, user=request.user).exists()
    
    # 处理标签
    tags_list = []
    if post.tags:
        tags_list = [tag.strip() for tag in post.tags.split(',') if tag.strip()]
    
    context = {
        'post': post,
        'comments': comments,
        'user_liked': user_liked,
        'user_collected': user_collected,
        'tags_list': tags_list,
    }
    
    return render(request, 'community/post_detail.html', context)

@login_required
def create_post(request):
    """发布新帖子"""
    if request.method == 'POST':
        title = request.POST.get('title')
        content = request.POST.get('content')
        topic_id = request.POST.get('topic')
        tags = request.POST.get('tags')
        cover_image = request.FILES.get('cover_image')
        
        if not title or not content:
            messages.error(request, '标题和内容不能为空')
            return redirect('create_post')
        
        # 获取话题对象
        topic = None
        if topic_id:
            topic = get_object_or_404(Topic, id=topic_id)
        
        post = Post.objects.create(
            title=title,
            content=content,
            author=request.user,
            topic=topic,
            tags=tags,
            cover_image=cover_image,
            status='published'
        )
        
        messages.success(request, '帖子发布成功！')
        return redirect('community_posts')  # 跳转到社区主页（帖子列表）
    
    # GET 请求，显示发帖表单
    topics = Topic.objects.all()
    return render(request, 'community/create_post.html', {'topics': topics})

@login_required
def toggle_like(request, post_id):
    """点赞/取消点赞"""
    post = get_object_or_404(Post, id=post_id)
    
    like, created = PostLike.objects.get_or_create(
        post=post,
        user=request.user
    )
    
    if not created:
        # 如果已存在，则删除（取消点赞）
        like.delete()
        post.likes -= 1
        messages.info(request, '已取消点赞')
    else:
        post.likes += 1
        messages.success(request, '点赞成功')
    
    post.save(update_fields=['likes'])
    
    # 如果是 AJAX 请求，返回 JSON
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        from django.http import JsonResponse
        return JsonResponse({
            'liked': created,
            'likes_count': post.likes
        })
    
    return redirect('post_detail', post_id=post.id)

@login_required
def toggle_collection(request, post_id):
    """收藏/取消收藏"""
    post = get_object_or_404(Post, id=post_id)
    
    collection, created = PostCollection.objects.get_or_create(
        post=post,
        user=request.user
    )
    
    if not created:
        # 如果已存在，则删除（取消收藏）
        collection.delete()
        post.collections -= 1
        messages.info(request, '已取消收藏')
    else:
        post.collections += 1
        messages.success(request, '收藏成功')
    
    post.save(update_fields=['collections'])
    
    # 如果是 AJAX 请求，返回 JSON
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        from django.http import JsonResponse
        return JsonResponse({
            'collected': created,
            'collections_count': post.collections
        })
    
    return redirect('post_detail', post_id=post.id)

@login_required
def create_comment(request, post_id):
    """发表评论"""
    post = get_object_or_404(Post, id=post_id)
    
    if request.method == 'POST':
        content = request.POST.get('content')
        parent_id = request.POST.get('parent_id')
        
        if not content:
            messages.error(request, '评论内容不能为空')
            return redirect('post_detail', post_id=post.id)
        
        parent = None
        if parent_id:
            parent = get_object_or_404(Comment, id=parent_id)
        
        comment = Comment.objects.create(
            post=post,
            user=request.user,
            parent=parent,
            content=content
        )
        
        # 更新帖子的评论数
        post.comments_count = post.comments.filter(is_deleted=False).count()
        post.save(update_fields=['comments_count'])
        
        messages.success(request, '评论成功！')
    
    return redirect('post_detail', post_id=post.id)

@login_required
def delete_comment(request, comment_id):
    """删除评论（软删除）"""
    comment = get_object_or_404(Comment, id=comment_id)
    
    # 只有评论作者或管理员可以删除
    if request.user == comment.user or request.user.is_staff:
        comment.is_deleted = True
        comment.save(update_fields=['is_deleted'])
        
        # 更新帖子的评论数
        post = comment.post
        post.comments_count = post.comments.filter(is_deleted=False).count()
        post.save(update_fields=['comments_count'])
        
        messages.success(request, '评论已删除')
    else:
        messages.error(request, '无权删除此评论')
    
    return redirect('post_detail', post_id=post.id)

@login_required
def report_content(request):
    """举报内容"""
    if request.method == 'POST':
        report_type = request.POST.get('report_type')
        reason = request.POST.get('reason')
        post_id = request.POST.get('post_id')
        comment_id = request.POST.get('comment_id')
        
        post = None
        comment = None
        
        if post_id:
            post = get_object_or_404(Post, id=post_id)
        if comment_id:
            comment = get_object_or_404(Comment, id=comment_id)
        
        if not report_type or not reason:
            messages.error(request, '请选择举报类型并填写原因')
            return redirect('community_posts')
        
        Report.objects.create(
            reporter=request.user,
            post=post,
            comment=comment,
            report_type=report_type,
            reason=reason,
            status='pending'
        )
        
        messages.success(request, '举报已提交，我们会尽快处理')
    
    return redirect('community_posts')

def topics_list(request):
    """话题列表页"""
    topics = Topic.objects.annotate(post_count=Count('posts')).order_by('-sort_order', '-post_count')
    return render(request, 'community/topics.html', {'topics': topics})
