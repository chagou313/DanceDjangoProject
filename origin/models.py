from django.db import models
from django.contrib.auth.models import User

class Region(models.Model):
    """地区表（用于地图检索）"""
    name = models.CharField(max_length=100, verbose_name="地区名称")
    code = models.CharField(max_length=20, unique=True, verbose_name="地区代码")
    parent = models.ForeignKey('self', on_delete=models.CASCADE, blank=True, null=True, related_name='children', verbose_name="父地区")
    level = models.IntegerField(default=1, verbose_name="地区级别（1-省，2-市，3-县）")
    coordinates = models.CharField(max_length=50, blank=True, verbose_name="地理坐标")
    
    class Meta:
        verbose_name = "地区"
        verbose_name_plural = "地区"
    
    def __str__(self):
        return self.name

class DanceProject(models.Model):
    """非遗舞蹈项目表（核心表）"""
    DANCE_TYPE_CHOICES = [
        ('classical', '古典舞'),
        ('folk', '民族舞'),
        ('traditional', '传统舞'),
        ('ethnic', '民间舞'),
    ]
    
    LEVEL_CHOICES = [
        ('national', '国家级'),
        ('provincial', '省级'),
        ('municipal', '市级'),
        ('county', '县级'),
    ]
    
    # 基本信息
    project_code = models.CharField(max_length=50, verbose_name="项目编号（如：Ⅲ-1）")
    name = models.CharField(max_length=200, verbose_name="项目名称")
    full_name = models.CharField(max_length=200, blank=True, verbose_name="全称（用于区分扩展项目）")
    dance_type = models.CharField(max_length=20, choices=DANCE_TYPE_CHOICES, default='traditional', verbose_name="舞蹈类型")
    category = models.CharField(max_length=50, default='传统舞蹈', verbose_name="类别")
    
    # 非遗信息
    level = models.CharField(max_length=20, choices=LEVEL_CHOICES, default='national', verbose_name="非遗级别")
    announce_batch = models.CharField(max_length=50, blank=True, verbose_name="公布批次（如：2006 年第一批）")
    announce_time = models.CharField(max_length=50, blank=True, verbose_name="公布时间")
    project_type = models.CharField(max_length=50, blank=True, verbose_name="项目类型（新增/扩展）")
    
    # 申报信息
    declare_region = models.CharField(max_length=200, blank=True, verbose_name="申报地区或单位")
    region = models.ForeignKey(Region, on_delete=models.SET_NULL, null=True, blank=True, verbose_name="所属地区")
    protection_unit = models.TextField(blank=True, verbose_name="保护单位")
    
    # 详细信息
    introduction = models.TextField(blank=True, verbose_name="项目简介")
    history = models.TextField(blank=True, verbose_name="历史渊源")
    characteristics = models.TextField(blank=True, verbose_name="艺术特色")
    folk_customs = models.TextField(blank=True, verbose_name="民俗背景")
    inheritance_system = models.TextField(blank=True, verbose_name="传承体系")
    
    # 多媒体
    images = models.ImageField(upload_to='origin/%Y%m%d/', blank=True, null=True, verbose_name="图片")
    video_url = models.URLField(blank=True, verbose_name="视频链接")
    
    # 统计
    views = models.IntegerField(default=0, verbose_name="浏览量")
    likes = models.IntegerField(default=0, verbose_name="点赞数")
    
    # 时间
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="创建时间")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="更新时间")
    
    class Meta:
        verbose_name = "非遗舞蹈项目"
        verbose_name_plural = "非遗舞蹈项目"
        ordering = ['project_code', 'name']
    
    def __str__(self):
        return f"{self.project_code} - {self.name}"

class Inheritor(models.Model):
    """传承人表"""
    GENDER_CHOICES = [
        ('male', '男'),
        ('female', '女'),
    ]
    
    inheritor_code = models.CharField(max_length=50, unique=True, verbose_name="传承人编号")
    name = models.CharField(max_length=100, verbose_name="姓名")
    gender = models.CharField(max_length=10, choices=GENDER_CHOICES, verbose_name="性别")
    birth_date = models.CharField(max_length=50, blank=True, verbose_name="出生日期")
    ethnicity = models.CharField(max_length=50, default='汉族', verbose_name="民族")
    category = models.CharField(max_length=50, default='传统舞蹈', verbose_name="类别")
    
    # 关联项目
    project_code = models.CharField(max_length=50, verbose_name="关联项目编号")
    project_name = models.CharField(max_length=200, verbose_name="关联项目名称")
    project = models.ForeignKey(DanceProject, on_delete=models.CASCADE, related_name='inheritors', verbose_name="关联舞蹈项目")
    
    # 申报信息
    declare_region = models.CharField(max_length=200, blank=True, verbose_name="申报地区或单位")
    
    # 详细信息
    introduction = models.TextField(blank=True, verbose_name="人物简介")
    achievements = models.TextField(blank=True, verbose_name="主要成就")
    inheritance_experience = models.TextField(blank=True, verbose_name="传承经历")
    honors = models.TextField(blank=True, verbose_name="荣誉称号")
    
    # 时间
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="创建时间")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="更新时间")
    
    class Meta:
        verbose_name = "传承人"
        verbose_name_plural = "传承人"
        ordering = ['project_code', 'name']
    
    def __str__(self):
        return f"{self.inheritor_code} - {self.name} ({self.project_name})"

