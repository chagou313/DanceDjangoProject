from django.shortcuts import render, get_object_or_404, redirect
from django.http import JsonResponse, HttpResponseRedirect
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.decorators import login_required
from django.utils import timezone
from django.db.models import Q, Max
from .models import Level, Question, LevelQuestion, UserQuizRecord, UserAnswerDetail
from knowledge.models import KnowledgePoint
from origin.models import DanceProject
import json
import random


def quiz_list(request):
    """答题闯关首页 - 关卡选择"""
    # 检查用户是否登录
    if not request.user.is_authenticated:
        return render(request, 'quiz/quiz_list.html', {'require_login': True, 'levels': []})
    
    # 获取所有开启的关卡（直接使用QuerySet，不在视图中转换）
    levels = Level.objects.filter(is_active=True).order_by('order_index')
    
    # 调试：打印关卡信息
    print(f"[QUIZ DEBUG] Levels count: {levels.count()}")
    for level in levels:
        print(f"  - Level {level.id}: {level.name}")
    
    # 获取用户各关卡的最佳成绩
    user_progress = {}
    best_records = UserQuizRecord.objects.filter(
        user=request.user
    ).values('level_id').annotate(
        best_score=Max('score'),
        is_passed=Max('is_passed')
    )
    for record in best_records:
        user_progress[record['level_id']] = {
            'best_score': record['best_score'],
            'is_passed': record['is_passed'],
        }
    
    context = {
        'levels': levels,
        'user_progress': user_progress,
    }
    return render(request, 'quiz/quiz_list.html', context)


@login_required
def quiz_game(request, level_id):
    """答题游戏页面"""
    level = get_object_or_404(Level, id=level_id, is_active=True)
    
    # 检查是否有进行中的答题记录
    ongoing_record = UserQuizRecord.objects.filter(
        user=request.user,
        level=level,
        is_completed=False
    ).first()
    
    context = {
        'level': level,
        'ongoing_record': ongoing_record,
    }
    return render(request, 'quiz/quiz_game.html', context)


@login_required
@csrf_exempt
def start_quiz(request, level_id):
    """开始答题 - 创建答题记录并返回题目"""
    if request.method != 'POST':
        return JsonResponse({'success': False, 'error': '仅支持POST请求'}, status=405)
    
    level = get_object_or_404(Level, id=level_id, is_active=True)
    
    # 检查是否有进行中的答题记录
    ongoing_record = UserQuizRecord.objects.filter(
        user=request.user,
        level=level,
        is_completed=False
    ).first()
    
    if ongoing_record:
        # 继续之前的答题
        quiz_record = ongoing_record
        
        # 检查是否有答题详情，如果没有则创建（兼容旧逻辑）
        answer_details_count = UserAnswerDetail.objects.filter(quiz_record=quiz_record).count()
        if answer_details_count == 0:
            questions = Question.objects.filter(
                difficulty__lte=level.difficulty
            ).order_by('?')[:level.question_count]
            
            for idx, question in enumerate(questions):
                UserAnswerDetail.objects.create(
                    quiz_record=quiz_record,
                    question=question,
                    user_answer='',
                    is_correct=False,
                )
    else:
        # 创建新的答题记录
        quiz_record = UserQuizRecord.objects.create(
            user=request.user,
            level=level,
            start_time=timezone.now(),
            total_questions=level.question_count,
        )
        
        # 每次从题库中随机抽取题目（不依赖固定的 LevelQuestion 绑定）
        questions = Question.objects.filter(
            difficulty__lte=level.difficulty
        ).order_by('?')[:level.question_count]
        
        if questions.count() < level.question_count:
            # 如果题目不够，降低难度要求再抽
            questions = Question.objects.all().order_by('?')[:level.question_count]
        
        # 创建答题详情
        for idx, question in enumerate(questions):
            UserAnswerDetail.objects.create(
                quiz_record=quiz_record,
                question=question,
                user_answer='',
                is_correct=False,
            )
    
    # 获取当前题目
    answer_details = UserAnswerDetail.objects.filter(
        quiz_record=quiz_record
    ).select_related('question', 'question__dance_project', 'question__knowledge_point')
    
    # 检查是否有答题详情
    if not answer_details.exists():
        return JsonResponse({'success': False, 'error': '没有可用的题目'}, status=400)
    
    # 确保索引不越界
    if quiz_record.current_question_index >= answer_details.count():
        return JsonResponse({'success': False, 'error': '已答完所有题目'}, status=400)
    
    current_detail = answer_details[quiz_record.current_question_index]
    question = current_detail.question
    
    # 构建题目数据
    question_data = {
        'id': question.id,
        'type': question.question_type,
        'content': question.content,
        'options': question.options,
        'difficulty': question.get_difficulty_display(),
        'knowledge_point': question.knowledge_point.name if question.knowledge_point else None,
        'dance_project': question.dance_project.name if question.dance_project else None,
        'current_index': quiz_record.current_question_index,
        'total_questions': quiz_record.total_questions,
    }
    
    return JsonResponse({
        'success': True,
        'quiz_record_id': quiz_record.id,
        'question': question_data,
        'time_limit': level.time_limit,
    })


