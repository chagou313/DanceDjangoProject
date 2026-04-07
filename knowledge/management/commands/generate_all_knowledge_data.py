"""
一键清除旧数据并重新生成全部356个非遗舞蹈项目知识图谱数据
使用方法: python manage.py generate_all_knowledge_data --clear
"""
import time
from django.core.management.base import BaseCommand
from django.db import transaction
from knowledge.models import DanceProject, ActionModule, SpecificMove, MoveAttribute, LearningResource, KnowledgePoint
from origin.models import DanceProject as OriginDanceProject


class Command(BaseCommand):
    help = '一次性生成全部356个非遗舞蹈项目知识图谱数据'

    def add_arguments(self, parser):
        parser.add_argument('--clear', action='store_true', help='生成前先清除所有旧数据')
        parser.add_argument('--batch-size', type=int, default=20, help='每处理多少个批次显示一次进度')

    def handle(self, *args, **options):
        start_time = time.time()
        
        if options['clear']:
            self.clear_data()
            
        self.stdout.write(self.style.SUCCESS('=' * 70))
        self.stdout.write(self.style.SUCCESS('开始生成全部非遗舞蹈知识图谱数据'))
        self.stdout.write(self.style.SUCCESS('=' * 70))
        
        # 获取原始项目
        origin_projects = OriginDanceProject.objects.all().order_by('id')
        total = origin_projects.count()
        self.stdout.write(f'从 origin 数据库加载 {total} 个真实非遗项目\n')
        
        success_count = 0
        fail_count = 0
        fail_names = []
        
        for i, op in enumerate(origin_projects, 1):
            try:
                with transaction.atomic():
                    self.create_project_data(op)
                success_count += 1
            except Exception as e:
                fail_count += 1
                fail_names.append(op.name)
                self.stdout.write(self.style.ERROR(f'[{i}/{total}] ✗ {op.name} 失败: {str(e)[:80]}'))
            
            # 进度提示
            if i % options['batch_size'] == 0 or i == total:
                elapsed = time.time() - start_time
                self.stdout.write(f'📊 进度: {i}/{total} | 成功: {success_count} | 失败: {fail_count} | 耗时: {elapsed:.1f}s')
        
        # 最终统计
        elapsed = time.time() - start_time
        self.stdout.write(self.style.SUCCESS('\n' + '=' * 70))
        self.stdout.write(self.style.SUCCESS(f'✅ 数据生成完成！'))
        self.stdout.write(f'📈 成功: {success_count} 个项目')
        self.stdout.write(f'❌ 失败: {fail_count} 个项目')
        self.stdout.write(f'⏱️  总耗时: {elapsed:.1f} 秒')
        
        if fail_names:
            self.stdout.write(self.style.WARNING('\n⚠️  失败项目列表:'))
            for name in fail_names[:10]:
                self.stdout.write(f'   - {name}')
            if len(fail_names) > 10:
                self.stdout.write(f'   ... 还有 {len(fail_names) - 10} 个')
                
        self.stdout.write(self.style.SUCCESS('=' * 70))
        
        # 打印数据库最终统计
        self.print_final_stats()

    def clear_data(self):
        """清除所有知识图谱数据"""
        self.stdout.write(self.style.WARNING('\n⚠️  正在清除旧数据...'))
        KnowledgePoint.objects.all().delete()
        LearningResource.objects.all().delete()
        MoveAttribute.objects.all().delete()
        SpecificMove.objects.all().delete()
        ActionModule.objects.all().delete()
        DanceProject.objects.all().delete()
        self.stdout.write(self.style.SUCCESS('✓ 旧数据已清除\n'))

    def print_final_stats(self):
        """打印最终统计信息"""
        projects = DanceProject.objects.count()
        modules = ActionModule.objects.count()
        moves = SpecificMove.objects.count()
        resources = LearningResource.objects.count()
        kps = KnowledgePoint.objects.count()
        
        self.stdout.write('\n📊 数据库最终统计:')
        self.stdout.write(f'   舞蹈项目: {projects}')
        self.stdout.write(f'   动作模块: {modules}')
        self.stdout.write(f'   具体招式: {moves}')
        self.stdout.write(f'   学习资源: {resources}')
        self.stdout.write(f'   知识点: {kps}')

    def create_project_data(self, origin_project):
        """为单个原始项目创建知识图谱数据"""
        name = origin_project.name
        
        # 检查是否已存在
        if DanceProject.objects.filter(name=name).exists():
            DanceProject.objects.filter(name=name).delete()
            
        # 创建项目
        project = DanceProject.objects.create(
            name=name,
            category=self.get_category(origin_project),
            description=origin_project.declare_region or '中国传统舞蹈',
            difficulty_level=3,
        )
        
        # 确定项目类型
        project_type = determine_project_type(name)
        modules_config = get_modules_config(name, project_type)
        
        for j, (module_name, module_desc, module_type) in enumerate(modules_config, 1):
            module = ActionModule.objects.create(
                dance_project=project,
                name=module_name,
                description=module_desc,
                order_index=j
            )
            
            # 生成招式
            moves_count = 3 if j == 1 else 2
            for k in range(1, moves_count + 1):
                create_move(module, k, name, module_type)

    def get_category(self, origin_project):
        """获取项目类别"""
        type_map = {
            'classical': '古典舞',
            'folk': '民族舞',
            'traditional': '传统舞',
            'ethnic': '民间舞',
        }
        return type_map.get(origin_project.dance_type, '传统舞')


