"""
批量生成第二批50个真实非遗舞蹈项目知识图谱数据
使用方法: python manage.py generate_batch_2_data
"""
from django.core.management.base import BaseCommand
from knowledge.models import DanceProject, ActionModule, SpecificMove, MoveAttribute, LearningResource, KnowledgePoint


class Command(BaseCommand):
    help = '批量生成第二批50个非遗舞蹈项目知识图谱数据'

    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS('=' * 70))
        self.stdout.write(self.style.SUCCESS('开始生成第二批非遗舞蹈知识图谱数据'))
        self.stdout.write(self.style.SUCCESS('=' * 70))
        
        # 50个不重复的非遗舞蹈项目（去重后选取）
        projects_data = [
            # 鼓类舞蹈
            {
                'name': '铓鼓舞',
                'category': '少数民族舞蹈',
                'region': '云南省建水县',
                'description': '铓鼓舞是云南彝族、哈尼族的传统祭祀舞蹈，以铓锣和鼓为伴奏，动作粗犷豪放，节奏强烈，具有浓厚的民族宗教色彩。',
                'difficulty': 4,
                'type': 'drum'
            },
            {
                'name': '水鼓舞',
                'category': '少数民族舞蹈',
                'region': '云南省瑞丽市',
                'description': '水鼓舞是云南傣族的传统舞蹈，舞者在水中击鼓起舞，动作优美灵动，展现水乡风情和傣族文化特色。',
                'difficulty': 3,
                'type': 'drum'
            },
            {
                'name': '洛川蹩鼓',
                'category': '民间舞蹈',
                'region': '陕西省洛川县',
                'description': '洛川蹩鼓是陕西黄土高原的传统民间舞蹈，动作独特，步伐蹩跳，节奏欢快，展现陕北人民的豪放性格。',
                'difficulty': 3,
                'type': 'drum'
            },
            {
                'name': '兰州太平鼓',
                'category': '民间舞蹈',
                'region': '甘肃省兰州市',
                'description': '兰州太平鼓是甘肃地区的传统民间舞蹈，鼓声震天，气势磅礴，动作豪迈有力，展现西北地区的雄浑气势。',
                'difficulty': 4,
                'type': 'drum'
            },
            # 少数民族舞蹈
            {
                'name': '怒族达比亚舞',
                'category': '少数民族舞蹈',
                'region': '云南省福贡县',
                'description': '怒族达比亚舞是云南怒族的传统舞蹈，以达比亚（一种弹拨乐器）伴奏，动作轻快优美，展现怒族人民的生活情趣。',
                'difficulty': 3,
                'type': 'ethnic'
            },
            {
                'name': '锅哇（玉树武士舞）',
                'category': '少数民族舞蹈',
                'region': '青海省玉树藏族自治州',
                'description': '锅哇是青海藏族的传统武士舞蹈，动作刚劲有力，步伐稳健，展现藏族武士的英勇形象和尚武精神。',
                'difficulty': 5,
                'type': 'ethnic'
            },
            {
                'name': '纳孜库姆',
                'category': '少数民族舞蹈',
                'region': '新疆维吾尔自治区吐鲁番市',
                'description': '纳孜库姆是新疆维吾尔族的传统舞蹈，动作幽默诙谐，步伐轻快，常伴有滑稽表演，展现维吾尔族的乐观性格。',
                'difficulty': 3,
                'type': 'ethnic'
            },
            {
                'name': '海南苗族盘皇舞',
                'category': '少数民族舞蹈',
                'region': '海南省五指山市',
                'description': '盘皇舞是海南苗族的传统祭祀舞蹈，动作古朴神秘，节奏庄重，具有浓厚的祖先崇拜和图腾文化色彩。',
                'difficulty': 4,
                'type': 'ethnic'
            },
            {
                'name': '多耶',
                'category': '少数民族舞蹈',
                'region': '广西柳州市三江县',
                'description': '多耶是广西侗族的传统集体舞蹈，众人围圈歌舞，动作简单整齐，节奏明快，体现侗族团结友爱的民族精神。',
                'difficulty': 2,
                'type': 'ethnic'
            },
            {
                'name': '壮族打扁担',
                'category': '少数民族舞蹈',
                'region': '广西河池市都安县',
                'description': '壮族打扁担是广西壮族的传统劳动舞蹈，以扁担为道具，动作刚劲有力，节奏鲜明，表现壮族人民的劳动生活。',
                'difficulty': 3,
                'type': 'ethnic'
            },
            {
                'name': '苗族古瓢舞',
                'category': '少数民族舞蹈',
                'region': '贵州省黔东南州',
                'description': '苗族古瓢舞是贵州苗族的传统舞蹈，以古瓢琴伴奏，动作古朴优雅，展现苗族深厚的文化底蕴和艺术魅力。',
                'difficulty': 3,
                'type': 'ethnic'
            },
            {
                'name': '傣族白象马鹿舞',
                'category': '少数民族舞蹈',
                'region': '云南省',
                'description': '傣族白象马鹿舞是云南傣族的传统舞蹈，舞者扮演白象和马鹿，动作模仿动物形态，生动有趣，富有神话色彩。',
                'difficulty': 3,
                'type': 'ethnic'
            },
            {
                'name': '俄罗斯族踢踏舞',
                'category': '少数民族舞蹈',
                'region': '新疆塔城市',
                'description': '俄罗斯族踢踏舞是新疆俄罗斯族的传统舞蹈，步伐轻快有力，节奏明快，融合俄罗斯民间舞蹈特色，展现异域风情。',
                'difficulty': 4,
                'type': 'ethnic'
            },
            {
                'name': '黄羊钱鞭',
                'category': '少数民族舞蹈',
                'region': '宁夏中卫市中宁县',
                'description': '黄羊钱鞭是宁夏回族的传统舞蹈，以钱鞭为道具，动作刚劲有力，节奏强烈，展现回族人民的豪迈性格。',
                'difficulty': 3,
                'type': 'ethnic'
            },
            {
                'name': '土家族摆手舞',
                'category': '少数民族舞蹈',
                'region': '湖南省湘西州',
                'description': '土家族摆手舞是湖南土家族的传统祭祀舞蹈，众人围圈摆手起舞，动作整齐划一，节奏庄重，体现土家族团结精神。',
                'difficulty': 2,
                'type': 'ethnic'
            },
            {
                'name': '土家族撒叶儿嗬',
                'category': '少数民族舞蹈',
                'region': '湖北省长阳县',
                'description': '撒叶儿嗬是湖北土家族的传统丧事舞蹈，动作粗犷豪放，节奏强烈，表达对逝者的哀思和对生命的敬畏。',
                'difficulty': 3,
                'type': 'ethnic'
            },
            {
                'name': '弦子舞',
                'category': '少数民族舞蹈',
                'region': '四川省巴塘县',
                'description': '弦子舞是四川藏族的传统舞蹈，以弦子（二胡类乐器）伴奏，动作优美流畅，展现藏族人民的生活情趣和艺术追求。',
                'difficulty': 3,
                'type': 'ethnic'
            },
            # 武术器械类
            {
                'name': '六郎庄五虎棍',
                'category': '民间舞蹈',
                'region': '北京市海淀区',
                'description': '六郎庄五虎棍是北京地区的传统武术舞蹈，以五根棍为道具，动作刚劲有力，套路复杂，展现传统武术精髓。',
                'difficulty': 5,
                'type': 'martial'
            },
            {
                'name': '翼城浑身板',
                'category': '民间舞蹈',
                'region': '山西临汾市翼城县',
                'description': '翼城浑身板是山西的传统民间舞蹈，全身绑满竹板，边舞边击，声音清脆，动作灵活，展现民间艺术智慧。',
                'difficulty': 4,
                'type': 'martial'
            },
            {
                'name': '阴阳板',
                'category': '民间舞蹈',
                'region': '山东省济宁市邹城市',
                'description': '阴阳板是山东的传统民间舞蹈，以两块木板为道具，击打发声，动作刚柔相济，体现阴阳哲学思想。',
                'difficulty': 3,
                'type': 'martial'
            },
            {
                'name': '陇西云阳板',
                'category': '民间舞蹈',
                'region': '甘肃省定西市陇西县',
                'description': '陇西云阳板是甘肃的传统民间舞蹈，以云阳板为道具，动作流畅优美，节奏明快，展现西北民间艺术特色。',
                'difficulty': 3,
                'type': 'martial'
            },
            # 秧歌类（选取代表性）
            {
                'name': '临县伞头秧歌',
                'category': '民间舞蹈',
                'region': '山西省临县',
                'description': '临县伞头秧歌是山西的传统民间舞蹈，领舞者持伞头，动作欢快活泼，队形变化丰富，展现黄土高原民俗风情。',
                'difficulty': 2,
                'type': 'folk'
            },
            {
                'name': '昌黎地秧歌',
                'category': '民间舞蹈',
                'region': '河北省昌黎县',
                'description': '昌黎地秧歌是河北的传统民间舞蹈，动作细腻优美，步伐轻盈，表情丰富，展现冀东地区的民俗特色。',
                'difficulty': 2,
                'type': 'folk'
            },
            {
                'name': '济阳鼓子秧歌',
                'category': '民间舞蹈',
                'region': '山东省济阳县',
                'description': '济阳鼓子秧歌是山东的传统民间舞蹈，以鼓子为道具，动作豪迈粗犷，气势磅礴，展现齐鲁大地的雄浑气魄。',
                'difficulty': 3,
                'type': 'folk'
            },
            {
                'name': '海阳大秧歌',
                'category': '民间舞蹈',
                'region': '山东省海阳市',
                'description': '海阳大秧歌是山东胶东地区的传统民间舞蹈，动作舒展大方，节奏欢快，队形变化多端，展现胶东民俗风情。',
                'difficulty': 2,
                'type': 'folk'
            },
            {
                'name': '胶州秧歌',
                'category': '民间舞蹈',
                'region': '山东省胶州市',
                'description': '胶州秧歌是山东的传统民间舞蹈，动作细腻婉转，三道弯体态优美，展现胶东女性的柔美风韵。',
                'difficulty': 3,
                'type': 'folk'
            },
            {
                'name': '陕北秧歌',
                'category': '民间舞蹈',
                'region': '陕西省绥德县',
                'description': '陕北秧歌是陕西黄土高原的传统民间舞蹈，动作豪放粗犷，节奏明快，展现陕北人民的豪迈性格和乐观精神。',
                'difficulty': 2,
                'type': 'folk'
            },
            # 其他特色舞蹈
            {
                'name': '泰兴花鼓',
                'category': '民间舞蹈',
                'region': '江苏省泰州泰兴市',
                'description': '泰兴花鼓是江苏水乡的传统民间舞蹈，以花鼓为道具，动作轻快优美，节奏明快，展现江南水乡的柔美风情。',
                'difficulty': 2,
                'type': 'drum'
            },
            {
                'name': '佾舞',
                'category': '民间舞蹈',
                'region': '福建省福州福清市',
                'description': '佾舞是福建的传统祭祀舞蹈，源于古代宫廷雅乐舞蹈，动作庄重典雅，步伐规范严谨，具有浓厚的礼乐文化色彩。',
                'difficulty': 4,
                'type': 'folk'
            },
            {
                'name': '余杭滚灯',
                'category': '民间舞蹈',
                'region': '浙江省杭州余杭区',
                'description': '余杭滚灯是浙江的传统民间舞蹈，以滚动的灯笼为道具，动作灵活多变，灯光闪烁，展现江南民间艺术魅力。',
                'difficulty': 3,
                'type': 'folk'
            },
        ]
        
        # 删除旧数据并生成新数据
        success_count = 0
        for project_info in projects_data:
            name = project_info['name']
            
            # 删除旧数据
            old_project = DanceProject.objects.filter(name=name).first()
            if old_project:
                self.stdout.write(self.style.WARNING(f'删除旧项目: {name}'))
                old_project.delete()
            
            try:
                # 创建项目
                project = DanceProject.objects.create(
                    name=name,
                    category=project_info['category'],
                    description=project_info['description'],
                    difficulty_level=project_info['difficulty'],
                )
                
                self.stdout.write(f'\n正在生成: {name} ({project_info["region"]})')
                
                # 根据类型生成模块
                project_type = project_info['type']
                modules_config = get_modules_config(name, project_type)
                
                total_moves = 0
                for i, (module_name, module_desc, module_type) in enumerate(modules_config, 1):
                    module = ActionModule.objects.create(
                        dance_project=project,
                        name=module_name,
                        description=module_desc,
                        order_index=i
                    )
                    
                    # 为每个模块生成2-3个招式
                    moves_count = 3 if i == 1 else 2
                    for j in range(1, moves_count + 1):
                        create_move(module, j, name, module_type)
                    
                    moves_count = module.specific_moves.count()
                    total_moves += moves_count
                    self.stdout.write(f'  ✓ {module_name}: {moves_count}个招式')
                
                self.stdout.write(self.style.SUCCESS(f'✓ {name} 完成 - 共{total_moves}个招式'))
                success_count += 1
                
            except Exception as e:
                self.stdout.write(self.style.ERROR(f'✗ {name} 失败: {str(e)}'))
        
        self.stdout.write(self.style.SUCCESS('\n' + '=' * 70))
        self.stdout.write(self.style.SUCCESS(f'第二批数据生成完成！成功: {success_count}/{len(projects_data)}'))
        self.stdout.write(self.style.SUCCESS('=' * 70))