@login_required
@csrf_exempt
def submit_answer(request):
    """提交答案"""
    if request.method != 'POST':
        return JsonResponse({'success': False, 'error': '仅支持POST请求'}, status=405)
    
    try:
        data = json.loads(request.body)
        quiz_record_id = data.get('quiz_record_id')
        answer = data.get('answer')
        time_spent = data.get('time_spent', 0)
        
        quiz_record = get_object_or_404(UserQuizRecord, id=quiz_record_id, user=request.user)
        
        # 获取当前答题详情
        answer_details = UserAnswerDetail.objects.filter(
            quiz_record=quiz_record
        ).select_related('question', 'question__dance_project', 'question__knowledge_point')
        
        current_detail = answer_details[quiz_record.current_question_index]
        question = current_detail.question
        
        # 判断答案是否正确
        is_correct = answer == question.correct_answer
        
        # 更新答题详情
        current_detail.user_answer = answer
        current_detail.is_correct = is_correct
        current_detail.time_spent = time_spent
        current_detail.save()
        
        # 更新答题记录
        if is_correct:
            quiz_record.correct_answers += 1
            quiz_record.score += 10  # 每题10分
        else:
            quiz_record.wrong_answers += 1
        
        # 移动到下一题
        quiz_record.current_question_index += 1
        
        # 检查是否答完所有题目
        if quiz_record.current_question_index >= quiz_record.total_questions:
            quiz_record.is_completed = True
            quiz_record.end_time = timezone.now()
            quiz_record.is_passed = quiz_record.score >= quiz_record.level.required_score
            quiz_record.save()
            
            return JsonResponse({
                'success': True,
                'completed': True,
                'is_correct': is_correct,
                'quiz_record': {
                    'score': quiz_record.score,
                    'is_passed': quiz_record.is_passed,
                    'correct_answers': quiz_record.correct_answers,
                    'wrong_answers': quiz_record.wrong_answers,
                },
                'extension_knowledge_points': list(question.extension_knowledge_points.values('id', 'name', 'description')) if is_correct else [],
            })
        else:
            quiz_record.save()
            
            # 获取下一题
            next_detail = answer_details[quiz_record.current_question_index]
            next_question = next_detail.question
            
            next_question_data = {
                'id': next_question.id,
                'type': next_question.question_type,
                'content': next_question.content,
                'options': next_question.options,
                'difficulty': next_question.get_difficulty_display(),
                'knowledge_point': next_question.knowledge_point.name if next_question.knowledge_point else None,
                'dance_project': next_question.dance_project.name if next_question.dance_project else None,
                'current_index': quiz_record.current_question_index,
                'total_questions': quiz_record.total_questions,
            }
            
            return JsonResponse({
                'success': True,
                'completed': False,
                'is_correct': is_correct,
                'next_question': next_question_data,
                'extension_knowledge_points': list(question.extension_knowledge_points.values('id', 'name', 'description')) if is_correct else [],
                'wrong_answer_info': {
                    'dance_project_id': question.dance_project.id if question.dance_project else None,
                    'dance_project_name': question.dance_project.name if question.dance_project else None,
                    'knowledge_point': question.knowledge_point.name if question.knowledge_point else None,
                    'explanation': question.explanation,
                } if not is_correct else None,
            })
    
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)}, status=500)


@login_required
def quiz_result(request, record_id):
    """答题结果页面"""
    quiz_record = get_object_or_404(UserQuizRecord, id=record_id, user=request.user)
    
    # 获取答题详情
    answer_details = UserAnswerDetail.objects.filter(
        quiz_record=quiz_record
    ).select_related('question', 'question__dance_project')
    
    context = {
        'quiz_record': quiz_record,
        'answer_details': answer_details,
    }
    return render(request, 'quiz/quiz_result.html', context)


