from django.shortcuts import render, get_object_or_404, redirect
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.decorators import login_required
from django.conf import settings
from .models import DanceProject, ActionModule, SpecificMove, MoveAttribute, LearningResource, KnowledgePoint, UserLearningProgress
import json
import requests

def knowledge_map(request):
    """知识图谱页面"""
    from origin.models import DanceProject as OriginDanceProject
    # 直接使用 origin 的舞蹈项目数据，确保列表不为空
    dance_projects = []
    for kp in OriginDanceProject.objects.all().order_by('name'):
        dance_projects.append({
            'id': kp.id,
            'name': kp.name,
            'image': kp.images.url if kp.images else None,
        })
    
    context = {
        'dance_projects': dance_projects,
    }
    return render(request, 'knowledge/knowledge_map.html', context)


def get_project_knowledge_graph(request, project_id):
    """获取指定项目的知识图谱数据"""
    from origin.models import DanceProject as OriginDanceProject
    try:
        # 先从 origin 表查找（因为前端传的是 origin 表的 ID）
        try:
            origin_project = OriginDanceProject.objects.get(id=project_id)
            project_name = origin_project.name
        except OriginDanceProject.DoesNotExist:
            # 如果 origin 表找不到，尝试从 knowledge 表按 ID 查找
            try:
                project = DanceProject.objects.get(id=project_id)
                project_name = project.name
            except DanceProject.DoesNotExist:
                return JsonResponse({
                    'success': False,
                    'error': '项目不存在'
                }, status=404)
        
        # 通过项目名称在 knowledge 表中查找对应的知识图谱数据
        try:
            project = DanceProject.objects.get(name=project_name)
        except DanceProject.DoesNotExist:
            return JsonResponse({
                'success': False,
                'error': f'未找到「{project_name}」的知识图谱数据'
            }, status=404)
        
        # 获取 origin 项目用于图片展示
        image_url = origin_project.images.url if origin_project and origin_project.images else None
        
        # 构建知识图谱数据
        graph_data = {
            'project': {
                'id': project.id,
                'name': project.name,
                'description': getattr(project, 'description', ''),
                'category': getattr(project, 'category', '传统舞蹈'),
                'difficulty_level': getattr(project, 'difficulty_level', 1),
                'image': image_url,
                # 从 origin 项目获取批次和年份
                'announce_batch': getattr(origin_project, 'announce_batch', ''),
                'announce_time': getattr(origin_project, 'announce_time', ''),
            },
            'modules': []
        }
        
        # 获取所有动作模块
        modules = ActionModule.objects.filter(dance_project=project).order_by('order_index')
        
        for module in modules:
            module_data = {
                'id': module.id,
                'name': module.name,
                'description': module.description,
                'order_index': module.order_index,
                'moves': []
            }
            
            # 获取该模块下的所有招式
            moves = SpecificMove.objects.filter(action_module=module).order_by('order_index')
            
            for move in moves:
                move_data = {
                    'id': move.id,
                    'name': move.name,
                    'description': move.description,
                    'difficulty': move.difficulty,
                    'duration': move.duration,
                    'attributes': None,
                    'resources': [],
                    'knowledge_points': []
                }
                
                # 获取动作属性
                try:
                    attr = MoveAttribute.objects.get(specific_move=move)
                    move_data['attributes'] = {
                        'force_parts': attr.force_parts,
                        'common_mistakes': attr.common_mistakes,
                        'key_points': attr.key_points,
                        'precautions': attr.precautions,
                    }
                except MoveAttribute.DoesNotExist:
                    pass
                
                # 获取学习资源
                resources = LearningResource.objects.filter(specific_move=move).order_by('order_index')
                for resource in resources:
                    move_data['resources'].append({
                        'id': resource.id,
                        'type': resource.resource_type,
                        'title': resource.title,
                        'url': resource.url,
                        'thumbnail': resource.thumbnail.url if resource.thumbnail else None,
                        'duration': resource.duration,
                    })
                
                # 获取知识点标签
                points = KnowledgePoint.objects.filter(specific_move=move)
                for point in points:
                    move_data['knowledge_points'].append({
                        'id': point.id,
                        'name': point.name,
                        'description': point.description,
                        'category': point.category,
                        'importance_level': point.importance_level,
                    })
                
                module_data['moves'].append(move_data)
            
            graph_data['modules'].append(module_data)
        
        return JsonResponse({
            'success': True,
            'data': graph_data
        })
    
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': f'加载失败：{str(e)}'
        }, status=500)