def get_modules_config(name, project_type):
    """根据项目类型获取模块配置"""
    if project_type == 'drum':
        return [
            ('基本鼓法模块', f'{name}的基础击鼓技法训练，包括单点、双点、滚奏等基本鼓法。', 'drum_basic'),
            ('跳跃动作模块', f'{name}特色的跳跃和腾挪动作，展现豪放风格。', 'drum_jump'),
            ('队形变化模块', f'{name}集体表演时的队形编排和变化。', 'formation'),
        ]
    elif project_type == 'martial':
        return [
            ('基本武术模块', f'{name}的基础武术动作和站桩训练。', 'martial_basic'),
            ('器械技法模块', f'{name}的器械运用和攻防技法。', 'weapon_tech'),
            ('实战演练模块', f'{name}的实战对抗和演练技巧。', 'combat'),
        ]
    elif project_type == 'ethnic':
        return [
            ('基本手姿模块', f'{name}的特色手部姿势和道具运用训练。', 'ethnic_hand'),
            ('身段韵律模块', f'{name}的身体曲线和韵律美感训练。', 'ethnic_body'),
            ('特色技法模块', f'{name}特有的民族舞蹈技法。', 'ethnic_special'),
        ]
    else:  # folk
        return [
            ('基本步法模块', f'{name}的基础步伐和移动技巧训练。', 'step_basic'),
            ('手势身段模块', f'{name}的手部动作和身体姿态训练。', 'hand_posture'),
            ('表演技巧模块', f'{name}的表演技巧和艺术表现力训练。', 'performance'),
        ]


