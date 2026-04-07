from django.shortcuts import render, get_object_or_404
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.conf import settings
from .models import DanceProject, ActionModule, SpecificMove, MoveAttribute, LearningResource, KnowledgePoint
import json
import requests

def knowledge_map(request):
    """知识图谱页面"""
    # 获取所有舞蹈项目
    dance_projects = DanceProject.objects.all().order_by('name')
    
    context = {
        'dance_projects': dance_projects,
    }
    return render(request, 'knowledge/knowledge_map.html', context)


def get_project_knowledge_graph(request, project_id):
    """获取指定项目的知识图谱数据"""
    try:
        project = DanceProject.objects.get(id=project_id)
        
        # 构建知识图谱数据
        graph_data = {
            'project': {
                'id': project.id,
                'name': project.name,
                'description': project.description,
                'category': project.category,
                'difficulty_level': project.difficulty_level,
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
    
    except DanceProject.DoesNotExist:
        return JsonResponse({
            'success': False,
            'error': '项目不存在'
        }, status=404)


def generate_learning_path(request, project_id):
    """生成个性化学习路径"""
    try:
        project = DanceProject.objects.get(id=project_id)
        
        # 根据难度等级生成学习路径
        modules = ActionModule.objects.filter(dance_project=project).order_by('order_index')
        
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
