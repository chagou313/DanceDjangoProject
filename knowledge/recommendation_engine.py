"""
个性化舞蹈学习路径推荐系统
基于内容的推荐算法实现
"""
import math
from django.db.models import Q, Avg, Count
from knowledge.models import DanceProject, ActionModule, SpecificMove, KnowledgePoint, UserLearningProgress
from dance.models import UserProfile
from community.models import PostLike, PostCollection


class ContentBasedRecommender:
    """基于内容的推荐引擎"""
    
    def __init__(self, user):
        self.user = user
        self.user_profile = UserProfile.objects.filter(user=user).first()
    
    def get_recommendations(self, limit=10):
        """
        获取个性化推荐列表
        :param limit: 返回推荐数量
        :return: 推荐项目列表，包含项目和推荐理由
        """
        # 获取所有候选项目（排除用户已完成的）
        completed_projects = UserLearningProgress.objects.filter(
            user=self.user,
            status='mastered'
        ).values_list('dance_project_id', flat=True)
        
        candidate_projects = DanceProject.objects.exclude(
            id__in=completed_projects
        )
        
        if not candidate_projects.exists():
            return []
        
        # 计算每个项目的推荐得分
        scored_projects = []
        for project in candidate_projects:
            score, reasons = self._calculate_project_score(project)
            if score > 0:
                scored_projects.append({
                    'project': project,
                    'score': score,
                    'reasons': reasons
                })
        
        # 按得分排序
        scored_projects.sort(key=lambda x: x['score'], reverse=True)
        
        # 返回前limit个
        return scored_projects[:limit]
    
    def _calculate_project_score(self, project):
        """
        计算项目推荐得分
        :param project: 舞蹈项目
        :return: (得分, 推荐理由列表)
        """
        total_score = 0
        reasons = []
        
        # 1. 难度匹配度 (权重: 0.25)
        difficulty_score = self._calculate_difficulty_match(project)
        if difficulty_score > 0:
            total_score += difficulty_score * 0.25
            reasons.append(f"难度适合您当前的水平")
        
        # 2. 类别偏好匹配 (权重: 0.25)
        category_score = self._calculate_category_match(project)
        if category_score > 0:
            total_score += category_score * 0.25
            reasons.append(f"符合您的舞种偏好")
        
        # 3. 知识点相关性 (权重: 0.20)
        knowledge_score = self._calculate_knowledge_relevance(project)
        if knowledge_score > 0:
            total_score += knowledge_score * 0.20
            reasons.append(f"与您已掌握的知识点相关")
        
        # 4. 社区热度 (权重: 0.15)
        popularity_score = self._calculate_popularity(project)
        if popularity_score > 0:
            total_score += popularity_score * 0.15
            reasons.append(f"社区热门项目")
        
        # 5. 学习进度连续性 (权重: 0.15)
        continuity_score = self._calculate_learning_continuity(project)
        if continuity_score > 0:
            total_score += continuity_score * 0.15
            reasons.append(f"与您正在学习的项目相关")
        
        return total_score, reasons
    
    def _calculate_difficulty_match(self, project):
        """
        计算难度匹配度
        基于用户的技能等级和项目难度
        """
        if not self.user_profile or not self.user_profile.skill_level:
            return 0.5  # 无用户数据时返回中等分数
        
        user_level = self.user_profile.skill_level
        project_difficulty = project.difficulty_level
        
        # 理想难度：用户当前等级或略高一级
        ideal_difficulty = min(user_level + 1, 5)
        
        # 计算难度差异
        diff = abs(project_difficulty - ideal_difficulty)
        
        # 使用高斯函数计算匹配度
        score = math.exp(-(diff ** 2) / 2)
        
        return score
    
    def _calculate_category_match(self, project):
        """
        计算类别偏好匹配度
        """
        if not self.user_profile or not self.user_profile.preferred_dance_types:
            return 0.5  # 无偏好时返回基础分
        
        preferred_types = self.user_profile.preferred_dance_types
        
        # 检查项目类别是否在用户偏好中
        if project.category in preferred_types:
            return 1.0
        
        # 检查是否有相似的类别
        # 这里可以扩展更复杂的类别相似性计算
        return 0.3
    
    def _calculate_knowledge_relevance(self, project):
        """
        计算知识点相关性
        基于用户已掌握的知识点的关联度
        """
        # 获取用户已掌握程度较高的知识点
        mastered_kps = UserLearningProgress.objects.filter(
            user=self.user,
            proficiency_score__gte=70
        ).select_related('specific_move')
        
        if not mastered_kps.exists():
            return 0.3  # 无历史数据时返回基础分
        
        # 获取目标项目的所有知识点
        project_kps = KnowledgePoint.objects.filter(
            specific_move__action_module__dance_project=project
        ).values_list('id', flat=True)
        
        if not project_kps:
            return 0.2
        
        # 计算重叠度
        mastered_kp_ids = set(
            kp.specific_move.knowledge_points.values_list('id', flat=True)
            for kp in mastered_kps
        )
        mastered_kp_ids = {kp_id for sublist in mastered_kp_ids for kp_id in sublist}
        
        overlap = len(set(project_kps) & mastered_kp_ids)
        total_project_kps = len(project_kps)
        
        if total_project_kps == 0:
            return 0.2
        
        relevance = overlap / total_project_kps
        return min(relevance * 2, 1.0)  # 放大相关性
    
    def _calculate_popularity(self, project):
        """
        计算项目热度
        基于社区互动数据（帖子、点赞、收藏）
        """
        from community.models import Post, PostLike, PostCollection
        
        # 1. 统计该项目相关的帖子数量
        related_posts = Post.objects.filter(
            Q(title__icontains=project.name) | 
            Q(content__icontains=project.name)
        )
        post_count = related_posts.count()
        
        if post_count == 0:
            return 0.0
        
        # 2. 统计这些帖子的点赞数
        like_count = PostLike.objects.filter(
            post__in=related_posts
        ).count()
        
        # 3. 统计这些帖子的收藏数
        collection_count = PostCollection.objects.filter(
            post__in=related_posts
        ).count()
        
        # 4. 综合计算热度得分（加权求和）
        # 帖子数权重 40%，点赞数权重 35%，收藏数权重 25%
        raw_score = (post_count * 0.4 + like_count * 0.35 + collection_count * 0.25)
        
        # 归一化到0-1之间（假设满分标准：50篇帖子 + 200个赞 + 100个收藏 = 120分）
        max_score = 120
        popularity = min(raw_score / max_score, 1.0)
        
        return popularity
    
    def _calculate_learning_continuity(self, project):
        """
        计算学习连续性
        基于用户正在进行的学习项目
        """
        # 获取用户正在学习的项目
        learning_projects = UserLearningProgress.objects.filter(
            user=self.user,
            status='learning'
        ).select_related('dance_project')
        
        if not learning_projects.exists():
            return 0.3  # 无进行中的项目时返回基础分
        
        # 检查是否有相同类别的项目
        current_categories = set(
            lp.dance_project.category 
            for lp in learning_projects
        )
        
        if project.category in current_categories:
            return 1.0
        
        # 检查是否有相同的动作模块类型
        current_modules = ActionModule.objects.filter(
            dance_project__in=[lp.dance_project for lp in learning_projects]
        ).values_list('name', flat=True)
        
        target_modules = ActionModule.objects.filter(
            dance_project=project
        ).values_list('name', flat=True)
        
        # 计算模块名称的相似度
        common_modules = set(current_modules) & set(target_modules)
        if common_modules:
            return 0.7
        
        return 0.2
    
    def generate_learning_path(self, project_id, stages=3):
        """
        为指定项目生成学习路径
        :param project_id: 项目ID（可能是 origin 表的 ID）
        :param stages: 阶段数量
        :return: 学习路径字典
        """
        from origin.models import DanceProject as OriginDanceProject
        
        # 尝试通过两种方式查找项目
        project = None
        try:
            # 先尝试从 knowledge 表查找
            project = DanceProject.objects.get(id=project_id)
        except DanceProject.DoesNotExist:
            # 如果找不到，尝试从 origin 表按 ID 查找，然后通过名称匹配 knowledge 表
            try:
                origin_project = OriginDanceProject.objects.get(id=project_id)
                project = DanceProject.objects.get(name=origin_project.name)
            except (OriginDanceProject.DoesNotExist, DanceProject.DoesNotExist):
                return None
        
        if not project:
            return None
        
        # 获取项目的所有动作模块
        modules = ActionModule.objects.filter(
            dance_project=project
        ).prefetch_related('specific_moves').order_by('order_index')
        
        if not modules.exists():
            return None
        
        # 根据难度和顺序划分阶段
        all_moves = []
        for module in modules:
            moves = SpecificMove.objects.filter(
                action_module=module
            ).order_by('difficulty', 'order_index')
            all_moves.extend(moves)
        
        # 按难度分组
        easy_moves = [m for m in all_moves if m.difficulty <= 3]
        medium_moves = [m for m in all_moves if 3 < m.difficulty <= 6]
        hard_moves = [m for m in all_moves if m.difficulty > 6]
        
        path_stages = []
        
        # 阶段1: 基础入门
        if easy_moves:
            stage1_moves = easy_moves[:len(easy_moves)//2 + 1]
            path_stages.append({
                'stage_name': '基础入门',
                'description': f'学习{project.name}的基础动作，建立正确的动作框架',
                'moves': self._format_moves(stage1_moves),
                'estimated_days': len(stage1_moves) * 3,  # 每个招式建议练习3天
                'difficulty': '初级'
            })
        
        # 阶段2: 技能提升
        if medium_moves or easy_moves:
            stage2_moves = (easy_moves[len(easy_moves)//2 + 1:] if len(easy_moves) > 1 else []) + medium_moves[:len(medium_moves)//2 + 1]
            if stage2_moves:
                path_stages.append({
                    'stage_name': '技能提升',
                    'description': f'掌握{project.name}的核心技法，提升动作质量',
                    'moves': self._format_moves(stage2_moves),
                    'estimated_days': len(stage2_moves) * 4,
                    'difficulty': '中级'
                })
        
        # 阶段3: 高级精通
        if hard_moves or medium_moves:
            stage3_moves = (medium_moves[len(medium_moves)//2 + 1:] if len(medium_moves) > 1 else []) + hard_moves
            if stage3_moves:
                path_stages.append({
                    'stage_name': '高级精通',
                    'description': f'精通{project.name}的高难度技巧，展现艺术表现力',
                    'moves': self._format_moves(stage3_moves),
                    'estimated_days': len(stage3_moves) * 5,
                    'difficulty': '高级'
                })
        
        # 计算总时长
        total_days = sum(stage['estimated_days'] for stage in path_stages)
        
        return {
            'project': {
                'id': project.id,
                'name': project.name,
                'category': project.category,
                'difficulty': project.difficulty_level,
                'description': project.description
            },
            'total_stages': len(path_stages),
            'total_estimated_days': total_days,
            'stages': path_stages
        }
    
    def _format_moves(self, moves):
        """格式化招式信息"""
        formatted = []
        for move in moves:
            move_data = {
                'id': move.id,
                'name': move.name,
                'description': move.description,
                'difficulty': move.difficulty,
                'duration': move.duration,
                'module': move.action_module.name
            }
            
            # 获取动作属性
            attr = move.attributes.first()
            if attr:
                move_data['key_points'] = attr.key_points
                move_data['common_mistakes'] = attr.common_mistakes
            
            # 获取学习资源
            resources = move.learning_resources.all()[:2]
            move_data['resources'] = [
                {
                    'type': r.resource_type,
                    'title': r.title,
                    'duration': r.duration
                }
                for r in resources
            ]
            
            formatted.append(move_data)
        
        return formatted


def get_user_recommendations(user, limit=10):
    """
    获取用户个性化推荐的便捷函数
    """
    recommender = ContentBasedRecommender(user)
    return recommender.get_recommendations(limit=limit)


def generate_learning_path_for_user(user, project_id):
    """
    为用户生成指定项目的学习路径
    """
    recommender = ContentBasedRecommender(user)
    return recommender.generate_learning_path(project_id)