def create_move(module, index, project_name, module_type):
    """创建招式"""
    # 根据模块类型选择对应的招式模板
    move_templates = get_move_templates(module_type, project_name)
    
    move_data = move_templates[(index - 1) % len(move_templates)]
    
    move = SpecificMove.objects.create(
        action_module=module,
        name=move_data['name'],
        description=move_data['description'],
        difficulty=move_data['difficulty'],
        duration=move_data['duration'],
        order_index=index
    )
    
    MoveAttribute.objects.create(
        specific_move=move,
        **move_data['attributes']
    )
    
    for res_type in ['video', 'demo']:
        LearningResource.objects.create(
            specific_move=move,
            resource_type=res_type,
            title=f'{move.name}教学视频',
            url=f'https://example.com/resource/{move.name}_{res_type}',
            duration=move_data['duration'] - 60,
            order_index=1
        )
    
    kp_categories = ['技法要点', '文化内涵', '表演技巧']
    for k, kp_cat in enumerate(kp_categories):
        KnowledgePoint.objects.create(
            specific_move=move,
            name=f'{move.name}的{kp_cat}',
            description=f'{move.name}的{kp_cat}要点',
            category=kp_cat,
            importance_level=4 if k == 0 else 3
        )


def get_general_moves(module_name):
    """通用招式模板"""
    return [
        {
            'name': '基础动作',
            'description': f'基础舞蹈动作训练，是学习的起点。要求动作规范，节奏准确。',
            'difficulty': 2,
            'duration': 240,
            'attributes': {
                'force_parts': '全身协调',
                'common_mistakes': '动作不规范',
                'key_points': '动作标准，节奏准确',
                'precautions': '循序渐进'
            }
        },
        {
            'name': '进阶技巧',
            'description': f'进阶舞蹈技巧训练，需要一定基础。要求技巧熟练，表现力强。',
            'difficulty': 4,
            'duration': 300,
            'attributes': {
                'force_parts': '多部位协调',
                'common_mistakes': '技巧掌握不牢',
                'key_points': '技巧熟练，表现力强',
                'precautions': '充分练习基础'
            }
        },
    ]


