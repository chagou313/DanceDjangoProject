"""
为所有 356 个传统舞蹈项目生成真实的知识图谱数据
使用方法: python manage.py generate_classic_dance_data
"""
import time
from django.core.management.base import BaseCommand
from knowledge.models import DanceProject, ActionModule, SpecificMove, MoveAttribute, LearningResource, KnowledgePoint
from origin.models import DanceProject as OriginDanceProject


class Command(BaseCommand):
    help = '为所有舞蹈项目生成真实数据'

    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS('=' * 70))
        self.stdout.write(self.style.SUCCESS('为所有舞蹈项目生成真实知识图谱数据'))
        self.stdout.write(self.style.SUCCESS('=' * 70))
        
        origin_projects = OriginDanceProject.objects.all()
        total_count = origin_projects.count()
        
        self.stdout.write(f'\n共有 {total_count} 个舞蹈项目需要处理\n')
        
        clear = input('是否先清除所有旧数据？(y/n): ').strip().lower()
        if clear == 'y':
            self.stdout.write(self.style.WARNING('\n⚠️  正在清除所有旧数据...'))
            KnowledgePoint.objects.all().delete()
            LearningResource.objects.all().delete()
            MoveAttribute.objects.all().delete()
            SpecificMove.objects.all().delete()
            ActionModule.objects.all().delete()
            DanceProject.objects.all().delete()
            self.stdout.write(self.style.SUCCESS('✓ 旧数据已清除\n'))
        
        success_count = 0
        skip_count = 0
        error_count = 0
        start_time = time.time()
        
        for idx, origin_project in enumerate(origin_projects, 1):
            try:
                if idx % 20 == 0 or idx == 1:
                    elapsed = time.time() - start_time
                    self.stdout.write(f'进度: [{idx}/{total_count}] ({idx*100//total_count}%) - 已用时 {elapsed:.1f}秒')
                
                kp_project, created = DanceProject.objects.get_or_create(
                    name=origin_project.name,
                    defaults={
                        'description': origin_project.introduction or f'{origin_project.name}是非物质文化遗产项目',
                        'category': origin_project.get_dance_type_display(),
                        'difficulty_level': 3,
                    }
                )
                
                if not created and ActionModule.objects.filter(dance_project=kp_project).exists():
                    skip_count += 1
                    continue
                
                if not created:
                    ActionModule.objects.filter(dance_project=kp_project).delete()
                
                self.generate_dance_data(kp_project, origin_project)
                success_count += 1
                
            except Exception as e:
                self.stdout.write(self.style.ERROR(f'\n✗ 失败 [{idx}]: {origin_project.name} - {str(e)}'))
                error_count += 1
        
        elapsed = time.time() - start_time
        self.stdout.write('\n' + '=' * 70)
        self.stdout.write(self.style.SUCCESS('生成完成！'))
        self.stdout.write(self.style.SUCCESS('=' * 70))
        self.stdout.write(f'总项目数: {total_count}')
        self.stdout.write(self.style.SUCCESS(f'成功生成: {success_count}'))
        self.stdout.write(self.style.WARNING(f'跳过(已存在): {skip_count}'))
        self.stdout.write(self.style.ERROR(f'失败: {error_count}'))
        self.stdout.write(f'总用时: {elapsed:.1f}秒')
        
        projects = DanceProject.objects.count()
        modules = ActionModule.objects.count()
        moves = SpecificMove.objects.count()
        resources = LearningResource.objects.count()
        kps = KnowledgePoint.objects.count()
        
        self.stdout.write('\n📊 数据库统计:')
        self.stdout.write(f'   舞蹈项目: {projects}')
        self.stdout.write(f'   动作模块: {modules}')
        self.stdout.write(f'   具体招式: {moves}')
        self.stdout.write(f'   学习资源: {resources}')
        self.stdout.write(f'   知识点: {kps}')

    def create_module(self, project, name, description, order_index):
        return ActionModule.objects.create(
            dance_project=project, name=name, description=description, order_index=order_index
        )

    def create_move(self, module, name, description, difficulty, duration, order_index,
                    force_parts='', common_mistakes='', key_points='', precautions=''):
        move = SpecificMove.objects.create(
            action_module=module, name=name, description=description,
            difficulty=difficulty, duration=duration, order_index=order_index
        )
        if force_parts or common_mistakes or key_points or precautions:
            MoveAttribute.objects.create(
                specific_move=move, force_parts=force_parts,
                common_mistakes=common_mistakes, key_points=key_points, precautions=precautions
            )
        return move

    def create_resource(self, move, resource_type, title, duration=None):
        return LearningResource.objects.create(
            specific_move=move, resource_type=resource_type, title=title, url='', duration=duration
        )

    def create_knowledge_point(self, move, name, description, category, importance_level):
        return KnowledgePoint.objects.create(
            specific_move=move, name=name, description=description,
            category=category, importance_level=importance_level
        )

    def generate_dance_data(self, project, origin_project):
        """智能路由：根据舞蹈名称和类型选择模板"""
        dance_name = origin_project.name
        
        # 鼓类舞蹈
        if '腰鼓' in dance_name or '太平鼓' in dance_name or '花鼓' in dance_name or '蹩鼓' in dance_name:
            self._generate_drum_dance(project, dance_name)
        # 盾牌舞
        elif '盾牌' in dance_name:
            self._generate_shield_dance(project, dance_name)
        # 孔雀舞
        elif '孔雀' in dance_name:
            self._generate_peacock_dance(project, dance_name)
        # 秧歌
        elif '秧歌' in dance_name:
            self._generate_yangge_dance(project, dance_name)
        # 龙舞
        elif '龙舞' in dance_name or '舞龙' in dance_name:
            self._generate_dragon_dance(project, dance_name)
        # 狮舞
        elif '狮舞' in dance_name or '舞狮' in dance_name:
            self._generate_lion_dance(project, dance_name)
        # 傩舞
        elif '傩' in dance_name:
            self._generate_nuo_dance(project, dance_name)
        # 花灯/灯舞
        elif '灯' in dance_name:
            self._generate_lantern_dance(project, dance_name)
        # 弦子/锅庄/藏族舞蹈
        elif '弦子' in dance_name or '锅庄' in dance_name:
            self._generate_tibetan_dance(project, dance_name)
        # 摆手舞
        elif '摆手' in dance_name:
            self._generate_baishou_dance(project, dance_name)
        # 默认民间舞蹈
        else:
            self._generate_folk_dance(project, dance_name)

    # ========== 模板实现 ==========

    def _generate_drum_dance(self, project, dance_name):
        self.stdout.write(f'  → {dance_name} (鼓类)')
        m1 = self.create_module(project, '基本鼓法模块', f'{dance_name}的基础击鼓技法，包括单点、双点、滚奏等基本技法。', 1)
        for name, desc, diff, dur, oi, fp, cm, kp, pc in [
            ('单点击鼓', f'右手持鼓槌单击鼓面中心，发出清脆响亮的声音。是{dance_name}最基础的击鼓技法。', 2, 300, 1, '手腕、前臂', '手臂僵硬、力度过大', '手腕放松，以腕发力，击鼓中心', '初学者应先练习手腕灵活性'),
            ('双点连击', '连续两次快速击鼓，形成"咚咚"的节奏型，间隔均匀。', 3, 360, 2, '手腕、手指', '两次击鼓力度不均、间隔不稳定', '手腕带动，力度均匀，节奏稳定', '先慢练，熟练掌握后再加快速度'),
            ('花点滚奏', '以手腕快速旋转带动鼓槌，在鼓面上连续滚动击打。是高难度技巧。', 5, 420, 3, '手腕、前臂、手指', '滚奏不连续、鼓声不均匀', '手腕放松旋转，节奏均匀', '需要先掌握单点和双点技法'),
        ]:
            move = self.create_move(m1, name, desc, diff, dur, oi, fp, cm, kp, pc)
            self.create_resource(move, 'video', f'{name}分解教学', 240)
            self.create_resource(move, 'demo', f'传承人{name}示范', 180)
            self.create_knowledge_point(move, '手腕发力', '掌握以腕部为主的发力技巧', '基础技法', 5)
            self.create_knowledge_point(move, '节奏控制', '培养准确的节奏感', '音乐素养', 5)
        
        m2 = self.create_module(project, '跳跃动作模块', f'{dance_name}特色的跳跃和腾挪动作，展现豪放风格。', 2)
        for name, desc, diff, dur, oi, fp, cm, kp, pc in [
            ('蹬腿跳跃', '单腿蹬地跃起，同时击鼓，落地稳健。体现民间舞蹈的豪迈性格。', 4, 360, 1, '腿部、腰部、核心力量', '跳跃高度不够、落地不稳', '蹬地有力，跳跃协调，落地稳健', '注意膝盖保护，循序渐进'),
            ('转身飞槌', '原地旋转360度，同时挥动鼓槌击鼓，动作连贯有力。', 5, 420, 2, '全身协调、腰部、手臂', '旋转不稳、击鼓不准', '以腰为轴，旋转流畅，击鼓准确', '先练习旋转平衡，再结合击鼓'),
        ]:
            move = self.create_move(m2, name, desc, diff, dur, oi, fp, cm, kp, pc)
            self.create_resource(move, 'video', f'{name}完整演示', 300)
            self.create_knowledge_point(move, '腿部力量', '增强腿部爆发力', '身体素质', 4)
            self.create_knowledge_point(move, '平衡能力', '掌握旋转中的平衡', '技能要点', 5)

    def _generate_shield_dance(self, project, dance_name):
        self.stdout.write(f'  → {dance_name} (盾牌类)')
        m1 = self.create_module(project, '基本武术模块', f'{dance_name}的基础武术动作和站桩训练。', 1)
        for name, desc, diff, dur, oi, fp, cm, kp, pc in [
            ('马步站桩', '双脚分开与肩同宽，屈膝下蹲成马步，双手持盾，稳如泰山。', 3, 360, 1, '腿部、腰部、核心力量', '马步不稳、重心偏移', '马步扎实，重心稳定，身体正直', '初学者时间不宜过长'),
            ('弓步推盾', '前腿弓，后腿绷，双手持盾向前推，展现进攻姿态。', 4, 320, 2, '腿部、手臂、腰部', '弓步不稳、推盾无力', '弓步扎实，推盾有力，身体协调', '注意前后腿的比例'),
        ]:
            move = self.create_move(m1, name, desc, diff, dur, oi, fp, cm, kp, pc)
            self.create_resource(move, 'video', f'{name}基础训练', 280)
            self.create_knowledge_point(move, '站桩基本功', '掌握传统武术站桩要领', '基础技法', 5)
        
        m2 = self.create_module(project, '盾牌技法模块', f'{dance_name}的盾牌运用和防守技法。', 2)
        for name, desc, diff, dur, oi, fp, cm, kp, pc in [
            ('盾牌格挡', '运用盾牌进行上下左右的格挡防守，动作敏捷灵活。', 4, 360, 1, '手臂、腰部、反应能力', '格挡不及时、盾牌位置不对', '反应敏捷，盾牌到位，动作流畅', '需要先练习基本反应速度'),
            ('盾牌旋转', '手持盾牌快速旋转，形成防御屏障。是高难度技巧。', 5, 380, 2, '手臂、腰部、全身协调', '旋转不稳、盾牌失控', '旋转流畅，盾牌稳定，身体协调', '先慢练旋转，再加快速度'),
        ]:
            move = self.create_move(m2, name, desc, diff, dur, oi, fp, cm, kp, pc)
            self.create_resource(move, 'video', f'{name}技巧讲解', 300)
            self.create_knowledge_point(move, '防守技法', '掌握盾牌防守的基本方法', '技能要点', 5)

    def _generate_peacock_dance(self, project, dance_name):
        self.stdout.write(f'  → {dance_name} (孔雀类)')
        m1 = self.create_module(project, '基本手型模块', f'{dance_name}的手部造型和手势变化，是最核心的表现手段。', 1)
        for name, desc, diff, dur, oi, fp, cm, kp, pc in [
            ('孔雀手型', '拇指与食指捏成圆形，其余三指自然展开，形如孔雀头部。是标志性手型。', 2, 240, 1, '手指、手腕', '手指僵硬、手型不标准', '拇指食指捏圆，三指舒展，手腕放松', '需要经常练习手指灵活性'),
            ('展翅手型', '双手在胸前或头顶展开，手指张开，模拟孔雀展翅的姿态。', 3, 300, 2, '手指、手臂、肩部', '展开不充分、手臂僵硬', '手臂舒展，手指张开，姿态优雅', '注意肩部的放松和打开'),
        ]:
            move = self.create_move(m1, name, desc, diff, dur, oi, fp, cm, kp, pc)
            self.create_resource(move, 'video', f'{name}基础教学', 200)
            self.create_knowledge_point(move, '手型规范', '掌握标准手型', '基础技法', 5)
        
        m2 = self.create_module(project, '身段韵律模块', f'{dance_name}的身体姿态和韵律表达，展现S曲线美感。', 2)
        for name, desc, diff, dur, oi, fp, cm, kp, pc in [
            ('三道弯', '身体呈现头、胸、腰三段弯曲的S型姿态，是典型身段。', 5, 420, 1, '腰部、胸部、颈部', '弯曲不自然、三段不协调', '三段弯曲自然流畅，姿态优美', '需要先练习腰部柔韧性'),
            ('孔雀步', '双脚交替前行，步伐轻盈优雅，身体微微晃动，模拟孔雀行走。', 3, 300, 2, '腿部、脚部、腰部', '步伐沉重、身体晃动过大', '步伐轻盈，身体微晃，节奏平稳', '注意重心的平稳转移'),
        ]:
            move = self.create_move(m2, name, desc, diff, dur, oi, fp, cm, kp, pc)
            self.create_resource(move, 'video', f'{name}身段教学', 280)
            self.create_knowledge_point(move, '三道弯体态', '掌握S曲线美感', '基础技法', 5)

    def _generate_yangge_dance(self, project, dance_name):
        self.stdout.write(f'  → {dance_name} (秧歌类)')
        m1 = self.create_module(project, '基本步法模块', f'{dance_name}的基础步伐训练。', 1)
        for name, desc, diff, dur, oi, fp, cm, kp, pc in [
            ('十字步', '双脚交叉行进，形成十字轨迹，是秧歌的典型步法。', 3, 300, 1, '腿部、脚部', '步伐混乱、重心不稳', '步伐清晰，重心稳定，节奏明快', '先慢练熟悉步伐路线'),
            ('扭步', '双脚交替扭动前行，身体随之左右摇摆，展现秧歌"扭"的特点。', 3, 280, 2, '腿部、腰部、脚部', '扭动不自然、身体僵硬', '扭动自然，身体放松，节奏均匀', '注意腰部的灵活运用'),
        ]:
            move = self.create_move(m1, name, desc, diff, dur, oi, fp, cm, kp, pc)
            self.create_resource(move, 'video', f'{name}基础教学', 240)
            self.create_knowledge_point(move, '基础步法', '掌握秧歌基本步法', '基础技法', 5)
        
        m2 = self.create_module(project, '手绢花模块', f'{dance_name}的手绢花技法和手部动作。', 2)
        for name, desc, diff, dur, oi, fp, cm, kp, pc in [
            ('转绢花', '手腕旋转带动手绢形成花型，动作灵活优美。是标志性技法。', 4, 300, 1, '手腕、手指', '手绢转不起来、动作僵硬', '手腕灵活，手指配合，手绢旋转流畅', '需要反复练习手腕灵活性'),
            ('抛绢花', '将手绢向上抛起再接住，动作轻盈准确。', 4, 280, 2, '手腕、手臂、眼手协调', '抛不准、接不住', '抛得稳，接得准，动作流畅', '先低抛练习，再逐渐加高'),
        ]:
            move = self.create_move(m2, name, desc, diff, dur, oi, fp, cm, kp, pc)
            self.create_resource(move, 'video', f'{name}技巧教学', 220)
            self.create_knowledge_point(move, '手绢技法', '掌握手绢花技法', '技能要点', 5)

    def _generate_dragon_dance(self, project, dance_name):
        self.stdout.write(f'  → {dance_name} (龙舞类)')
        m1 = self.create_module(project, '基本龙舞模块', f'{dance_name}的基础龙舞动作。', 1)
        for name, desc, diff, dur, oi, fp, cm, kp, pc in [
            ('游龙', '舞龙者持龙杆，步伐协调，使龙身呈现游动姿态。', 3, 360, 1, '全身协调、手臂力量', '龙身不流畅、步伐混乱', '步伐稳健，龙身流畅，团队配合', '需要多次排练培养默契'),
            ('盘龙', '龙身盘旋上升，形成螺旋状，展现龙的雄伟气势。', 4, 420, 2, '全身协调、腰部', '盘旋不流畅、龙身打结', '盘旋流畅，龙身舒展，气势磅礴', '需要熟练掌握龙杆操作'),
        ]:
            move = self.create_move(m1, name, desc, diff, dur, oi, fp, cm, kp, pc)
            self.create_resource(move, 'video', f'{name}基础教学', 300)
            self.create_knowledge_point(move, '龙杆操控', '掌握龙杆的基本操控技巧', '技能要点', 5)

    def _generate_lion_dance(self, project, dance_name):
        self.stdout.write(f'  → {dance_name} (狮舞类)')
        m1 = self.create_module(project, '基本狮舞模块', f'{dance_name}的基础狮舞动作。', 1)
        for name, desc, diff, dur, oi, fp, cm, kp, pc in [
            ('醒狮', '狮子从沉睡中苏醒，伸懒腰、打哈欠，动作生动有趣。', 3, 300, 1, '全身协调、手臂', '动作不连贯、缺乏生气', '动作连贯，表情生动，富有生命力', '需要两人默契配合'),
            ('采青', '狮子发现食物，小心翼翼靠近，最终获取，展现狮子的机敏。', 4, 360, 2, '腿部、腰部、全身协调', '动作笨拙、缺乏技巧', '动作灵活，表现机敏，层次分明', '需要反复排练'),
        ]:
            move = self.create_move(m1, name, desc, diff, dur, oi, fp, cm, kp, pc)
            self.create_resource(move, 'video', f'{name}基础教学', 280)
            self.create_knowledge_point(move, '狮头操控', '掌握狮头的基本操控技巧', '技能要点', 5)

    def _generate_nuo_dance(self, project, dance_name):
        self.stdout.write(f'  → {dance_name} (傩舞类)')
        m1 = self.create_module(project, '基本傩舞模块', f'{dance_name}的基础傩舞动作，具有浓厚的祭祀色彩。', 1)
        for name, desc, diff, dur, oi, fp, cm, kp, pc in [
            ('傩面舞步', '佩戴傩面，步伐沉稳有力，展现神灵的威严。', 3, 300, 1, '腿部、脚部', '步伐不稳、缺乏威严', '步伐沉稳，姿态威严，节奏庄重', '需要先适应傩面重量'),
            ('驱邪动作', '双手持法器，做出驱邪赶鬼的动作，气势磅礴。', 4, 360, 2, '手臂、腰部、全身', '动作不连贯、缺乏气势', '动作有力，气势磅礴，节奏统一', '需要充分理解傩文化内涵'),
        ]:
            move = self.create_move(m1, name, desc, diff, dur, oi, fp, cm, kp, pc)
            self.create_resource(move, 'video', f'{name}基础教学', 280)
            self.create_knowledge_point(move, '傩面文化', '了解傩面的文化内涵', '文化内涵', 5)

    def _generate_lantern_dance(self, project, dance_name):
        self.stdout.write(f'  → {dance_name} (花灯类)')
        m1 = self.create_module(project, '基本手势模块', f'{dance_name}的手部动作和手势变化。', 1)
        for name, desc, diff, dur, oi, fp, cm, kp, pc in [
            ('兰花指', '拇指与中指相捏，其余三指自然舒展，形如兰花。是典型手型。', 2, 240, 1, '手指、手腕', '手指僵硬、手型不标准', '手指自然弯曲，拇指中指相捏', '需要经常练习手指灵活性'),
            ('云手', '双手在胸前划圆，如云卷云舒，动作优美流畅。', 3, 300, 2, '手臂、腰部、手腕', '划圆不流畅、手臂僵硬', '以腰带动，手臂划圆流畅', '先慢练体会动作路线'),
        ]:
            move = self.create_move(m1, name, desc, diff, dur, oi, fp, cm, kp, pc)
            self.create_resource(move, 'video', f'{name}手势教学', 200)
            self.create_knowledge_point(move, '手型规范', '掌握标准手型', '基础技法', 5)

    def _generate_tibetan_dance(self, project, dance_name):
        self.stdout.write(f'  → {dance_name} (藏族舞蹈类)')
        m1 = self.create_module(project, '基本步法模块', f'{dance_name}的基础步伐训练。', 1)
        for name, desc, diff, dur, oi, fp, cm, kp, pc in [
            ('颤膝步', '双膝有节奏地颤动，步伐轻盈，是藏族舞蹈的典型步法。', 3, 300, 1, '腿部、膝盖', '颤动不自然、节奏不稳', '颤动自然，节奏均匀，步伐轻盈', '注意膝盖的放松'),
            ('踏步', '双脚交替踏地，动作有力，展现藏族人民的豪迈性格。', 3, 280, 2, '腿部、脚部', '踏步无力、节奏混乱', '踏步有力，节奏明快，身体协调', '注意重心的平稳转移'),
        ]:
            move = self.create_move(m1, name, desc, diff, dur, oi, fp, cm, kp, pc)
            self.create_resource(move, 'video', f'{name}基础教学', 240)
            self.create_knowledge_point(move, '藏族舞蹈韵律', '掌握藏族舞蹈的独特韵律', '基础技法', 5)

    def _generate_baishou_dance(self, project, dance_name):
        self.stdout.write(f'  → {dance_name} (摆手舞类)')
        m1 = self.create_module(project, '基本摆手模块', f'{dance_name}的基础摆手动作。', 1)
        for name, desc, diff, dur, oi, fp, cm, kp, pc in [
            ('单摆手', '单手在体侧摆动，配合脚步移动，动作自然流畅。', 2, 280, 1, '手臂、肩部', '摆动不自然、身体僵硬', '摆动自然，身体放松，节奏平稳', '注意肩部的放松'),
            ('双摆手', '双手同时摆动，动作幅度大，展现摆手舞的豪放特点。', 3, 320, 2, '手臂、肩部、腰部', '摆动不协调、节奏不稳', '双手协调，动作幅度大，节奏明快', '注意身体的配合'),
        ]:
            move = self.create_move(m1, name, desc, diff, dur, oi, fp, cm, kp, pc)
            self.create_resource(move, 'video', f'{name}基础教学', 240)
            self.create_knowledge_point(move, '摆手技法', '掌握摆手的基本技法', '基础技法', 5)

    def _generate_folk_dance(self, project, dance_name):
        self.stdout.write(f'  → {dance_name} (民间舞蹈)')
        m1 = self.create_module(project, '基本步法模块', f'{dance_name}的基础步伐训练。', 1)
        for name, desc, diff, dur, oi, fp, cm, kp, pc in [
            ('基本步', f'{dance_name}的基础步伐，要求步伐稳健，节奏明快。', 2, 280, 1, '腿部、脚部', '步伐不稳、节奏混乱', '步伐稳健，节奏明快，重心稳定', '先慢练熟悉步伐路线'),
            ('交叉步', '双脚交叉行进，动作灵活，是民间舞蹈的常见步法。', 3, 300, 2, '腿部、脚部、腰部', '交叉不流畅、身体不协调', '交叉流畅，身体协调，节奏均匀', '注意重心的平稳转移'),
        ]:
            move = self.create_move(m1, name, desc, diff, dur, oi, fp, cm, kp, pc)
            self.create_resource(move, 'video', f'{name}基础教学', 240)
            self.create_knowledge_point(move, '基础步法', '掌握该舞蹈的基本步法', '基础技法', 5)
        
        m2 = self.create_module(project, '身段韵律模块', f'{dance_name}的身段变化和韵律表达。', 2)
        for name, desc, diff, dur, oi, fp, cm, kp, pc in [
            ('基本身段', f'{dance_name}的基本身体姿态，展现舞蹈的优美风格。', 3, 300, 1, '腰部、胸部', '身段不自然、身体僵硬', '身段自然，姿态优美，气息配合', '注意身体的放松'),
            ('旋转动作', '原地旋转，动作流畅优美。是舞蹈的常见表现手法。', 4, 340, 2, '全身协调、腰部', '旋转不稳、动作不协调', '旋转流畅，身体协调，姿态优美', '先练旋转平衡'),
        ]:
            move = self.create_move(m2, name, desc, diff, dur, oi, fp, cm, kp, pc)
            self.create_resource(move, 'video', f'{name}身段教学', 260)
            self.create_knowledge_point(move, '身段造型', '掌握该舞蹈的标准身段', '基础技法', 5)