# ==================== 类型判断与模块配置 ====================

def determine_project_type(name):
    """根据项目名称判断舞蹈类型"""
    if '鼓' in name:
        return 'drum'
    elif any(x in name for x in ['棍', '板', '鞭', '虎', '牛', '龙', '狮', '盾', '牌', '武']):
        return 'martial'
    elif any(x in name for x in ['族', '藏', '蒙', '维吾尔', '哈萨克', '彝', '苗', '侗', '壮', '瑶', '白', '哈尼', '土家', '傣', '黎', '纳西', '达斡尔', '鄂温克', '锡伯', '俄罗斯', '高山', '怒', '佤', '拉祜', '水', '仫佬', '毛南', '仡佬', '布朗', '阿昌', '普米', '塔吉克', '德昂', '保安', '裕固', '京', '塔塔尔', '独龙', '赫哲', '门巴', '珞巴', '基诺']):
        return 'ethnic'
    else:
        return 'folk'


def get_modules_config(name, project_type):
    """根据类型返回模块配置"""
    configs = {
        'drum': [
            ('基本鼓法模块', f'{name}的基础击鼓技法训练。', 'drum_basic'),
            ('跳跃动作模块', f'{name}特色的跳跃和腾挪动作。', 'drum_jump'),
            ('队形变化模块', f'{name}集体表演时的队形编排。', 'formation'),
        ],
        'martial': [
            ('基本武术模块', f'{name}的基础武术动作训练。', 'martial_basic'),
            ('器械技法模块', f'{name}的器械运用技法。', 'weapon_tech'),
            ('实战演练模块', f'{name}的实战演练技巧。', 'combat'),
        ],
        'ethnic': [
            ('基本手姿模块', f'{name}的特色手部姿势训练。', 'ethnic_hand'),
            ('身段韵律模块', f'{name}的身体韵律美感训练。', 'ethnic_body'),
            ('特色技法模块', f'{name}特有的民族舞蹈技法。', 'ethnic_special'),
        ],
        'folk': [
            ('基本步法模块', f'{name}的基础步伐训练。', 'step_basic'),
            ('手势身段模块', f'{name}的手部动作训练。', 'hand_posture'),
            ('表演技巧模块', f'{name}的表演技巧训练。', 'performance'),
        ],
    }
    return configs.get(project_type, configs['folk'])


def create_move(module, index, project_name, module_type):
    """创建招式及相关数据"""
    templates = get_move_templates(module_type, project_name)
    move_data = templates[(index - 1) % len(templates)]
    
    move = SpecificMove.objects.create(
        action_module=module,
        name=move_data['name'],
        description=move_data['description'],
        difficulty=move_data['difficulty'],
        duration=move_data['duration'],
        order_index=index
    )
    
    MoveAttribute.objects.create(specific_move=move, **move_data['attributes'])
    
    resources = []
    for res_type in ['video', 'demo']:
        resources.append(LearningResource(
            specific_move=move,
            resource_type=res_type,
            title=f'{move.name}教学视频',
            url=f'https://example.com/resource/{move.name}_{res_type}',
            duration=move_data['duration'] - 60,
            order_index=1
        ))
    LearningResource.objects.bulk_create(resources)
    
    kps = []
    for k, kp_cat in enumerate(['技法要点', '文化内涵', '表演技巧']):
        kps.append(KnowledgePoint(
            specific_move=move,
            name=f'{move.name}的{kp_cat}',
            description=f'{move.name}的{kp_cat}要点',
            category=kp_cat,
            importance_level=4 if k == 0 else 3
        ))
    KnowledgePoint.objects.bulk_create(kps)