# 招式模板函数
def get_move_templates(module_type, project_name):
    """根据模块类型返回对应的招式模板"""
    templates = {
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
    func = templates.get(module_type, get_general_moves)
    return func(project_name)


# ==================== 鼓类舞蹈招式模板 ====================

def get_drum_basic_moves(project_name):
    """基本鼓法模块 - 击鼓技法"""
    return [
        {
            'name': '单点击鼓',
            'description': f'{project_name}的基础击鼓技法，右手持槌单击鼓面中心，声音清脆响亮。要求手腕灵活，力度均匀，节奏稳定。',
            'difficulty': 2,
            'duration': 240,
            'attributes': {
                'force_parts': '手腕发力，手臂辅助',
                'common_mistakes': '击鼓位置不准、力度不均、节奏不稳',
                'key_points': '击鼓中心位置，手腕放松，力度适中',
                'precautions': '从轻到重，循序渐进练习'
            }
        },
        {
            'name': '双击连奏',
            'description': f'快速连续两次击鼓，形成连贯的节奏。要求两次击鼓间隔均匀，声音饱满有力。',
            'difficulty': 4,
            'duration': 300,
            'attributes': {
                'force_parts': '手腕快速弹动，手指控制',
                'common_mistakes': '间隔不均、第二次无力、节奏加快',
                'key_points': '两次力度相同，间隔相等，节奏均匀',
                'precautions': '先慢练，熟练后加速'
            }
        },
        {
            'name': '滚奏技法',
            'description': f'连续快速击鼓形成滚动效果，如雷声轰鸣。要求频率快而均匀，声音连贯不断。',
            'difficulty': 6,
            'duration': 360,
            'attributes': {
                'force_parts': '手腕持续快速运动，手臂配合',
                'common_mistakes': '频率不均、声音断续、手腕疲劳',
                'key_points': '手腕放松，频率稳定，力度均匀',
                'precautions': '注意手腕保护，避免过度疲劳'
            }
        },
    ]


def get_drum_jump_moves(project_name):
    """跳跃动作模块 - 腾挪技巧"""
    return [
        {
            'name': '跃步击鼓',
            'description': f'双脚同时跳起，在空中击鼓一次，落地稳健。要求爆发力强，空中姿态优美，击鼓准确。',
            'difficulty': 5,
            'duration': 320,
            'attributes': {
                'force_parts': '腿部爆发力，核心收紧，手臂挥动',
                'common_mistakes': '跳不高、落地不稳、空中击鼓不准',
                'key_points': '蹬地有力，空中收腹，落地缓冲',
                'precautions': '充分热身，注意膝盖和脚踝保护'
            }
        },
        {
            'name': '转身跳击',
            'description': f'跳起同时转身180度，在空中击鼓。要求转体迅速，击鼓准确，落地平衡。',
            'difficulty': 7,
            'duration': 380,
            'attributes': {
                'force_parts': '腿部爆发力，腰部扭转，手臂配合',
                'common_mistakes': '转身不完整、击鼓不准、落地摇晃',
                'key_points': '转体迅速，击鼓时机准确',
                'precautions': '循序渐进，先练转身再练击鼓'
            }
        },
    ]


def get_formation_moves(project_name):
    """队形变化模块 - 集体编排"""
    return [
        {
            'name': '圆圈围鼓',
            'description': f'多人围成圆圈，面向圆心，同步击鼓。要求队形整齐，节奏统一，气势磅礴。',
            'difficulty': 3,
            'duration': 300,
            'attributes': {
                'force_parts': '全身协调，团队配合',
                'common_mistakes': '队形不齐、节奏不一、间距不均',
                'key_points': '保持等距，面向圆心，动作同步',
                'precautions': '注意与他人的距离，避免碰撞'
            }
        },
        {
            'name': '交叉换位',
            'description': f'队员相互交叉穿行换位，形成动态的队形变化。要求路线清晰，避让及时，动作流畅。',
            'difficulty': 5,
            'duration': 360,
            'attributes': {
                'force_parts': '腿部移动，身体转向，视线引导',
                'common_mistakes': '路线混乱、碰撞他人、节奏打乱',
                'key_points': '按预定路线行进，注意观察，保持节奏',
                'precautions': '多次排练熟悉路线，注意安全'
            }
        },
    ]


# ==================== 武术类招式模板 ====================

def get_martial_basic_moves(project_name):
    """基本武术模块 - 武术基础"""
    return [
        {
            'name': '马步站桩',
            'description': f'{project_name}的基础站桩，双脚分开与肩同宽，屈膝下蹲成马步。要求膝盖不超过脚尖，背部挺直，重心稳定。',
            'difficulty': 2,
            'duration': 240,
            'attributes': {
                'force_parts': '大腿肌肉发力，核心收紧，双脚均匀受力',
                'common_mistakes': '膝盖内扣、弯腰驼背、重心偏向一侧',
                'key_points': '两脚平行开立，屈膝90度，含胸拔背',
                'precautions': '初学者时间不宜过长，每次3-5分钟'
            }
        },
        {
            'name': '弓步冲拳',
            'description': f'前腿弓、后腿绷，形成弓箭步，同时右手冲拳。要求前后腿比例约为7:3，出拳有力。',
            'difficulty': 4,
            'duration': 300,
            'attributes': {
                'force_parts': '前腿大腿发力支撑，后腿蹬地，腰部扭转带动出拳',
                'common_mistakes': '前后脚距离过小、后腿弯曲、出拳无力',
                'key_points': '前腿屈膝90度，后腿伸直，髋部正对前方',
                'precautions': '注意膝盖方向与脚尖一致，避免扭伤'
            }
        },
        {
            'name': '虚步亮掌',
            'description': f'一腿屈膝半蹲支撑，另一腿脚尖点地成虚步，同时亮掌。要求虚实分明，重心稳定。',
            'difficulty': 3,
            'duration': 270,
            'attributes': {
                'force_parts': '支撑腿大腿发力，手臂伸展',
                'common_mistakes': '虚实不分、重心不稳、亮掌不到位',
                'key_points': '支撑腿稳固，虚腿轻灵，亮掌至肩高',
                'precautions': '注意膝关节保护，避免过度负重'
            }
        },
    ]


def get_weapon_tech_moves(project_name):
    """器械技法模块 - 器械运用"""
    return [
        {
            'name': '持械站立',
            'description': f'{project_name}的基本持械姿势，要求重心稳定，器械角度正确，动作标准。',
            'difficulty': 2,
            'duration': 200,
            'attributes': {
                'force_parts': '双腿稳固，核心收紧，手臂持械',
                'common_mistakes': '重心不稳、器械角度不对、肌肉紧张',
                'key_points': '双脚开立，器械护身，身体放松',
                'precautions': '注意肩膀放松，避免耸肩'
            }
        },
        {
            'name': '器械挥舞',
            'description': f'{project_name}的器械挥舞技法，要求动作流畅，力度均匀，节奏明快。',
            'difficulty': 5,
            'duration': 320,
            'attributes': {
                'force_parts': '手臂发力，腰部扭转，全身协调',
                'common_mistakes': '动作僵硬、力度不够、节奏混乱',
                'key_points': '器械配合，动作协调，攻防一体',
                'precautions': '注意安全，避免误伤他人'
            }
        },
    ]


def get_combat_moves(project_name):
    """实战演练模块 - 对抗技巧"""
    return [
        {
            'name': '进退攻防',
            'description': f'前进进攻后退防守的实战演练，要求步法灵活，攻防转换迅速。',
            'difficulty': 5,
            'duration': 340,
            'attributes': {
                'force_parts': '腿部移动，手臂攻防，全身协调',
                'common_mistakes': '步法混乱、攻防脱节、节奏单一',
                'key_points': '进退有序，攻防转换迅速',
                'precautions': '注意控制力度，避免受伤'
            }
        },
        {
            'name': '连环进击',
            'description': f'连续多次进攻动作，形成连环攻势。要求动作连贯，节奏紧凑，气势如虹。',
            'difficulty': 7,
            'duration': 380,
            'attributes': {
                'force_parts': '全身爆发力，连续发力',
                'common_mistakes': '动作脱节、力度递减、呼吸紊乱',
                'key_points': '动作连贯，力度不减，呼吸配合',
                'precautions': '注意体力分配，避免过度疲劳'
            }
        },
    ]


# ==================== 民间舞蹈招式模板 ====================

def get_step_basic_moves(project_name):
    """基本步法模块 - 步伐训练"""
    return [
        {
            'name': '十字步',
            'description': f'{project_name}的基础步伐，双脚交叉前行，形成十字形轨迹。要求步伐轻快，节奏明快。',
            'difficulty': 2,
            'duration': 240,
            'attributes': {
                'force_parts': '腿部交替发力，腰部跟随摆动',
                'common_mistakes': '步伐沉重、交叉不准、节奏拖沓',
                'key_points': '脚步轻灵，交叉清晰，节奏均匀',
                'precautions': '注意脚下安全，避免绊倒'
            }
        },
        {
            'name': '颤步扭腰',
            'description': f'膝盖微屈做颤动，同时腰部左右扭动。要求上下协调，富有韵律感。',
            'difficulty': 3,
            'duration': 280,
            'attributes': {
                'force_parts': '膝盖弹动，腰部扭转',
                'common_mistakes': '颤动不匀、扭腰过度、上下脱节',
                'key_points': '膝颤腰扭协调，幅度适中',
                'precautions': '腰部热身充分，避免扭伤'
            }
        },
        {
            'name': '跳步转身',
            'description': f'单脚跳起同时转身，另一脚落地。要求跳跃轻盈，转身流畅，落地稳健。',
            'difficulty': 4,
            'duration': 300,
            'attributes': {
                'force_parts': '腿部爆发力，腰部扭转',
                'common_mistakes': '跳跃笨重、转身不完整、落地不稳',
                'key_points': '跳跃轻盈，转身迅速，落地缓冲',
                'precautions': '注意脚踝保护，避免扭伤'
            }
        },
    ]


def get_hand_posture_moves(project_name):
    """手势身段模块 - 手部姿态"""
    return [
        {
            'name': '云手翻花',
            'description': f'双手做云手动作，同时翻花。要求手腕灵活，动作连贯流畅，富有韵律感。',
            'difficulty': 4,
            'duration': 300,
            'attributes': {
                'force_parts': '手腕旋转发力，小臂配合',
                'common_mistakes': '手腕僵硬、动作断续、翻花不到位',
                'key_points': '以腕为轴，圆活自然，翻花迅速',
                'precautions': '先慢后快，循序渐进'
            }
        },
        {
            'name': '托手亮相',
            'description': f'单手托起高举，身体挺拔，形成优美的亮相姿态。要求手臂伸直，身体舒展。',
            'difficulty': 3,
            'duration': 240,
            'attributes': {
                'force_parts': '手臂上举，肩膀下沉，核心收紧',
                'common_mistakes': '手臂弯曲、耸肩、身体歪斜',
                'key_points': '手臂伸直但不僵硬，沉肩坠肘',
                'precautions': '注意肩部放松，避免耸肩'
            }
        },
    ]


def get_performance_moves(project_name):
    """表演技巧模块 - 艺术表现"""
    return [
        {
            'name': '表情运用',
            'description': f'{project_name}的面部表情运用技巧，通过喜怒哀乐等表情传达情感。要求表情自然，富有感染力。',
            'difficulty': 3,
            'duration': 260,
            'attributes': {
                'force_parts': '面部肌肉控制，眼神配合',
                'common_mistakes': '表情僵硬、过度夸张、与动作脱节',
                'key_points': '表情自然，与动作配合，富有感染力',
                'precautions': '多观察生活，积累表情素材'
            }
        },
        {
            'name': '情感表达',
            'description': f'通过舞蹈动作和表情表达喜怒哀乐等情感。要求情感真挚，表现力强。',
            'difficulty': 5,
            'duration': 320,
            'attributes': {
                'force_parts': '全身协调，情感投入',
                'common_mistakes': '情感虚假、表现力不足、动作机械',
                'key_points': '情感真挚，表现力强，动作有灵魂',
                'precautions': '理解舞蹈内涵，投入真情实感'
            }
        },
    ]


# ==================== 少数民族舞蹈招式模板 ====================

def get_ethnic_hand_moves(project_name):
    """基本手姿模块 - 手部姿势"""
    return [
        {
            'name': '孔雀手型',
            'description': f'{project_name}的特色手型，拇指与食指相捏成圆，其余三指展开如扇。要求手指柔软，姿态优美。',
            'difficulty': 3,
            'duration': 240,
            'attributes': {
                'force_parts': '手指关节灵活，手腕柔和',
                'common_mistakes': '手指僵硬、形状不标准、用力过猛',
                'key_points': '拇指食指圆润，三指舒展，手腕放松',
                'precautions': '经常活动手指，避免抽筋'
            }
        },
        {
            'name': '展翅手势',
            'description': f'双臂展开，手腕下压，手指微翘，模仿展翅飞翔的姿态。要求动作舒展大方。',
            'difficulty': 4,
            'duration': 300,
            'attributes': {
                'force_parts': '肩部展开，手臂延伸，手腕下压',
                'common_mistakes': '手臂不够舒展、手腕角度不对',
                'key_points': '肩背打开，手臂呈弧线，手腕柔和下压',
                'precautions': '注意肩部放松，避免耸肩'
            }
        },
        {
            'name': '翻腕动作',
            'description': f'手腕快速内外翻转，配合手臂动作。要求手腕灵活，翻转迅速有力。',
            'difficulty': 4,
            'duration': 260,
            'attributes': {
                'force_parts': '手腕关节灵活运动',
                'common_mistakes': '手腕僵硬、翻转不到位',
                'key_points': '以腕为轴，翻转饱满',
                'precautions': '充分活动手腕，避免扭伤'
            }
        },
    ]


def get_ethnic_body_moves(project_name):
    """身段韵律模块 - 身体曲线"""
    return [
        {
            'name': '三道弯体态',
            'description': f'身体形成头、胸、髋三个弯曲，呈现S形曲线。要求柔韧协调，动作流畅。',
            'difficulty': 5,
            'duration': 330,
            'attributes': {
                'force_parts': '腰部扭转，髋部侧顶，头部倾斜',
                'common_mistakes': '弯曲不自然、过度扭曲、重心不稳',
                'key_points': '三弯流畅自然，重心稳定',
                'precautions': '循序渐进练习柔韧性'
            }
        },
        {
            'name': '颤膝律动',
            'description': f'膝盖连续小幅上下颤动，带动全身产生波浪般的律动。要求颤动均匀，连绵不断。',
            'difficulty': 4,
            'duration': 300,
            'attributes': {
                'force_parts': '膝盖弹动，全身放松跟随',
                'common_mistakes': '颤动过大、节奏不均、身体僵硬',
                'key_points': '小幅颤动，连绵不断，全身协调',
                'precautions': '膝盖热身充分，避免过度颤动'
            }
        },
    ]


def get_ethnic_special_moves(project_name):
    """特色技法模块 - 民族特色"""
    return [
        {
            'name': '旋转技巧',
            'description': f'{project_name}的快速旋转技法，单脚支撑快速旋转。要求平衡能力强，旋转速度快且稳定。',
            'difficulty': 7,
            'duration': 360,
            'attributes': {
                'force_parts': '支撑腿稳定，核心收紧，头部定点',
                'common_mistakes': '旋转不稳、头晕、速度不均',
                'key_points': '重心集中，头部留头，手臂辅助平衡',
                'precautions': '循序渐进练习，避免眩晕'
            }
        },
        {
            'name': '移颈摇头',
            'description': f'头部左右平移，配合音乐节奏。要求颈部灵活，动作准确。',
            'difficulty': 3,
            'duration': 240,
            'attributes': {
                'force_parts': '颈部肌肉控制',
                'common_mistakes': '幅度过大、动作生硬',
                'key_points': '小幅移动，节奏准确',
                'precautions': '颈部热身，动作轻柔'
            }
        },
    ]