class RelatedProject(models.Model):
    """相关项目表（同一舞蹈的不同地区变体）"""
    project_code = models.CharField(max_length=50, verbose_name="项目编号")
    name = models.CharField(max_length=200, verbose_name="项目名称")
    project_type = models.CharField(max_length=50, blank=True, verbose_name="类型")
    category = models.CharField(max_length=50, default='传统舞蹈', verbose_name="类别")
    declare_region = models.CharField(max_length=200, blank=True, verbose_name="申报地区或单位")
    
    # 关联到主项目
    main_project = models.ForeignKey(DanceProject, on_delete=models.CASCADE, related_name='related_projects', verbose_name="主项目")
    
    # 详细信息
    introduction = models.TextField(blank=True, verbose_name="简介")
    differences = models.TextField(blank=True, verbose_name="与主项目的区别")
    
    # 时间
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="创建时间")
    
    class Meta:
        verbose_name = "相关项目"
        verbose_name_plural = "相关项目"
        ordering = ['project_code', 'declare_region']
    
    def __str__(self):
        return f"{self.project_code} - {self.name} ({self.declare_region})"

class News(models.Model):
    """相关资讯表"""
    CATEGORY_CHOICES = [
        ('news', '新闻动态'),
        ('activity', '活动资讯'),
        ('policy', '政策法规'),
        ('research', '学术研究'),
        ('exhibition', '展览演出'),
    ]
    
    title = models.CharField(max_length=200, verbose_name="标题")
    category = models.CharField(max_length=20, choices=CATEGORY_CHOICES, default='news', verbose_name="资讯类型")
    
    # 关联舞蹈项目
    related_projects = models.ManyToManyField(DanceProject, blank=True, related_name='news_list', verbose_name="相关舞蹈项目")
    
    # 内容
    content = models.TextField(verbose_name="内容")
    source = models.CharField(max_length=200, blank=True, verbose_name="来源")
    author = models.CharField(max_length=100, blank=True, verbose_name="作者")
    publish_date = models.DateField(blank=True, null=True, verbose_name="发布日期")
    
    # 多媒体
    cover_image = models.ImageField(upload_to='news/%Y%m%d/', blank=True, null=True, verbose_name="封面图")
    
    # 统计
    views = models.IntegerField(default=0, verbose_name="浏览量")
    likes = models.IntegerField(default=0, verbose_name="点赞数")
    is_hot = models.BooleanField(default=False, verbose_name="是否热门")
    is_recommend = models.BooleanField(default=False, verbose_name="是否推荐")
    
    # 时间
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="创建时间")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="更新时间")
    
    class Meta:
        verbose_name = "相关资讯"
        verbose_name_plural = "相关资讯"
        ordering = ['-publish_date', '-created_at']
    
    def __str__(self):
        return self.title

class AcademicResearch(models.Model):
    """学术研究表"""
    TYPE_CHOICES = [
        ('paper', '论文'),
        ('book', '著作'),
        ('thesis', '学位论文'),
        ('report', '报告'),
        ('other', '其他'),
    ]
    
    title = models.CharField(max_length=300, verbose_name="标题")
    research_type = models.CharField(max_length=20, choices=TYPE_CHOICES, default='paper', verbose_name="研究类型")
    
    # 关联舞蹈项目
    related_projects = models.ManyToManyField(DanceProject, blank=True, related_name='academic_researches', verbose_name="相关舞蹈项目")
    
    # 作者信息
    author = models.CharField(max_length=200, verbose_name="作者")
    institution = models.CharField(max_length=200, blank=True, verbose_name="机构/学校")
    
    # 出版信息
    publisher = models.CharField(max_length=200, blank=True, verbose_name="发表刊物/出版社")
    publish_date = models.DateField(blank=True, null=True, verbose_name="发表时间")
    doi = models.CharField(max_length=100, blank=True, verbose_name="DOI 编号")
    
    # 内容
    abstract = models.TextField(blank=True, verbose_name="摘要")
    keywords = models.TextField(blank=True, verbose_name="关键词")
    download_link = models.URLField(blank=True, verbose_name="下载链接")
    
    # 时间
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="创建时间")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="更新时间")
    
    class Meta:
        verbose_name = "学术研究"
        verbose_name_plural = "学术研究"
        ordering = ['-publish_date', '-created_at']
    
    def __str__(self):
        return self.title