def get_move_templates(module_type, project_name):
    """根据模块类型返回招式模板"""
    template_map = {
        'drum_basic': get_drum_basic_moves,
        'drum_jump': get_drum_jump_moves,
        'formation': get_formation_moves,
        'martial_basic': get_martial_basic_moves,
        'weapon_tech': get_weapon_tech_moves,
        'combat': get_combat_moves,
        'step_basic': get_step_basic_moves,
        'hand_posture': get_hand_posture_moves,
        'performance': get_performance_moves,
        'ethnic_hand': get_ethnic_hand_moves,
        'ethnic_body': get_ethnic_body_moves,
        'ethnic_special': get_ethnic_special_moves,
    }
    func = template_map.get(module_type, get_general_moves)
    return func(project_name)


# ==================== 招式模板函数 ====================

def get_drum_basic_moves(name):
    return [
        {'name': '单点击鼓', 'description': f'{name}的基础击鼓技法，右手持槌单击鼓面中心。要求手腕灵活，力度均匀。', 'difficulty': 2, 'duration': 240, 'attributes': {'force_parts': '手腕发力，手臂辅助', 'common_mistakes': '击鼓位置不准、力度不均', 'key_points': '击鼓中心位置，手腕放松', 'precautions': '从轻到重，循序渐进'}},
        {'name': '双击连奏', 'description': f'快速连续两次击鼓，形成连贯节奏。要求间隔均匀，声音饱满。', 'difficulty': 4, 'duration': 300, 'attributes': {'force_parts': '手腕快速弹动', 'common_mistakes': '间隔不均、第二次无力', 'key_points': '两次力度相同，节奏均匀', 'precautions': '先慢练后加速'}},
        {'name': '滚奏技法', 'description': f'连续快速击鼓形成滚动效果。要求频率快而均匀，声音连贯。', 'difficulty': 6, 'duration': 360, 'attributes': {'force_parts': '手腕持续快速运动', 'common_mistakes': '频率不均、声音断续', 'key_points': '手腕放松，频率稳定', 'precautions': '注意手腕保护'}},
    ]

def get_drum_jump_moves(name):
    return [
        {'name': '跃步击鼓', 'description': f'双脚跳起在空中击鼓。要求爆发力强，空中姿态优美。', 'difficulty': 5, 'duration': 320, 'attributes': {'force_parts': '腿部爆发力，核心收紧', 'common_mistakes': '跳不高、落地不稳', 'key_points': '蹬地有力，空中收腹', 'precautions': '充分热身，保护膝盖'}},
        {'name': '转身跳击', 'description': f'跳起同时转身击鼓。要求转体迅速，击鼓准确。', 'difficulty': 7, 'duration': 380, 'attributes': {'force_parts': '腿部爆发力，腰部扭转', 'common_mistakes': '转身不完整、击鼓不准', 'key_points': '转体迅速，时机准确', 'precautions': '循序渐进练习'}},
    ]

def get_formation_moves(name):
    return [
        {'name': '圆圈围鼓', 'description': f'多人围成圆圈同步击鼓。要求队形整齐，节奏统一。', 'difficulty': 3, 'duration': 300, 'attributes': {'force_parts': '全身协调，团队配合', 'common_mistakes': '队形不齐、节奏不一', 'key_points': '保持等距，动作同步', 'precautions': '注意间距，避免碰撞'}},
        {'name': '交叉换位', 'description': f'队员交叉穿行换位。要求路线清晰，避让及时。', 'difficulty': 5, 'duration': 360, 'attributes': {'force_parts': '腿部移动，视线引导', 'common_mistakes': '路线混乱、碰撞他人', 'key_points': '按路线行进，保持节奏', 'precautions': '多次排练熟悉路线'}},
    ]

