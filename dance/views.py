from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.forms import AuthenticationForm, UserCreationForm
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from django.db.models import Case, When
from django import forms
from django.contrib import messages
from .models import UserProfile

class RegisterForm(UserCreationForm):
    # 添加额外字段
    email = forms.EmailField(required=False, label="邮箱")
    
    class Meta:
        model = User
        fields = ["username", "email", "password1", "password2"]

def home(request):
    """网站首页 - 展示用户所在地区非遗舞蹈、全国热门资讯与平台介绍"""
    # 获取用户选择的地区（从 GET 参数或 session）
    selected_region_id = request.GET.get('region')
    
    # 调试信息
    print(f"\n=== Home View Debug ===")
    print(f"GET parameters: {request.GET}")
    print(f"'region' in GET: {'region' in request.GET}")
    print(f"GET.get('region'): '{request.GET.get('region')}'")
    print(f"Session before: {request.session.get('selected_region_id')}")
    
    # 关键逻辑：只有当 GET 参数中存在 region 键时（包括空字符串），才更新 session
    # 这样可以区分"用户主动选择全部地区"和"首次访问没有选择"
    if 'region' in request.GET:
        selected_region_id = request.GET.get('region')
        print(f"Using GET parameter: '{selected_region_id}'")
        # 更新 session
        if selected_region_id and selected_region_id.strip():
            # 有有效值，保存到 session
            request.session['selected_region_id'] = selected_region_id
            print(f"Saved to session: {selected_region_id}")
        else:
            # 值为空字符串或 None，清除 session 中的地区选择
            request.session.pop('selected_region_id', None)
            selected_region_id = None
            print("Cleared session (selected 'all regions')")
    else:
        # GET 参数中没有 region，从 session 中获取（保持之前的选择）
        selected_region_id = request.session.get('selected_region_id')
        print(f"Using session value: {selected_region_id}")
    
    print(f"Final selected_region_id: {selected_region_id}")
    print(f"========================\n")
    
    local_dances = []
    popular_dances = []
    hot_news = []
    regions = []
    selected_region = None
    
    from origin.models import DanceProject, Region
    from news.models import News
    from django.db.models import Count, Q
    
    # 获取所有省级地区用于选择
    regions = Region.objects.filter(level=1).order_by('name')
    
    # 处理地区选择（只影响热门舞蹈）
    # 注意：只有当 selected_region_id 来自 GET 参数时才更新 session
    if selected_region_id and 'region' in request.GET:
        try:
            selected_region = Region.objects.get(id=selected_region_id)
            # session 已经在上面更新过了，这里不需要重复操作
        except Region.DoesNotExist:
            selected_region_id = None
            selected_region = None
    elif selected_region_id:
        # selected_region_id 来自 session，直接使用
        try:
            selected_region = Region.objects.get(id=selected_region_id)
        except Region.DoesNotExist:
            selected_region_id = None
            selected_region = None
    
    # 最新非遗舞蹈 - 始终显示最新批次，不根据地区变化
    latest_batch = DanceProject.objects.values_list('announce_time', flat=True).distinct().order_by('-announce_time').first()
    if latest_batch:
        # 从最新批次中随机获取 6 个舞蹈
        local_dances = DanceProject.objects.filter(announce_time=latest_batch).order_by('?')[:6]
    else:
        # 如果没有批次数据，随机获取 6 个
        local_dances = DanceProject.objects.all().order_by('?')[:6]
    
    # 全国热门舞蹈（根据选择的地区显示）
    if selected_region_id:
        # 显示选定地区的舞蹈
        popular_dances = DanceProject.objects.filter(region_id=selected_region_id).order_by('-created_at')[:8]
    else:
        # 未选择地区，显示最新批次的舞蹈
        latest_batch = DanceProject.objects.values_list('announce_time', flat=True).distinct().order_by('-announce_time').first()
        if latest_batch:
            popular_dances = DanceProject.objects.filter(announce_time=latest_batch).order_by('-created_at')[:8]
        else:
            popular_dances = DanceProject.objects.all().order_by('-created_at')[:8]
    
    # 热门资讯（优先显示 is_hot=True 的）
    hot_news = News.objects.filter(is_hot=True).order_by('-created_at', '-views')[:6]
    
    # 统计数据
    total_projects = DanceProject.objects.count()
    
    # 按批次统计（公布时间）
    batch_stats = DanceProject.objects.values('announce_time').annotate(
        count=Count('id')
    ).order_by('announce_time')
    batch_count = batch_stats.count()
    
    # 按类别统计
    category_stats = DanceProject.objects.values('category').annotate(
        count=Count('id')
    ).order_by('-count')
    
    # 按类型统计
    type_stats = DanceProject.objects.values('dance_type').annotate(
        count=Count('id')
    )
    
    # 按项目类型统计（新增项目/扩展项目）
    project_type_stats = DanceProject.objects.exclude(project_type='').values('project_type').annotate(
        count=Count('id')
    )
    
    context = {
        'regions': regions,
        'selected_region': selected_region,
        'local_dances': local_dances,
        'popular_dances': popular_dances,
        'hot_news': hot_news,
        'total_projects': total_projects,
        'batch_count': batch_count,
        'category_stats': category_stats,
        'type_stats': type_stats,
        'project_type_stats': project_type_stats,
    }
    
    return render(request, 'dance/home.html', context)