def generate_learning_path(request, project_id):
    """生成个性化学习路径"""
    from origin.models import DanceProject as OriginDanceProject
    try:
        # 兼容查找
        try:
            project = DanceProject.objects.get(id=project_id)
        except DanceProject.DoesNotExist:
            project = OriginDanceProject.objects.get(id=project_id)
        
        # 根据难度等级生成学习路径
        modules = ActionModule.objects.filter(dance_project_id=project.id).order_by('order_index')
        
        learning_path = {
            'project_name': project.name,
            'total_modules': modules.count(),
            'estimated_time': 0,
            'stages': []
        }
        
        stage_num = 1
        for module in modules:
            moves = SpecificMove.objects.filter(action_module=module).order_by('difficulty', 'order_index')
            
            stage = {
                'stage': stage_num,
                'module_name': module.name,
                'module_description': module.description,
                'moves': [],
                'estimated_hours': 0
            }
            
            total_duration = 0
            for move in moves:
                move_info = {
                    'name': move.name,
                    'difficulty': move.difficulty,
                    'duration_minutes': move.duration / 60,
                    'suggested_practice_days': max(3, move.difficulty),  # 根据难度建议练习天数
                }
                stage['moves'].append(move_info)
                total_duration += move.duration
            
            # 计算该阶段预计学习时长（小时）
            stage['estimated_hours'] = round(total_duration / 3600 * stage['moves'][0]['suggested_practice_days'] if stage['moves'] else 0, 1)
            learning_path['estimated_time'] += stage['estimated_hours']
            
            learning_path['stages'].append(stage)
            stage_num += 1
        
        return JsonResponse({
            'success': True,
            'data': learning_path
        })
    
    except DanceProject.DoesNotExist:
        return JsonResponse({
            'success': False,
            'error': '项目不存在'
        }, status=404)


def ai_chat(request):
    """AI智能问答页面"""
    return render(request, 'knowledge/ai_chat.html')


@csrf_exempt
def chat_with_ai(request):
    """与文心一言AI对话"""
    if request.method != 'POST':
        return JsonResponse({'success': False, 'error': '仅支持POST请求'}, status=405)
    
    try:
        data = json.loads(request.body)
        user_message = data.get('message', '')
        context = data.get('context', '')  # 可选的上下文信息
        
        if not user_message:
            return JsonResponse({'success': False, 'error': '消息不能为空'}, status=400)
        
        # 调用文心一言API
        ai_response = call_wenxin_api(user_message, context)
        
        return JsonResponse({
            'success': True,
            'response': ai_response
        })
    
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': f'AI服务异常: {str(e)}'
        }, status=500)


def call_wenxin_api(message, context=''):
    """
    调用通义千问API
    需要在 settings.py 中配置：
    QWEN_API_KEY = 'your_api_key'
    """
    # 获取API密钥
    api_key = getattr(settings, 'QWEN_API_KEY', '')
    
    if not api_key:
        # 如果没有配置API密钥，返回模拟响应
        return generate_mock_response(message)
    
    try:
        from dashscope import Generation
        import dashscope
        
        # 设置API密钥
        dashscope.api_key = api_key
        
        # 构建系统提示词
        system_prompt = """你是非遗传统舞蹈知识专家，专门回答关于中国非物质文化遗产舞蹈的问题。
请基于以下原则回答：
1. 提供准确、专业的舞蹈知识
2. 结合历史文化背景进行解释
3. 语言通俗易懂，适合学习者理解
4. 如果问题超出你的知识范围，请诚实说明"""
        
        # 构建用户消息
        user_message = f"{system_prompt}\n\n用户问题：{message}"
        if context:
            user_message += f"\n\n相关背景：{context}"
        
        # 调用通义千问API
        response = Generation.call(
            model='qwen-plus-latest',  # 与阿里云百炼应用配置一致
            messages=[
                {'role': 'user', 'content': user_message}
            ],
            temperature=0.7,
            top_p=0.8,
        )
        
        if response.status_code == 200:
            return response.output.text
        else:
            return f"API调用失败：{response.message}"
    
    except ImportError:
        # 如果没有安装dashscope库，返回模拟响应
        return generate_mock_response(message)
    except Exception as e:
        return f"AI服务异常：{str(e)}"


