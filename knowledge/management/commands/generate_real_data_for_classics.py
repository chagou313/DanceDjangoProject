"""
为指定的经典舞蹈项目生成真实数据
使用方法: python manage.py generate_real_data_for_classics
"""
from django.core.management.base import BaseCommand
from knowledge.models import DanceProject, ActionModule, SpecificMove, MoveAttribute, LearningResource, KnowledgePoint
from origin.models import DanceProject as OriginDanceProject


class Command(BaseCommand):
    help = '为经典舞蹈生成真实数据'

    CLASSIC_DANCES = [
        '安塞腰鼓', '傣族孔雀舞', '秧歌（胶州秧歌）', '永新盾牌舞', '花鼓灯（蚌埠花鼓灯）',
        '京西太平鼓', '龙舞（铜梁龙舞）', '狮舞（徐水舞狮）', '傩舞（南丰跳傩）', '秧歌（昌黎地秧歌）'
    ]

    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS('=' * 70))
        self.stdout.write(self.style.SUCCESS('为经典舞蹈项目生成真实数据'))
        self.stdout.write(self.style.SUCCESS('=' * 70))
        self.stdout.write(f'\n将为以下 {len(self.CLASSIC_DANCES)} 个经典项目生成数据:')
        for i, name in enumerate(self.CLASSIC_DANCES, 1):
            self.stdout.write(f'  {i}. {name}')
        
        confirm = input('\n是否继续？(y/n): ').strip().lower()
        if confirm != 'y':
            return
        
        # 清除旧数据
        self.stdout.write(self.style.WARNING('\n清除旧数据...'))
        KnowledgePoint.objects.all().delete()
        LearningResource.objects.all().delete()
        MoveAttribute.objects.all().delete()
        SpecificMove.objects.all().delete()
        ActionModule.objects.all().delete()
        DanceProject.objects.all().delete()
        self.stdout.write(self.style.SUCCESS('✓ 完成\n'))
        
        # 为每个经典项目生成数据
        for dance_name in self.CLASSIC_DANCES:
            try:
                origin_project = OriginDanceProject.objects.filter(name=dance_name).first()
                if not origin_project:
                    self.stdout.write(self.style.WARNING(f'跳过: {dance_name} (不在数据库中)'))
                    continue
                
                kp_project, _ = DanceProject.objects.get_or_create(
                    name=origin_project.name,
                    defaults={
                        'description': origin_project.introduction or '',
                        'category': origin_project.get_dance_type_display(),
                        'difficulty_level': 3,
                    }
                )
                ActionModule.objects.filter(dance_project=kp_project).delete()
                
                self.generate_for_dance(kp_project, dance_name)
                self.stdout.write(self.style.SUCCESS(f'✓ {dance_name}'))
            except Exception as e:
                self.stdout.write(self.style.ERROR(f'✗ {dance_name}: {e}'))
        
        # 统计
        self.stdout.write('\n' + '=' * 70)
        self.stdout.write(self.style.SUCCESS('完成!'))
        self.stdout.write(f'项目: {DanceProject.objects.count()}')
        self.stdout.write(f'模块: {ActionModule.objects.count()}')
        self.stdout.write(f'招式: {SpecificMove.objects.count()}')
        self.stdout.write(f'资源: {LearningResource.objects.count()}')
        self.stdout.write(f'知识点: {KnowledgePoint.objects.count()}')

    def create_module(self, project, name, desc, order):
        return ActionModule.objects.create(dance_project=project, name=name, description=desc, order_index=order)

    def create_move(self, module, name, desc, diff, dur, order, fp='', cm='', kp='', pc=''):
        move = SpecificMove.objects.create(action_module=module, name=name, description=desc, difficulty=diff, duration=dur, order_index=order)
        if fp or cm or kp or pc:
            MoveAttribute.objects.create(specific_move=move, force_parts=fp, common_mistakes=cm, key_points=kp, precautions=pc)
        return move

    def create_resource(self, move, rtype, title, dur=None):
        return LearningResource.objects.create(specific_move=move, resource_type=rtype, title=title, url='', duration=dur)

    def create_kp(self, move, name, desc, cat, level):
        return KnowledgePoint.objects.create(specific_move=move, name=name, description=desc, category=cat, importance_level=level)

    def generate_for_dance(self, project, name):
        """根据舞蹈名称生成专属数据"""
        if '安塞腰鼓' in name:
            self._ansai(project, name)
        elif '孔雀' in name:
            self._peacock(project, name)
        elif '胶州' in name:
            self._jiaozhou(project, name)
        elif '盾牌' in name:
            self._shield(project, name)
        elif '花鼓灯' in name:
            self._huagudeng(project, name)
        elif '太平鼓' in name:
            self._taiping(project, name)
        elif '铜梁龙' in name:
            self._dragon(project, name)
        elif '徐水' in name or '狮舞' in name:
            self._lion(project, name)
        elif '南丰' in name or '跳傩' in name:
            self._nuo(project, name)
        elif '昌黎' in name:
            self._folk(project, name)
        else:
            self._folk(project, name)

    def _ansai(self, p, n):
        m1 = self.create_module(p, '基本鼓法', f'{n}的基础击鼓技法，包括单点、双点、滚奏等，是黄土高原文化的代表。', 1)
        for nm, ds, df, dr, oi, fp, cm, kp, pc in [
            ('单点击鼓', '右手持鼓槌，以腕部发力单击鼓面中心，发出清脆响亮的声音。是安塞腰鼓最基础的技法，源于明代军旅鼓乐。', 2, 300, 1, '手腕、前臂', '手臂僵硬、击点不准', '以腕发力，击鼓中心，声脆节奏准', '先练手腕灵活性'),
            ('双点连击', '连续两次快速击鼓形成"咚咚"节奏型，间隔均匀。表现腰鼓节奏感的重要技法。', 3, 360, 2, '手腕、手指', '力度不均、间隔不稳', '手腕带动，力度均匀，节奏稳定', '先慢练再加速'),
            ('花点滚奏', '手腕快速旋转带动鼓槌在鼓面连续滚动击打，发出密集鼓声。高难度技巧需长期练习。', 5, 420, 3, '手腕、前臂、手指', '滚奏不连续、鼓声不均', '手腕放松旋转，鼓槌弹性好，节奏匀', '需先掌握单双点'),
        ]:
            mv = self.create_move(m1, nm, ds, df, dr, oi, fp, cm, kp, pc)
            self.create_resource(mv, 'video', f'{nm}分解教学', 240)
            self.create_resource(mv, 'demo', f'传承人{nm}示范', 180)
            self.create_kp(mv, '手腕发力', '掌握以腕为主的击鼓发力技巧', '基础技法', 5)
            self.create_kp(mv, '节奏控制', '培养准确的节奏感', '音乐素养', 5)
        
        m2 = self.create_module(p, '跳跃腾挪', f'{n}特色的跳跃动作，展现黄土高原人民的豪迈性格。', 2)
        for nm, ds, df, dr, oi, fp, cm, kp, pc in [
            ('蹬腿跳跃', '单腿蹬地跃起同时击鼓，落地稳健。体现安塞腰鼓的阳刚之气，源于古代战阵鼓舞。', 4, 360, 1, '腿部、腰部、核心', '跳跃低、落地不稳、击鼓时机错', '蹬地有力，跳跃协调，落地稳击鼓准', '注意膝盖保护'),
            ('转身飞槌', '原地旋转360度同时挥动鼓槌击鼓，动作连贯有力。是最具视觉冲击力的动作。', 5, 420, 2, '全身协调、腰部、手臂', '旋转不稳、击鼓不准、头晕', '以腰为轴旋转流畅，击鼓准确', '先练旋转平衡'),
        ]:
            mv = self.create_move(m2, nm, ds, df, dr, oi, fp, cm, kp, pc)
            self.create_resource(mv, 'video', f'{nm}完整演示', 300)
            self.create_kp(mv, '腿部力量', '增强腿部爆发力和耐力', '身体素质', 4)
            self.create_kp(mv, '平衡能力', '掌握跳跃旋转中的平衡', '技能要点', 5)
        
        m3 = self.create_module(p, '队形阵法', f'{n}集体表演的队形编排，展现群体舞蹈壮观场面。', 3)
        for nm, ds, df, dr, oi, fp, cm, kp, pc in [
            ('四门斗底阵', '四人一组形成四方阵型，相互呼应节奏统一。是安塞腰鼓最经典的传统阵法。', 4, 480, 1, '全身协调、团队配合', '阵型不齐、节奏不统、配合差', '阵型规整，节奏统一，相互配合', '需多次排练培养默契'),
            ('双龙出海阵', '两队交错行进如两条龙穿梭，队形变化复杂气势磅礴。大型表演常用阵法。', 5, 540, 2, '全身协调、空间感知', '队形混乱、碰撞、节奏不一', '行进路线清晰，保持距离，节奏统', '先分队练再合练'),
        ]:
            mv = self.create_move(m3, nm, ds, df, dr, oi, fp, cm, kp, pc)
            self.create_resource(mv, 'video', f'{nm}编排教学', 360)
            self.create_kp(mv, '团队协作', '培养集体舞蹈的默契配合', '表演技巧', 5)
            self.create_kp(mv, '阵法文化', '了解传统阵法的文化内涵', '文化内涵', 4)

    def _peacock(self, p, n):
        m1 = self.create_module(p, '基本手型', f'{n}的手部造型，是傣族舞蹈最核心的表现手段。', 1)
        for nm, ds, df, dr, oi, fp, cm, kp, pc in [
            ('孔雀手型', '拇指与食指捏成圆形，其余三指自然展开形如孔雀头部。是孔雀舞最具标志性的手型。', 2, 240, 1, '手指、手腕', '手指僵硬、手型不标准', '拇指食指捏圆，三指舒展，手腕放松', '常练手指灵活性'),
            ('展翅手型', '双手在胸前或头顶展开，手指张开模拟孔雀展翅。动作舒展优美表现高贵气质。', 3, 300, 2, '手指、手臂、肩部', '展开不充分、手臂僵硬', '手臂舒展，手指张开，姿态优雅', '注意肩部放松打开'),
            ('饮水手型', '手指并拢向前伸出模拟孔雀低头饮水。手腕柔软动作流畅自然。', 3, 280, 3, '手指、手腕、手臂', '手指不并拢、手腕僵硬', '手指并拢，手腕柔软，动作流畅', '先慢练体会路线'),
        ]:
            mv = self.create_move(m1, nm, ds, df, dr, oi, fp, cm, kp, pc)
            self.create_resource(mv, 'video', f'{nm}基础教学', 200)
            self.create_kp(mv, '手型规范', '掌握孔雀舞标准手型', '基础技法', 5)
            self.create_kp(mv, '手指灵活', '提高手指控制能力', '身体素质', 4)
        
        m2 = self.create_module(p, '身段韵律', f'{n}的身体姿态，展现傣族舞蹈S曲线美感。', 2)
        for nm, ds, df, dr, oi, fp, cm, kp, pc in [
            ('三道弯', '身体呈现头、胸、腰三段弯曲的S型姿态。是傣族舞蹈典型身段，要求柔韧性好。', 5, 420, 1, '腰部、胸部、颈部', '弯曲不自然、三段不协调', '三段弯曲自然流畅，姿态优美', '需先练腰部柔韧'),
            ('孔雀步', '双脚交替前行步伐轻盈优雅，身体微微晃动模拟孔雀行走姿态。', 3, 300, 2, '腿部、脚部、腰部', '步伐沉重、晃动过大', '步伐轻盈，身体微晃，节奏平稳', '注意重心平稳转移'),
        ]:
            mv = self.create_move(m2, nm, ds, df, dr, oi, fp, cm, kp, pc)
            self.create_resource(mv, 'video', f'{nm}身段教学', 280)
            self.create_resource(mv, 'demo', '傣族传承人示范', 240)
            self.create_kp(mv, '三道弯体态', '掌握傣族舞蹈S曲线美感', '基础技法', 5)
            self.create_kp(mv, '柔韧训练', '提高身体柔韧和控制力', '训练方法', 4)
        
        m3 = self.create_module(p, '孔雀模仿', f'{n}模仿孔雀各种姿态，是舞蹈灵魂所在。', 3)
        for nm, ds, df, dr, oi, fp, cm, kp, pc in [
            ('孔雀开屏', '双臂在身后展开手指张开，身体微后仰模拟开屏壮观场面。', 4, 360, 1, '手臂、背部、手指', '展开不充分、姿态不美', '双臂展开手指张开，表情陶醉', '需充分肩背柔韧'),
            ('梳理羽毛', '双手在身体两侧做梳理动作模拟孔雀用嘴梳理羽毛。动作细腻优雅。', 3, 300, 2, '手臂、手腕、手指', '动作粗糙、不够细腻', '动作轻柔细腻，节奏舒缓', '注意手腕灵活运用'),
        ]:
            mv = self.create_move(m3, nm, ds, df, dr, oi, fp, cm, kp, pc)
            self.create_resource(mv, 'video', f'{nm}模仿教学', 300)
            self.create_kp(mv, '动物模仿', '掌握动物姿态模仿技巧', '表演技巧', 5)
            self.create_kp(mv, '表情管理', '培养舞蹈中表情表达', '表演技巧', 4)

    def _jiaozhou(self, p, n):
        m1 = self.create_module(p, '基本步法', f'{n}的基础步伐，包括十字步、扭步、滑步等。', 1)
        for nm, ds, df, dr, oi, fp, cm, kp, pc in [
            ('十字步', '双脚交叉行进形成十字轨迹，是胶州秧歌典型步法。要求步伐稳健有力节奏明快。', 3, 300, 1, '腿部、脚部', '步伐混乱、重心不稳', '步伐清晰，重心稳定，节奏明快', '先慢练熟悉路线'),
            ('扭步', '双脚交替扭动前行，身体随之左右摇摆，展现"扭"的特点。', 3, 280, 2, '腿部、腰部、脚部', '扭动不自然、身体僵硬', '扭动自然，身体放松，节奏均匀', '注意腰部灵活运用'),
        ]:
            mv = self.create_move(m1, nm, ds, df, dr, oi, fp, cm, kp, pc)
            self.create_resource(mv, 'video', f'{nm}基础教学', 240)
            self.create_kp(mv, '基础步法', '掌握秧歌基本步法', '基础技法', 5)
            self.create_kp(mv, '节奏感', '培养舞蹈节奏感', '音乐素养', 5)
        
        m2 = self.create_module(p, '手绢花', f'{n}的手绢花技法，是秧歌重要道具和表现手段。', 2)
        for nm, ds, df, dr, oi, fp, cm, kp, pc in [
            ('转绢花', '手腕旋转带动手绢形成花型，动作灵活优美。是胶州秧歌标志性技法。', 4, 300, 1, '手腕、手指', '手绢转不起来、动作僵硬', '手腕灵活，手指配合，旋转流畅', '需反复练手腕灵活'),
            ('抛绢花', '将手绢向上抛起再接住，动作轻盈准确。展现表演者技巧和自信。', 4, 280, 2, '手腕、手臂、眼手协调', '抛不准、接不住', '抛得稳，接得准，动作流畅', '先低抛练再加高'),
        ]:
            mv = self.create_move(m2, nm, ds, df, dr, oi, fp, cm, kp, pc)
            self.create_resource(mv, 'video', f'{nm}技巧教学', 220)
            self.create_kp(mv, '手绢技法', '掌握手绢花基本技法', '技能要点', 5)
            self.create_kp(mv, '手腕灵活', '提高手腕灵活控制力', '身体素质', 4)
        
        m3 = self.create_module(p, '身段韵律', f'{n}的身体姿态，展现胶东女性柔美。', 3)
        for nm, ds, df, dr, oi, fp, cm, kp, pc in [
            ('扭摆身段', '身体左右扭摆配合脚步动作，展现"扭、摆"特点。姿态优美节奏明快。', 4, 320, 1, '腰部、胸部、颈部', '扭摆不自然、身体僵硬', '扭摆自然，身体放松，节奏明快', '注意腰部带动'),
            ('扇形手', '双手在胸前或头顶展开形成扇形，配合身体扭摆。展现优美身段。', 3, 280, 2, '手臂、手腕、手指', '展开不充分、手型不标准', '双手展开，手型标准，姿态优美', '注意手臂舒展'),
        ]:
            mv = self.create_move(m3, nm, ds, df, dr, oi, fp, cm, kp, pc)
            self.create_resource(mv, 'video', f'{nm}身段教学', 260)
            self.create_resource(mv, 'demo', '胶州秧歌传承人示范', 300)
            self.create_kp(mv, '身段造型', '掌握胶州秧歌标准身段', '基础技法', 5)
            self.create_kp(mv, '韵律表达', '培养舞蹈韵律感', '表演技巧', 5)

    def _shield(self, p, n):
        m1 = self.create_module(p, '基本武术', f'{n}的基础武术动作和站桩训练。', 1)
        for nm, ds, df, dr, oi, fp, cm, kp, pc in [
            ('马步站桩', '双脚分开与肩同宽，屈膝下蹲成马步，双手持盾稳如泰山。是盾牌舞基本功。', 3, 360, 1, '腿部、腰部、核心', '马步不稳、重心偏移', '马步扎实，重心稳定，身体正直', '初学者时间不宜长'),
            ('弓步推盾', '前腿弓后腿绷，双手持盾向前推展现进攻姿态。动作刚劲有力。', 4, 320, 2, '腿部、手臂、腰部', '弓步不稳、推盾无力', '弓步扎实，推盾有力，身体协调', '注意前后腿比例'),
        ]:
            mv = self.create_move(m1, nm, ds, df, dr, oi, fp, cm, kp, pc)
            self.create_resource(mv, 'video', f'{nm}基础训练', 280)
            self.create_kp(mv, '站桩基本功', '掌握传统武术站桩要领', '基础技法', 5)
            self.create_kp(mv, '腿部力量', '增强腿部力量和稳定性', '身体素质', 4)
        
        m2 = self.create_module(p, '盾牌技法', f'{n}的盾牌运用和防守技法。', 2)
        for nm, ds, df, dr, oi, fp, cm, kp, pc in [
            ('盾牌格挡', '运用盾牌进行上下左右格挡防守，动作敏捷灵活。是核心技法。', 4, 360, 1, '手臂、腰部、反应能力', '格挡不及时、位置不对', '反应敏捷，盾牌到位，动作流畅', '需先练基本反应速度'),
            ('盾牌旋转', '手持盾牌快速旋转形成防御屏障，同时保持移动。高难度技巧。', 5, 380, 2, '手臂、腰部、全身协调', '旋转不稳、盾牌失控', '旋转流畅，盾牌稳定，身体协调', '先慢练旋转再加快速度'),
        ]:
            mv = self.create_move(m2, nm, ds, df, dr, oi, fp, cm, kp, pc)
            self.create_resource(mv, 'video', f'{nm}技巧讲解', 300)
            self.create_kp(mv, '防守技法', '掌握盾牌防守基本方法', '技能要点', 5)
            self.create_kp(mv, '反应能力', '提高身体反应速度', '身体素质', 4)

    def _huagudeng(self, p, n):
        m1 = self.create_module(p, '基本手势', f'{n}的手部动作和手势变化，展现灵动优美。', 1)
        for nm, ds, df, dr, oi, fp, cm, kp, pc in [
            ('兰花指', '拇指与中指相捏，其余三指自然舒展形如兰花。是花鼓灯和汉族舞蹈典型手型。', 2, 240, 1, '手指、手腕', '手指僵硬、手型不标准', '手指自然弯曲，拇指中指相捏', '需常练手指灵活性'),
            ('云手', '双手在胸前划圆如云卷云舒，动作优美流畅。展现花鼓灯柔美特点。', 3, 300, 2, '手臂、腰部、手腕', '划圆不流畅、手臂僵硬', '以腰带动，手臂划圆流畅', '先慢练体会路线'),
        ]:
            mv = self.create_move(m1, nm, ds, df, dr, oi, fp, cm, kp, pc)
            self.create_resource(mv, 'video', f'{nm}手势教学', 200)
            self.create_kp(mv, '手型规范', '掌握标准手型要求', '基础技法', 5)
            self.create_kp(mv, '手腕灵活', '提高手腕灵活性', '身体素质', 4)
        
        m2 = self.create_module(p, '鼓点节奏', f'{n}的鼓点敲击技法和节奏训练。', 2)
        for nm, ds, df, dr, oi, fp, cm, kp, pc in [
            ('单点击鼓', '右手持鼓槌单击鼓面发出清脆鼓声。是花鼓灯基础击鼓技法。', 2, 280, 1, '手腕、前臂', '击鼓位置不准、力度过大', '击鼓中心，声音清脆，节奏准确', '先练节奏感'),
            ('双点连击', '连续两次击鼓形成"咚咚"节奏型。是花鼓灯常用节奏型。', 3, 300, 2, '手腕、手指', '力度不均、间隔不稳定', '力度均匀，节奏稳定', '先慢练再加速'),
        ]:
            mv = self.create_move(m2, nm, ds, df, dr, oi, fp, cm, kp, pc)
            self.create_resource(mv, 'video', f'{nm}鼓点教学', 240)
            self.create_kp(mv, '节奏型掌握', '学习基本鼓点节奏型', '音乐素养', 5)
            self.create_kp(mv, '手腕发力', '掌握以腕为主击鼓技巧', '基础技法', 5)
        
        m3 = self.create_module(p, '身段韵律', f'{n}的身段变化，展现江淮舞蹈优美姿态。', 3)
        for nm, ds, df, dr, oi, fp, cm, kp, pc in [
            ('三道弯', '身体呈现头、胸、腰三段弯曲S型姿态，展现女性柔美。是花鼓灯典型身段。', 4, 360, 1, '腰部、胸部、颈部', '弯曲不自然、三段不协调', '三段弯曲自然流畅，姿态优美', '需先练腰部柔韧'),
            ('扭摆步', '身体左右扭摆配合脚步移动，展现花鼓灯韵律美。', 3, 300, 2, '腰部、腿部、脚部', '扭摆不自然、身体僵硬', '扭摆自然，身体放松，节奏平稳', '注意腰部带动'),
        ]:
            mv = self.create_move(m3, nm, ds, df, dr, oi, fp, cm, kp, pc)
            self.create_resource(mv, 'video', f'{nm}身段教学', 280)
            self.create_resource(mv, 'demo', '花鼓灯传承人示范', 320)
            self.create_kp(mv, '身段造型', '掌握花鼓灯标准身段', '基础技法', 5)
            self.create_kp(mv, '韵律表达', '培养舞蹈韵律感', '表演技巧', 5)

    def _taiping(self, p, n):
        m1 = self.create_module(p, '基本鼓法', f'{n}的基础击鼓技法。', 1)
        for nm, ds, df, dr, oi, fp, cm, kp, pc in [
            ('单点击鼓', '右手持鼓槌单击鼓面中心，发出清脆响亮声音。是太平鼓基础技法。', 2, 300, 1, '手腕、前臂', '手臂僵硬、击点不准', '以腕发力，击鼓中心，声脆', '先练手腕灵活性'),
            ('双点连击', '连续两次快速击鼓形成"咚咚"节奏型，间隔均匀。', 3, 360, 2, '手腕、手指', '力度不均、间隔不稳', '手腕带动，力度均匀，节奏稳', '先慢练再加速'),
        ]:
            mv = self.create_move(m1, nm, ds, df, dr, oi, fp, cm, kp, pc)
            self.create_resource(mv, 'video', f'{nm}分解教学', 240)
            self.create_kp(mv, '手腕发力', '掌握以腕为主发力技巧', '基础技法', 5)
            self.create_kp(mv, '节奏控制', '培养准确节奏感', '音乐素养', 5)
        
        m2 = self.create_module(p, '跳跃动作', f'{n}特色的跳跃腾挪动作。', 2)
        for nm, ds, df, dr, oi, fp, cm, kp, pc in [
            ('蹬腿跳跃', '单腿蹬地跃起同时击鼓，落地稳健。体现民间舞蹈豪迈性格。', 4, 360, 1, '腿部、腰部、核心', '跳跃低、落地不稳', '蹬地有力，跳跃协调，落地稳', '注意膝盖保护'),
            ('转身飞槌', '原地旋转360度同时挥动鼓槌击鼓，动作连贯有力。', 5, 420, 2, '全身协调、腰部、手臂', '旋转不稳、击鼓不准', '以腰为轴旋转流畅，击鼓准', '先练旋转平衡'),
        ]:
            mv = self.create_move(m2, nm, ds, df, dr, oi, fp, cm, kp, pc)
            self.create_resource(mv, 'video', f'{nm}完整演示', 300)
            self.create_kp(mv, '腿部力量', '增强腿部爆发力', '身体素质', 4)
            self.create_kp(mv, '平衡能力', '掌握旋转中平衡', '技能要点', 5)

    def _dragon(self, p, n):
        m1 = self.create_module(p, '基本龙舞', f'{n}的基础龙舞动作。', 1)
        for nm, ds, df, dr, oi, fp, cm, kp, pc in [
            ('游龙', '舞龙者持龙杆步伐协调，使龙身呈现游动姿态。', 3, 360, 1, '全身协调、手臂力量', '龙身不流畅、步伐混乱', '步伐稳健，龙身流畅，团队配合', '需多次排练培养默契'),
            ('盘龙', '龙身盘旋上升形成螺旋状，展现龙的雄伟气势。', 4, 420, 2, '全身协调、腰部', '盘旋不流畅、龙身打结', '盘旋流畅，龙身舒展，气势磅礴', '需熟练掌握龙杆操作'),
        ]:
            mv = self.create_move(m1, nm, ds, df, dr, oi, fp, cm, kp, pc)
            self.create_resource(mv, 'video', f'{nm}基础教学', 300)
            self.create_kp(mv, '龙杆操控', '掌握龙杆基本操控技巧', '技能要点', 5)
            self.create_kp(mv, '团队协作', '培养集体舞蹈默契配合', '表演技巧', 5)

    def _lion(self, p, n):
        m1 = self.create_module(p, '基本狮舞', f'{n}的基础狮舞动作。', 1)
        for nm, ds, df, dr, oi, fp, cm, kp, pc in [
            ('醒狮', '狮子从沉睡中苏醒，伸懒腰打哈欠，动作生动有趣。', 3, 300, 1, '全身协调、手臂', '动作不连贯、缺乏生气', '动作连贯，表情生动，富有生命力', '需两人默契配合'),
            ('采青', '狮子发现食物小心翼翼靠近最终获取，展现狮子机敏。', 4, 360, 2, '腿部、腰部、全身协调', '动作笨拙、缺乏技巧', '动作灵活，表现机敏，层次分明', '需反复排练'),
        ]:
            mv = self.create_move(m1, nm, ds, df, dr, oi, fp, cm, kp, pc)
            self.create_resource(mv, 'video', f'{nm}基础教学', 280)
            self.create_kp(mv, '狮头操控', '掌握狮头基本操控技巧', '技能要点', 5)
            self.create_kp(mv, '团队配合', '培养两人默契配合', '表演技巧', 5)

    def _nuo(self, p, n):
        m1 = self.create_module(p, '基本傩舞', f'{n}的基础傩舞动作，具有浓厚祭祀色彩。', 1)
        for nm, ds, df, dr, oi, fp, cm, kp, pc in [
            ('傩面舞步', '佩戴傩面步伐沉稳有力，展现神灵威严。', 3, 300, 1, '腿部、脚部', '步伐不稳、缺乏威严', '步伐沉稳，姿态威严，节奏庄重', '需先适应傩面重量'),
            ('驱邪动作', '双手持法器做出驱邪赶鬼动作，气势磅礴。', 4, 360, 2, '手臂、腰部、全身', '动作不连贯、缺乏气势', '动作有力，气势磅礴，节奏统一', '需充分理解傩文化内涵'),
        ]:
            mv = self.create_move(m1, nm, ds, df, dr, oi, fp, cm, kp, pc)
            self.create_resource(mv, 'video', f'{nm}基础教学', 280)
            self.create_kp(mv, '傩面文化', '了解傩面文化内涵', '文化内涵', 5)
            self.create_kp(mv, '祭祀舞蹈', '理解祭祀舞蹈的文化意义', '文化内涵', 4)

    def _folk(self, p, n):
        m1 = self.create_module(p, '基本步法', f'{n}的基础步伐训练。', 1)
        for nm, ds, df, dr, oi, fp, cm, kp, pc in [
            ('基本步', f'{n}的基础步伐，要求步伐稳健节奏明快。', 2, 280, 1, '腿部、脚部', '步伐不稳、节奏混乱', '步伐稳健，节奏明快，重心稳定', '先慢练熟悉路线'),
            ('交叉步', '双脚交叉行进动作灵活，是民间舞蹈常见步法。', 3, 300, 2, '腿部、脚部、腰部', '交叉不流畅、身体不协调', '交叉流畅，身体协调，节奏均匀', '注意重心平稳转移'),
        ]:
            mv = self.create_move(m1, nm, ds, df, dr, oi, fp, cm, kp, pc)
            self.create_resource(mv, 'video', f'{nm}基础教学', 240)
            self.create_kp(mv, '基础步法', '掌握该舞蹈基本步法', '基础技法', 5)
        
        m2 = self.create_module(p, '身段韵律', f'{n}的身段变化和韵律表达。', 2)
        for nm, ds, df, dr, oi, fp, cm, kp, pc in [
            ('基本身段', f'{n}的基本身体姿态，展现舞蹈优美风格。', 3, 300, 1, '腰部、胸部', '身段不自然、身体僵硬', '身段自然，姿态优美，气息配合', '注意身体放松'),
            ('旋转动作', '原地旋转动作流畅优美。是舞蹈常见表现手法。', 4, 340, 2, '全身协调、腰部', '旋转不稳、动作不协调', '旋转流畅，身体协调，姿态优美', '先练旋转平衡'),
        ]:
            mv = self.create_move(m2, nm, ds, df, dr, oi, fp, cm, kp, pc)
            self.create_resource(mv, 'video', f'{nm}身段教学', 260)
            self.create_kp(mv, '身段造型', '掌握该舞蹈标准身段', '基础技法', 5)
            self.create_kp(mv, '韵律表达', '培养舞蹈韵律感', '表演技巧', 5)