def login_view(request):
    """用户登录"""
    if request.user.is_authenticated:
        # 如果已登录，检查是否是超级管理员
        if request.user.is_staff:
            return redirect('admin:index')
        return redirect('home')

    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(username=username, password=password)
            if user is not None:
                login(request, user)
                # 判断用户权限，超级管理员跳转到 admin 后台
                if user.is_staff:
                    return redirect('admin:index')
                # 普通用户跳转到首页
                return redirect('home')
            else:
                messages.error(request, '用户名或密码错误')
        else:
            messages.error(request, '用户名或密码错误')
    else:
        form = AuthenticationForm()

    return render(request, 'dance/login.html', {'form': form})

def register_view(request):
    """用户注册 - 简化版，无需选择地区"""
    if request.user.is_authenticated:
        return redirect('home')

    if request.method == 'POST':
        form = RegisterForm(request.POST)
        if form.is_valid():
            # 创建用户
            user = form.save()
            
            # 自动登录
            from django.contrib.auth import login
            login(request, user)
            # 注册成功后，直接重定向到首页
            return redirect('home')
        else:
            print(f"\n=== 表单验证失败 ===")
            print(form.errors)
    else:
        form = RegisterForm()

    return render(request, 'dance/register.html', {'form': form})

def logout_view(request):
    """用户登出"""
    logout(request)
    messages.info(request, '您已成功退出登录')
    return redirect('home')

def news_list(request):
    """新闻资讯列表页"""
    from news.models import News
    from django.db.models import Q
    
    # 获取筛选参数
    category = request.GET.get('category', '')
    keyword = request.GET.get('keyword', '').strip()
    
    # 构建查询 - 移除 is_hot 限制，显示所有新闻
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

def dance_origin_list(request):
    """舞蹈起源列表页 - 地图形式呈现"""
    from origin.models import DanceProject, Region
    from django.db.models import Q, Count
    
    # 获取所有舞蹈项目，用于地图展示
    dances = DanceProject.objects.all()
    
    # 统计数据（仅用于地图显示）
    total_results = dances.count()
    
    # 为地图准备数据 - 按地区统计
    region_data = {}
    for dance in dances:
        if dance.region_id:
            region_name = dance.region.name if dance.region else '未知'
            if region_name not in region_data:
                region_data[region_name] = {
                    'count': 0,
                    'dances': []
                }
            region_data[region_name]['count'] += 1
            region_data[region_name]['dances'].append({
                'id': dance.id,
                'name': dance.name,
                'project_code': dance.project_code,
                'dance_type': dance.get_dance_type_display(),
                'category': dance.category,
                'level': dance.level,
                'image': dance.images.url if dance.images else '',
            })
    
    # 为地图准备 JSON 数据
    regions_data = []
    for region_name, data in region_data.items():
        regions_data.append({
            'name': region_name,
            'count': data['count'],
        })
    
    import json
    context = {
        'total_results': total_results,
        'region_data': region_data,
        'regions_data': json.dumps(regions_data),
    }
    return render(request, 'origin/dance_origin_list.html', context)