def generate_mock_response(message):
    """生成模拟响应（当API未配置时）"""
    # 这里可以根据关键词提供一些基础回复
    if '安塞腰鼓' in message:
        return "安塞腰鼓是陕西省延安市安塞区的传统舞蹈，属于国家级非物质文化遗产。它以豪迈奔放、气势磅礴著称，主要特点是：\n\n1. **基本技法**：包括单槌点击、双槌连击、花槌滚击等\n2. **跳跃动作**：蹬腿跳跃、转身飞槌等高难度技巧\n3. **队形阵法**：四门斗底阵、双龙出海阵等集体表演形式\n\n安塞腰鼓体现了黄土高原人民的豪放性格和深厚的文化底蕴。"
    
    elif '孔雀舞' in message:
        return "孔雀舞是傣族最具代表性的传统舞蹈，主要流传于云南西双版纳地区。其特点包括：\n\n1. **手型特色**：孔雀手型（拇指食指捏圆，三指展开）\n2. **身段韵律**：三道弯体态，展现S曲线美感\n3. **动作模仿**：展翅、饮水、梳理羽毛等孔雀姿态\n\n孔雀舞象征着吉祥、幸福和美好，是傣族文化的重要载体。"
    
    else:
        return f"感谢您的提问！\n\n关于「{message}」，建议您：\n\n1. 在知识图谱中选择具体的舞蹈项目查看详细招式\n2. 浏览学习资源中的教学视频\n3. 参考相关知识点的详细说明\n\n如需更专业的解答，请配置文心一言API密钥以获得AI智能回答。"


@login_required
def personalized_recommendations(request):
    """个性化推荐页面"""
    from .recommendation_engine import get_user_recommendations
    from origin.models import DanceProject as OriginDanceProject
    
    # 获取推荐列表
    recommendations = get_user_recommendations(request.user, limit=12)
    
    # 为每个推荐项添加 origin 项目 ID 和图片
    for rec in recommendations:
        project = rec['project']
        try:
            origin_project = OriginDanceProject.objects.get(name=project.name)
            rec['origin_project_id'] = origin_project.id
            rec['project_image'] = origin_project.images.url if origin_project.images else None
        except OriginDanceProject.DoesNotExist:
            rec['origin_project_id'] = project.id  # 如果找不到，使用 knowledge 表的 ID
            rec['project_image'] = project.image.url if project.image else None
    
    context = {
        'recommendations': recommendations,
    }
    return render(request, 'knowledge/recommendations.html', context)


@login_required
def get_recommendations_api(request):
    """获取推荐列表API"""
    from .recommendation_engine import get_user_recommendations, RecommendationLog
    
    limit = int(request.GET.get('limit', 10))
    recommendations = get_user_recommendations(request.user, limit=limit)
    
    # 记录推荐日志
    for rec in recommendations:
        RecommendationLog.objects.create(
            user=request.user,
            recommended_project=rec['project'],
            recommendation_algorithm='content_based',
            recommendation_score=rec['score'],
            recommendation_reason='; '.join(rec['reasons'])
        )
    
    # 格式化返回数据
    data = []
    for rec in recommendations:
        project = rec['project']
        data.append({
            'id': project.id,
            'name': project.name,
            'category': project.category,
            'difficulty_level': project.difficulty_level,
            'description': project.description[:100] + '...' if len(project.description) > 100 else project.description,
            'image': project.image.url if project.image else None,
            'score': round(rec['score'], 2),
            'reasons': rec['reasons'][:3],  # 最多显示3个理由
        })
    
    return JsonResponse({
        'success': True,
        'data': data
    })


@login_required
def learning_path_view(request, project_id):
    """学习路径页面"""
    from .recommendation_engine import generate_learning_path_for_user
    from origin.models import DanceProject as OriginDanceProject
    
    # 获取项目信息
    try:
        origin_project = OriginDanceProject.objects.get(id=project_id)
        project_name = origin_project.name
    except OriginDanceProject.DoesNotExist:
        # 项目不存在，返回知识图谱页面并显示错误信息
        from django.contrib import messages
        messages.error(request, '找不到该舞蹈项目')
        return redirect('knowledge:knowledge_map')
    
    # 生成学习路径
    learning_path = generate_learning_path_for_user(request.user, project_id)
    
    if not learning_path:
        # 没有学习路径数据，返回知识图谱页面
        from django.contrib import messages
        messages.warning(request, f'「{project_name}」暂无学习路径数据')
        return redirect('knowledge:knowledge_map')
    
    context = {
        'learning_path': learning_path,
        'origin_project': origin_project,
    }
    return render(request, 'knowledge/learning_path.html', context)


