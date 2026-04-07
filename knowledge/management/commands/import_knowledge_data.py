"""
知识图谱数据导入脚本

使用方法：
1. 将AI生成的JSON文件放在 knowledge/data/ 目录下
2. 运行: python manage.py import_knowledge_data --file=data/京西太平鼓.json
3. 或批量导入: python manage.py import_knowledge_data --dir=data/
"""

import json
import os
from django.core.management.base import BaseCommand, CommandError
from knowledge.models import DanceProject, ActionModule, SpecificMove, MoveAttribute, LearningResource, KnowledgePoint


class Command(BaseCommand):
    help = '从JSON文件导入知识图谱数据'

    def add_arguments(self, parser):
        parser.add_argument(
            '--file',
            type=str,
            help='单个JSON文件路径',
        )
        parser.add_argument(
            '--dir',
            type=str,
            help='包含多个JSON文件的目录路径',
        )

    def handle(self, *args, **options):
        if options['file']:
            self.import_single_file(options['file'])
        elif options['dir']:
            self.import_directory(options['dir'])
        else:
            raise CommandError('请提供 --file 或 --dir 参数')

    def import_single_file(self, file_path):
        """导入单个JSON文件"""
        if not os.path.exists(file_path):
            raise CommandError(f'文件不存在: {file_path}')

        self.stdout.write(f'正在导入: {file_path}')
        
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            self.import_project_data(data)
            self.stdout.write(
                self.style.SUCCESS(f'✓ 成功导入: {file_path}')
            )
        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f'✗ 导入失败: {str(e)}')
            )
            raise

    def import_directory(self, dir_path):
        """导入目录下所有JSON文件"""
        if not os.path.exists(dir_path):
            raise CommandError(f'目录不存在: {dir_path}')

        json_files = [f for f in os.listdir(dir_path) if f.endswith('.json')]
        
        if not json_files:
            raise CommandError(f'目录中没有JSON文件: {dir_path}')

        self.stdout.write(f'找到 {len(json_files)} 个JSON文件')
        
        success_count = 0
        error_count = 0

        for filename in json_files:
            file_path = os.path.join(dir_path, filename)
            try:
                self.import_single_file(file_path)
                success_count += 1
            except Exception as e:
                self.stdout.write(
                    self.style.ERROR(f'✗ {filename}: {str(e)}')
                )
                error_count += 1

        self.stdout.write('\n' + '=' * 60)
        self.stdout.write(
            self.style.SUCCESS(f'导入完成! 成功: {success_count}, 失败: {error_count}')
        )

    def import_project_data(self, data):
        """导入单个项目的完整数据"""
        project_name = data.get('dance_project_name')
        if not project_name:
            raise CommandError('JSON数据缺少 dance_project_name 字段')

        # 查找或创建舞蹈项目
        project, created = DanceProject.objects.get_or_create(
            name=project_name,
            defaults={
                'category': data.get('dance_project_category', '民间舞蹈'),
                'description': data.get('dance_project_description', ''),
                'difficulty_level': data.get('difficulty_level', 3),
            }
        )

        if created:
            self.stdout.write(f'  创建新项目: {project_name}')
        else:
            self.stdout.write(f'  更新现有项目: {project_name}')

        # 导入模块和招式
        modules_data = data.get('modules', [])
        total_moves = 0
        total_resources = 0
        total_knowledge_points = 0

        for module_data in modules_data:
            module, module_created = ActionModule.objects.get_or_create(
                dance_project=project,
                name=module_data['name'],
                defaults={
                    'description': module_data.get('description', ''),
                    'order_index': module_data.get('order_index', 1),
                }
            )

            moves_data = module_data.get('moves', [])
            for move_data in moves_data:
                move, move_created = SpecificMove.objects.get_or_create(
                    action_module=module,
                    name=move_data['name'],
                    defaults={
                        'description': move_data.get('description', ''),
                        'difficulty': move_data.get('difficulty', 3),
                        'duration': move_data.get('duration', 300),
                        'order_index': move_data.get('order_index', 1),
                    }
                )
                total_moves += 1

                # 导入动作属性
                if 'attributes' in move_data:
                    attr_data = move_data['attributes']
                    MoveAttribute.objects.update_or_create(
                        specific_move=move,
                        defaults={
                            'force_parts': attr_data.get('force_parts', ''),
                            'common_mistakes': attr_data.get('common_mistakes', ''),
                            'key_points': attr_data.get('key_points', ''),
                            'precautions': attr_data.get('precautions', ''),
                        }
                    )

                # 导入学习资源
                resources_data = move_data.get('resources', [])
                for res_data in resources_data:
                    LearningResource.objects.get_or_create(
                        specific_move=move,
                        title=res_data['title'],
                        defaults={
                            'resource_type': res_data.get('type', 'video'),
                            'url': res_data.get('url', ''),
                            'duration': res_data.get('duration'),
                            'thumbnail': None,
                            'order_index': 1,
                        }
                    )
                    total_resources += 1

                # 导入知识点
                kp_data_list = move_data.get('knowledge_points', [])
                for kp_data in kp_data_list:
                    KnowledgePoint.objects.get_or_create(
                        specific_move=move,
                        name=kp_data['name'],
                        defaults={
                            'description': kp_data.get('description', ''),
                            'category': kp_data.get('category', '技法要点'),
                            'importance_level': kp_data.get('importance_level', 3),
                        }
                    )
                    total_knowledge_points += 1

        self.stdout.write(
            f'    模块数: {len(modules_data)}, '
            f'招式数: {total_moves}, '
            f'资源数: {total_resources}, '
            f'知识点: {total_knowledge_points}'
        )