def dance_project_list(request):
    """舞蹈项目列表页 - 带筛选功能"""
    from origin.models import DanceProject, Region
    from django.db.models import Q, Count
    
    # 获取搜索参数
    region_id = request.GET.get('region', '')
    announce_time = request.GET.get('announce_time', '')
    category = request.GET.get('category', '')
    dance_type = request.GET.get('dance_type', '')
    keyword = request.GET.get('keyword', '')
    
    dances = DanceProject.objects.all()
    
    # 应用筛选条件
    if region_id:
        # 检查是 ID 还是地区名称
        if region_id.isdigit():
            # 是数字，按 ID 筛选
            dances = dances.filter(region_id=region_id)
        else:
            # 是地区名称，按名称筛选
            try:
                region = Region.objects.get(name=region_id)
                dances = dances.filter(region=region)
            except Region.DoesNotExist:
                pass
    if announce_time:
        dances = dances.filter(announce_time=announce_time)
    if category:
        dances = dances.filter(category=category)
    if dance_type:
        dances = dances.filter(dance_type=dance_type)
    if keyword:
        # 关键词搜索：项目名称或项目编号
        dances = dances.filter(
            Q(name__icontains=keyword) | 
            Q(project_code__icontains=keyword)
        )
    
    regions = Region.objects.filter(level=1).order_by('name')
    
    # 统计数据（用于筛选器选项）
    batch_stats = DanceProject.objects.values('announce_time').annotate(
        count=Count('id')
    ).order_by('announce_time')
    
    category_stats = DanceProject.objects.values('category').annotate(
        count=Count('id')
    ).order_by('-count')
    
    type_stats = DanceProject.objects.values('dance_type').annotate(
        count=Count('id')
    )
    
    context = {
        'dances': dances,
        'regions': regions,
        'current_region': region_id,
        'current_announce_time': announce_time,
        'current_category': category,
        'current_type': dance_type,
        'current_keyword': keyword,
        'total_results': dances.count(),
        'batch_stats': batch_stats,
        'category_stats': category_stats,
        'type_stats': type_stats,
    }
    return render(request, 'origin/dance_list.html', context)

def project_detail(request, project_id):
    """非遗舞蹈项目详情页"""
    from origin.models import DanceProject, Inheritor, RelatedProject
    from news.models import News
    
    # 使用项目ID精确查找，避免编号重复导致的问题
    try:
        project = DanceProject.objects.select_related('region').get(id=project_id)
    except DanceProject.DoesNotExist:
        from django.http import Http404
        raise Http404("项目不存在")
    
    # 获取传承人：使用项目名称匹配（而不是项目编号）
    # 因为同一编号可能对应多个项目，但项目名称是唯一的
    inheritors = Inheritor.objects.filter(project_name=project.name)
    
    # 获取相关项目
    related_projects = RelatedProject.objects.filter(main_project=project)
    
    # 获取相关资讯
    news_list = News.objects.filter(dance_project=project)[:6]
    
    # 增加浏览量
    project.views += 1
    project.save(update_fields=['views'])
    
    context = {
        'project': project,
        'inheritors': inheritors,
        'related_projects': related_projects,
        'news_list': news_list,
    }
    
    return render(request, 'origin/project_detail.html', context)

def knowledge_map(request):
    """知识图谱页面 - 即将上线"""
    # TODO: 未来实现知识图谱功能
    return render(request, 'knowledge/knowledge_map.html')

def quiz_list(request):
    """答题闯关页面 - 即将上线"""
    # TODO: 未来实现答题闯关功能
    return render(request, 'quiz/quiz_list.html')

def community_posts(request):
    """交流社区页面 - 即将上线"""
    # TODO: 未来实现交流社区功能
    return render(request, 'community/community_posts.html')