def get_martial_basic_moves(name):
    return [
        {'name': '马步站桩', 'description': f'{name}的基础站桩，双脚开立屈膝下蹲。要求重心稳定，背部挺直。', 'difficulty': 2, 'duration': 240, 'attributes': {'force_parts': '大腿发力，核心收紧', 'common_mistakes': '膝盖内扣、弯腰驼背', 'key_points': '两脚平行，含胸拔背', 'precautions': '时间不宜过长'}},
        {'name': '弓步冲拳', 'description': f'前腿弓后腿绷，同时冲拳。要求前后腿比例7:3，出拳有力。', 'difficulty': 4, 'duration': 300, 'attributes': {'force_parts': '后腿蹬地，腰部扭转', 'common_mistakes': '前后距离小、出拳无力', 'key_points': '前腿90度，髋部正向', 'precautions': '膝盖与脚尖一致'}},
        {'name': '虚步亮掌', 'description': f'一腿支撑一腿虚点，同时亮掌。要求虚实分明，重心稳定。', 'difficulty': 3, 'duration': 270, 'attributes': {'force_parts': '支撑腿发力，手臂伸展', 'common_mistakes': '虚实不分、重心不稳', 'key_points': '支撑稳固，亮掌至肩', 'precautions': '保护膝关节'}},
    ]

def get_weapon_tech_moves(name):
    return [
        {'name': '持械站立', 'description': f'{name}的基本持械姿势。要求重心稳定，器械角度正确。', 'difficulty': 2, 'duration': 200, 'attributes': {'force_parts': '核心收紧，手臂持械', 'common_mistakes': '重心不稳、器械角度错', 'key_points': '器械护身，身体放松', 'precautions': '肩膀放松'}},
        {'name': '器械挥舞', 'description': f'{name}的器械挥舞技法。要求动作流畅，力度均匀。', 'difficulty': 5, 'duration': 320, 'attributes': {'force_parts': '全身协调，腰部带动', 'common_mistakes': '动作僵硬、力度不够', 'key_points': '攻防一体，节奏明快', 'precautions': '注意安全距离'}},
    ]

def get_combat_moves(name):
    return [
        {'name': '进退攻防', 'description': f'前进后退攻防演练。要求步法灵活，转换迅速。', 'difficulty': 5, 'duration': 340, 'attributes': {'force_parts': '腿部移动，全身协调', 'common_mistakes': '步法混乱、攻防脱节', 'key_points': '进退有序，转换迅速', 'precautions': '控制力度，避免受伤'}},
        {'name': '连环进击', 'description': f'连续多次进攻动作。要求动作连贯，节奏紧凑。', 'difficulty': 7, 'duration': 380, 'attributes': {'force_parts': '全身爆发，连续发力', 'common_mistakes': '动作脱节、力度递减', 'key_points': '动作连贯，呼吸配合', 'precautions': '合理分配体力'}},
    ]

def get_step_basic_moves(name):
    return [
        {'name': '十字步', 'description': f'{name}的基础步伐，双脚交叉前行。要求步伐轻快，节奏明快。', 'difficulty': 2, 'duration': 240, 'attributes': {'force_parts': '腿部交替，腰部跟随', 'common_mistakes': '步伐沉重、交叉不准', 'key_points': '脚步轻灵，交叉清晰', 'precautions': '注意脚下安全'}},
        {'name': '颤步扭腰', 'description': f'膝盖颤动同时腰部扭动。要求上下协调，富有韵律。', 'difficulty': 3, 'duration': 280, 'attributes': {'force_parts': '膝盖弹动，腰部扭转', 'common_mistakes': '颤动不匀、上下脱节', 'key_points': '膝颤腰扭协调', 'precautions': '腰部充分热身'}},
        {'name': '跳步转身', 'description': f'单脚跳起转身落地。要求跳跃轻盈，转身流畅。', 'difficulty': 4, 'duration': 300, 'attributes': {'force_parts': '腿部爆发，腰部扭转', 'common_mistakes': '跳跃笨重、落地不稳', 'key_points': '跳跃轻盈，落地缓冲', 'precautions': '保护脚踝'}},
    ]

def get_hand_posture_moves(name):
    return [
        {'name': '云手翻花', 'description': f'双手做云手同时翻花。要求手腕灵活，动作连贯。', 'difficulty': 4, 'duration': 300, 'attributes': {'force_parts': '手腕旋转，小臂配合', 'common_mistakes': '手腕僵硬、翻花不到位', 'key_points': '以腕为轴，圆活自然', 'precautions': '先慢后快'}},
        {'name': '托手亮相', 'description': f'单手托起高举亮相。要求手臂伸直，身体舒展。', 'difficulty': 3, 'duration': 240, 'attributes': {'force_parts': '手臂上举，核心收紧', 'common_mistakes': '手臂弯曲、耸肩', 'key_points': '沉肩坠肘，身体挺拔', 'precautions': '肩部放松'}},
    ]