@login_required
def user_progress(request):
    """用户答题进度页面"""
    # 获取所有开启的关卡
    all_levels = Level.objects.filter(is_active=True)
    total_levels = all_levels.count()
    
    # 获取用户所有答题记录
    records = UserQuizRecord.objects.filter(
        user=request.user
    ).select_related('level').order_by('-start_time')
    
    # 统计各关卡最佳成绩
    level_stats = {}
    for record in records:
        level_id = record.level.id
        if level_id not in level_stats or record.score > level_stats[level_id]['best_score']:
            level_stats[level_id] = {
                'level': record.level,
                'best_score': record.score,
                'is_passed': record.is_passed,
                'attempt_count': level_stats.get(level_id, {}).get('attempt_count', 0) + 1,
            }
        else:
            level_stats[level_id]['attempt_count'] += 1
    
    # 计算通关率
    total_passed = sum(1 for v in level_stats.values() if v['is_passed'])
    pass_rate = (total_passed / total_levels * 100) if total_levels > 0 else 0
    
    context = {
        'records': records[:20],  # 最近20条记录
        'level_stats': level_stats,
        'total_passed': total_passed,
        'total_levels': total_levels,
        'total_attempts': records.count(),
        'pass_rate': pass_rate,
    }
    return render(request, 'quiz/user_progress.html', context)


@login_required
def wrong_questions(request):
    """错题集页面"""
    # 获取用户所有答题记录，按时间倒序
    all_answers = UserAnswerDetail.objects.filter(
        quiz_record__user=request.user
    ).select_related(
        'question',
        'question__knowledge_point',
        'question__dance_project',
        'quiz_record__level'
    ).order_by('-quiz_record__start_time', '-id')
    
    # 去重：同一题目只保留最近一次答题记录
    seen_questions = {}
    for answer in all_answers:
        question_id = answer.question.id
        if question_id not in seen_questions:
            seen_questions[question_id] = answer
    
    # 筛选出最近一次答错的题目
    unique_wrong_answers = [
        answer for answer in seen_questions.values()
        if not answer.is_correct
    ]
    
    # 分页处理
    from django.core.paginator import Paginator
    paginator = Paginator(unique_wrong_answers, 10)  # 每页10个
    page_number = request.GET.get('page', 1)
    page_obj = paginator.get_page(page_number)
    
    context = {
        'page_obj': page_obj,
        'wrong_answers': page_obj,  # 使用分页后的数据
        'total_wrong': len(unique_wrong_answers),
    }
    return render(request, 'quiz/wrong_questions.html', context)


@login_required
def retry_wrong_questions(request):
    """错题重答功能"""
    # 获取用户所有答题记录，按时间倒序
    all_answers = UserAnswerDetail.objects.filter(
        quiz_record__user=request.user
    ).order_by('-quiz_record__start_time', '-id')
    
    # 去重：同一题目只保留最近一次答题记录
    seen_questions = {}
    for answer in all_answers:
        question_id = answer.question_id
        if question_id not in seen_questions:
            seen_questions[question_id] = answer
    
    # 筛选出最近一次答错的题目ID
    wrong_question_ids = [
        question_id for question_id, answer in seen_questions.items()
        if not answer.is_correct
    ]
    
    if not wrong_question_ids:
        from django.contrib import messages
        messages.info(request, '暂无错题可重答')
        return redirect('quiz:wrong_questions')
    
    # 创建一个临时的错题练习关卡
    from django.utils import timezone
    import random
    
    # 检查是否已经有错题练习关卡
    retry_level, created = Level.objects.get_or_create(
        name='错题重练',
        defaults={
            'description': '自动生成的错题练习关卡',
            'category': 'mixed',
            'difficulty': 3,
            'question_count': min(len(wrong_question_ids), 20),  # 最多20题
            'time_limit': 0,  # 不限时
            'required_score': 60,
            'is_active': True,
            'order_index': 999,
            'icon': 'fa-redo',
        }
    )
    
    # 如果不是刚创建的，更新题目数量
    if not created:
        retry_level.question_count = min(len(wrong_question_ids), 20)
        retry_level.save()
    
    # 创建答题记录
    quiz_record = UserQuizRecord.objects.create(
        user=request.user,
        level=retry_level,
        start_time=timezone.now(),
        total_questions=retry_level.question_count,
    )
    
    # 随机选择错题（最多20道）
    selected_question_ids = random.sample(
        list(wrong_question_ids),
        min(len(wrong_question_ids), 20)
    )
    
    questions = Question.objects.filter(id__in=selected_question_ids)
    
    # 创建答题详情
    for idx, question in enumerate(questions):
        UserAnswerDetail.objects.create(
            quiz_record=quiz_record,
            question=question,
            user_answer='',
            is_correct=False,
        )
    
    # 重定向到答题页面
    from django.http import HttpResponseRedirect
    return HttpResponseRedirect(f'/quiz/game/{retry_level.id}/')


# 添加缺失的导入
from django.db import models