def profile(request):
    """个人主页 - 显示用户的统计数据概览"""
    from dance.models import UserProfile
    from community.models import Post, PostLike, PostCollection, Comment
    from news.models import UserInteraction, News
    
    if not request.user.is_authenticated:
        return redirect('login')
    
    try:
        user_profile = UserProfile.objects.get(user=request.user)
    except UserProfile.DoesNotExist:
        user_profile = None
    
    # 帖子互动统计
    total_likes = PostLike.objects.filter(user=request.user).count()
    total_collections = PostCollection.objects.filter(user=request.user).count()
    total_comments = Comment.objects.filter(user=request.user, is_deleted=False).count()
    total_posts = Post.objects.filter(author=request.user, status='published').count()
    
    # 资讯互动统计
    news_liked_count = UserInteraction.objects.filter(user=request.user, interaction_type='like').count()
    news_collected_count = UserInteraction.objects.filter(user=request.user, interaction_type='collect').count()
    
    # 获取最近浏览的资讯（从 session 中获取 ID）
    visited_news_ids = request.session.get('visited_news', [])[:3]
    recent_news = News.objects.filter(id__in=visited_news_ids).select_related('author', 'dance_project').order_by('-created_at')[:3]
    # 按浏览顺序排序
    recent_news = sorted(recent_news, key=lambda x: visited_news_ids.index(x.id) if x.id in visited_news_ids else 999)
    
    # 获取最近浏览的帖子（从 session 中获取 ID）
    visited_posts_ids = request.session.get('visited_posts_home', [])[:3]
    recent_posts_browsed = Post.objects.filter(id__in=visited_posts_ids).select_related('author', 'topic').order_by('-created_at')[:3]
    # 按浏览顺序排序
    recent_posts_browsed = sorted(recent_posts_browsed, key=lambda x: visited_posts_ids.index(x.id) if x.id in visited_posts_ids else 999)
    
    # 保留原有的最近发帖和评论（用于备用）
    recent_posts_created = Post.objects.filter(author=request.user, status='published').select_related('topic').order_by('-created_at')[:5]
    recent_comments = Comment.objects.filter(user=request.user, is_deleted=False).select_related('post').order_by('-created_at')[:3]
    
    context = {
        'user_profile': user_profile,
        'total_likes': total_likes,
        'total_collections': total_collections,
        'total_comments': total_comments,
        'total_posts': total_posts,
        'news_liked_count': news_liked_count,
        'news_collected_count': news_collected_count,
        'recent_news': recent_news,
        'recent_posts_browsed': recent_posts_browsed,
        'recent_posts_created': recent_posts_created,
        'recent_comments': recent_comments,
    }
    return render(request, 'community/profile.html', context)

@login_required
def user_liked_posts(request):
    """用户点赞的帖子列表"""
    from community.models import Post, PostLike
    
    # 直接使用 JOIN 查询，按点赞时间倒序
    liked_posts = Post.objects.filter(
        postlike__user=request.user
    ).select_related('author', 'topic').order_by('-postlike__created_at').distinct()
    
    total_count = liked_posts.count()
    
    context = {
        'page_title': '我的点赞',
        'posts': liked_posts,
        'total_count': total_count,
        'icon': 'fa-heart',
        'color': '#E74C3C',
    }
    return render(request, 'community/user_interactions.html', context)

@login_required
def user_collected_posts(request):
    """用户收藏的帖子列表"""
    from community.models import Post, PostCollection
    
    # 直接使用 JOIN 查询，按收藏时间倒序
    collected_posts = Post.objects.filter(
        postcollection__user=request.user
    ).select_related('author', 'topic').order_by('-postcollection__created_at').distinct()
    
    total_count = collected_posts.count()
    
    context = {
        'page_title': '我的收藏',
        'posts': collected_posts,
        'total_count': total_count,
        'icon': 'fa-star',
        'color': '#F39C12',
    }
    return render(request, 'community/user_interactions.html', context)

@login_required
def user_comments(request):
    """用户的评论列表"""
    from community.models import Comment
    
    comments = Comment.objects.filter(
        user=request.user,
        is_deleted=False
    ).select_related('post', 'parent').order_by('-created_at')
    
    total_count = comments.count()
    
    context = {
        'page_title': '我的评论',
        'comments': comments,
        'total_count': total_count,
        'icon': 'fa-comments',
        'color': '#3498DB',
    }
    return render(request, 'community/user_comments.html', context)