def get_performance_moves(name):
    return [
        {'name': '表情运用', 'description': f'{name}的面部表情技巧。要求表情自然，富有感染力。', 'difficulty': 3, 'duration': 260, 'attributes': {'force_parts': '面部控制，眼神配合', 'common_mistakes': '表情僵硬、过度夸张', 'key_points': '表情自然，配合动作', 'precautions': '观察生活积累'}},
        {'name': '情感表达', 'description': f'通过舞蹈表达情感。要求情感真挚，表现力强。', 'difficulty': 5, 'duration': 320, 'attributes': {'force_parts': '全身协调，情感投入', 'common_mistakes': '情感虚假、表现不足', 'key_points': '情感真挚，动作有魂', 'precautions': '理解舞蹈内涵'}},
    ]

def get_ethnic_hand_moves(name):
    return [
        {'name': '孔雀手型', 'description': f'{name}的特色手型，拇指食指捏圆，三指展开。要求手指柔软。', 'difficulty': 3, 'duration': 240, 'attributes': {'force_parts': '手指灵活，手腕柔和', 'common_mistakes': '手指僵硬、形状不标准', 'key_points': '拇指食指圆润，三指舒展', 'precautions': '经常活动手指'}},
        {'name': '展翅手势', 'description': f'双臂展开手腕下压，模仿展翅。要求动作舒展大方。', 'difficulty': 4, 'duration': 300, 'attributes': {'force_parts': '肩部展开，手臂延伸', 'common_mistakes': '手臂不舒展、手腕角度错', 'key_points': '肩背打开，手腕下压', 'precautions': '避免耸肩'}},
        {'name': '翻腕动作', 'description': f'手腕快速内外翻转。要求手腕灵活，翻转迅速。', 'difficulty': 4, 'duration': 260, 'attributes': {'force_parts': '手腕关节运动', 'common_mistakes': '手腕僵硬、翻转不到位', 'key_points': '以腕为轴，翻转饱满', 'precautions': '充分活动手腕'}},
    ]

def get_ethnic_body_moves(name):
    return [
        {'name': '三道弯体态', 'description': f'身体形成头胸髋三弯S曲线。要求柔韧协调，动作流畅。', 'difficulty': 5, 'duration': 330, 'attributes': {'force_parts': '腰部扭转，髋部侧顶', 'common_mistakes': '弯曲不自然、重心不稳', 'key_points': '三弯流畅，重心稳定', 'precautions': '循序渐进练柔韧'}},
        {'name': '颤膝律动', 'description': f'膝盖连续小幅颤动带动全身。要求颤动均匀，连绵不断。', 'difficulty': 4, 'duration': 300, 'attributes': {'force_parts': '膝盖弹动，全身放松', 'common_mistakes': '颤动过大、身体僵硬', 'key_points': '小幅颤动，全身协调', 'precautions': '膝盖充分热身'}},
    ]

def get_ethnic_special_moves(name):
    return [
        {'name': '旋转技巧', 'description': f'{name}的快速旋转技法。要求平衡力强，旋转稳定。', 'difficulty': 7, 'duration': 360, 'attributes': {'force_parts': '核心收紧，头部定点', 'common_mistakes': '旋转不稳、头晕', 'key_points': '重心集中，手臂平衡', 'precautions': '避免眩晕'}},
        {'name': '移颈摇头', 'description': f'头部左右平移配合节奏。要求颈部灵活，动作准确。', 'difficulty': 3, 'duration': 240, 'attributes': {'force_parts': '颈部肌肉控制', 'common_mistakes': '幅度过大、动作生硬', 'key_points': '小幅移动，节奏准确', 'precautions': '颈部轻柔热身'}},
    ]

def get_general_moves(name):
    return [
        {'name': '基础动作', 'description': f'基础舞蹈动作训练。要求动作规范，节奏准确。', 'difficulty': 2, 'duration': 240, 'attributes': {'force_parts': '全身协调', 'common_mistakes': '动作不规范', 'key_points': '动作标准，节奏准确', 'precautions': '循序渐进'}},
        {'name': '进阶技巧', 'description': f'进阶舞蹈技巧训练。要求技巧熟练，表现力强。', 'difficulty': 4, 'duration': 300, 'attributes': {'force_parts': '多部位协调', 'common_mistakes': '技巧不牢', 'key_points': '技巧熟练，表现力强', 'precautions': '夯实基础'}},
    ]