@login_required
def my_progress(request):
    """我的学习进度页面"""
    from origin.models import DanceProject as OriginDanceProject
    
    # 获取用户所有学习进度，按项目分组
    progress_records = UserLearningProgress.objects.filter(
        user=request.user
    ).select_related(
        'dance_project',
        'specific_move',
        'specific_move__action_module'
    ).order_by('-updated_at')
    
    # 按项目分组统计
    project_progress = {}
    for record in progress_records:
        project = record.dance_project
        project_id = project.id
        
        if project_id not in project_progress:
            project_progress[project_id] = {
                'project': project,
                'total_moves': 0,
                'not_started': 0,
                'learning': 0,
                'completed': 0,
                'mastered': 0,
                'avg_proficiency': 0,
                'proficiency_sum': 0,
            }
        
        pp = project_progress[project_id]
        pp['total_moves'] += 1
        pp[record.status] += 1
        pp['proficiency_sum'] += record.proficiency_score
    
    # 计算平均熟练度和完成度
    for pp in project_progress.values():
        if pp['total_moves'] > 0:
            pp['avg_proficiency'] = pp['proficiency_sum'] / pp['total_moves']
            # 完成度 = (已完成 + 已掌握) / 总数
            pp['completion_rate'] = (pp['completed'] + pp['mastered']) / pp['total_moves'] * 100
            # 学习进度 = (学习中 + 已完成 + 已掌握) / 总数（用于判断是否已开始学习）
            pp['learning_progress_rate'] = (pp['learning'] + pp['completed'] + pp['mastered']) / pp['total_moves'] * 100
        else:
            pp['completion_rate'] = 0
            pp['learning_progress_rate'] = 0
    
    # 转换为列表并排序（按完成度降序）
    # 过滤掉完全没有学习进度的项目（所有招式都是未开始状态）
    progress_list = sorted(
        [pp for pp in project_progress.values() if pp['learning_progress_rate'] > 0],
        key=lambda x: x['completion_rate'],
        reverse=True
    )
    
    # 总体统计
    total_projects = len(progress_list)
    total_moves = sum(pp['total_moves'] for pp in progress_list)
    mastered_projects = sum(1 for pp in progress_list if pp['completion_rate'] == 100)
    avg_completion = sum(pp['completion_rate'] for pp in progress_list) / total_projects if total_projects > 0 else 0
    
    context = {
        'progress_list': progress_list,
        'total_projects': total_projects,
        'total_moves': total_moves,
        'mastered_projects': mastered_projects,
        'avg_completion': avg_completion,
    }
    return render(request, 'knowledge/my_progress.html', context)


@login_required
@csrf_exempt
def update_learning_progress(request, move_id):
    """
    更新招式学习进度（自动根据学习时间计算熟练度）
    POST /knowledge/api/update-progress/<move_id>/
    {
        "practice_time": 秒数（必填）
    }
    """
    if request.method != 'POST':
        return JsonResponse({'success': False, 'error': '仅支持POST请求'}, status=405)
    
    try:
        move = SpecificMove.objects.get(id=move_id)
        data = json.loads(request.body)
        practice_time = data.get('practice_time', 0)
        
        if practice_time <= 0:
            return JsonResponse({'success': False, 'error': '练习时间必须大于0'}, status=400)
        
        # 获取或创建学习进度记录
        progress, created = UserLearningProgress.objects.get_or_create(
            user=request.user,
            specific_move=move,
            defaults={
                'dance_project': move.action_module.dance_project,
                'status': 'learning',
                'proficiency_score': 0,
                'practice_count': 1,
                'total_practice_time': practice_time,
            }
        )
        
        if not created:
            # 累加练习时间和次数
            progress.total_practice_time += practice_time
            progress.practice_count += 1
        
        # 自动计算熟练度（基于总练习时长和招式难度）
        # 标准练习时长 = 招式duration * 难度系数 * 3（建议练习天数）
        estimated_standard_time = move.duration * move.difficulty * 3
        
        # 熟练度 = (总练习时间 / 标准时间) * 100，最高100
        proficiency = min((progress.total_practice_time / estimated_standard_time) * 100, 100)
        progress.proficiency_score = round(proficiency, 1)
        
        # 根据熟练度自动判断状态
        if proficiency >= 85:
            progress.status = 'mastered'
        elif proficiency >= 70:
            progress.status = 'completed'
        elif proficiency > 0:
            progress.status = 'learning'
        else:
            progress.status = 'not_started'
        
        progress.save()
        
        return JsonResponse({
            'success': True,
            'message': '进度已更新',
            'data': {
                'status': progress.status,
                'status_display': dict(UserLearningProgress.STATUS_CHOICES)[progress.status],
                'proficiency_score': progress.proficiency_score,
                'practice_count': progress.practice_count,
                'total_practice_time': progress.total_practice_time,
                'estimated_standard_time': estimated_standard_time,
            }
        })
    
    except SpecificMove.DoesNotExist:
        return JsonResponse({'success': False, 'error': '招式不存在'}, status=404)
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)}, status=500)