@login_required
def user_posts(request):
    """用户发布的帖子列表（排除草稿箱）"""
    from community.models import Post
    
    posts = Post.objects.filter(
        author=request.user,
        status='published'
    ).select_related('topic').order_by('-created_at')
    
    total_count = posts.count()
    
    context = {
        'page_title': '我的帖子',
        'posts': posts,
        'total_count': total_count,
        'icon': 'fa-file-alt',
        'color': '#2ECC71',
    }
    return render(request, 'community/user_interactions.html', context)

@login_required
def user_liked_news(request):
    """用户点赞的资讯列表"""
    from news.models import News, UserInteraction
    
    news_list = News.objects.filter(
        userinteraction__user=request.user,
        userinteraction__interaction_type='like'
    ).select_related('author', 'dance_project').order_by('-userinteraction__created_at').distinct()
    
    total_count = news_list.count()
    
    context = {
        'page_title': '我点赞的资讯',
        'news_list': news_list,
        'total_count': total_count,
        'icon': 'fa-heart',
        'color': '#E74C3C',
    }
    return render(request, 'news/user_news_interactions.html', context)

@login_required
def user_collected_news(request):
    """用户收藏的资讯列表"""
    from news.models import News, UserInteraction
    
    news_list = News.objects.filter(
        userinteraction__user=request.user,
        userinteraction__interaction_type='collect'
    ).select_related('author', 'dance_project').order_by('-userinteraction__created_at').distinct()
    
    total_count = news_list.count()
    
    context = {
        'page_title': '我收藏的资讯',
        'news_list': news_list,
        'total_count': total_count,
        'icon': 'fa-star',
        'color': '#F39C12',
    }
    return render(request, 'news/user_news_interactions.html', context)

@login_required
def edit_avatar(request):
    """修改个人头像"""
    from .models import UserProfile
    from django.core.files.storage import default_storage
    
    user_profile = UserProfile.objects.get_or_create(user=request.user)[0]
    
    if request.method == 'POST':
        avatar = request.FILES.get('avatar')
        
        if avatar:
            # 删除旧头像
            if user_profile.avatar and default_storage.exists(user_profile.avatar.name):
                default_storage.delete(user_profile.avatar.name)
            
            # 保存新头像
            user_profile.avatar = avatar
            user_profile.save(update_fields=['avatar'])
            
            messages.success(request, '头像更新成功！')
            return redirect('profile')
        else:
            messages.error(request, '请选择要上传的图片')
    
    return render(request, 'community/edit_avatar.html', {'user_profile': user_profile})


@login_required
def edit_profile(request):
    """编辑个人资料（技能等级、偏好舞种等）"""
    from .models import UserProfile
    
    user_profile = UserProfile.objects.get_or_create(user=request.user)[0]
    
    # 可选的舞种列表
    dance_type_choices = [
        '古典舞蹈', '民间舞蹈', '民族舞蹈', '传统舞蹈',
        '现代舞', '芭蕾舞', '街舞', '国标舞'
    ]
    
    if request.method == 'POST':
        # 获取表单数据
        skill_level = request.POST.get('skill_level', 1)
        learning_goal = request.POST.get('learning_goal', '')
        available_time = request.POST.get('available_time_per_week', 5)
        
        # 获取偏好舞种（复选框）
        preferred_types = request.POST.getlist('preferred_dance_types')
        
        # 验证数据
        try:
            skill_level = int(skill_level)
            if skill_level < 1 or skill_level > 5:
                skill_level = 1
        except (ValueError, TypeError):
            skill_level = 1
        
        try:
            available_time = int(available_time)
            if available_time < 1 or available_time > 50:
                available_time = 5
        except (ValueError, TypeError):
            available_time = 5
        
        # 更新用户资料
        user_profile.skill_level = skill_level
        user_profile.learning_goal = learning_goal[:200]  # 限制长度
        user_profile.available_time_per_week = available_time
        user_profile.preferred_dance_types = preferred_types
        user_profile.save()
        
        messages.success(request, '个人资料更新成功！推荐结果已刷新')
        return redirect('knowledge:recommendations')
    
    context = {
        'user_profile': user_profile,
        'dance_type_choices': dance_type_choices,
    }
    return render(request, 'community/edit_profile.html', context)
