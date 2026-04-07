# 非遗传统舞蹈知识图谱 - AI数据生成指南

## 📋 使用说明

本文档提供356个非遗传统舞蹈项目的**动作模块**和**具体招式**的数据生成框架。
您可以将此框架提供给AI助手，让它为每个舞蹈项目生成真实、专业的数据。

---

## 🎯 数据结构说明

### 四层关联体系
```
舞蹈项目 (DanceProject)
  └─ 基础动作模块 (ActionModule) [4个模块/项目]
      └─ 具体招式 (SpecificMove) [10-15个招式/模块]
          ├─ 动作属性 (MoveAttribute)
          ├─ 学习资源 (LearningResource) [3-5个资源/招式]
          └─ 知识点标签 (KnowledgePoint) [4-6个标签/招式]
```

---

## 📝 数据生成模板

### 1. 基础动作模块模板 (ActionModule)

每个舞蹈项目需要 **4个基础动作模块**：

```python
{
    "dance_project_id": <项目ID>,
    "modules": [
        {
            "name": "模块名称",
            "description": "模块描述（50-100字）",
            "order_index": 1,  # 1-4
            "moves": [
                # 具体招式列表（见下方）
            ]
        },
        # ... 共4个模块
    ]
}
```

#### 四种模块类型（根据舞蹈类别选择）：

**A. 民间舞蹈类**
1. 基本步伐模块 - 基础步法训练
2. 手势身段模块 - 手部动作与身体姿态
3. 队形变化模块 - 集体舞蹈的队形编排
4. 节奏韵律模块 - 音乐配合与节奏掌握

**B. 宫廷舞蹈类**
1. 礼仪规范模块 - 宫廷礼仪与仪态
2. 优雅身韵模块 - 柔美流畅的身段
3. 道具运用模块 - 扇子、绸带等道具使用
4. 队列阵势模块 - 大型表演的阵列变化

**C. 宗教祭祀舞蹈类**
1. 仪式程序模块 - 祭祀流程与仪式动作
2. 象征手势模块 - 具有宗教意义的手势
3. 法器运用模块 - 鼓、铃等法器使用
4. 诵唱配合模块 - 舞蹈与诵经的配合

**D. 少数民族舞蹈类**
1. 民族特色步伐模块 - 该民族特有的步法
2. 服饰道具模块 - 民族服饰与特色道具
3. 节庆仪式模块 - 节日庆典中的舞蹈
4. 生活劳作模块 - 反映日常生活的动作

---

### 2. 具体招式模板 (SpecificMove)

每个模块需要 **10-15个具体招式**：

```python
{
    "name": "招式名称",
    "description": "招式详细描述（80-150字）",
    "difficulty": 3,  # 难度等级 1-10
    "duration": 300,  # 学习时长（秒），建议180-600秒
    "order_index": 1,  # 在模块中的顺序
    
    # 动作属性
    "attributes": {
        "force_parts": "发力部位描述（如：腰部带动手臂，重心在右脚）",
        "common_mistakes": "常见错误（如：手臂僵硬、重心不稳、节奏不准）",
        "key_points": "标准要领（如：含胸拔背、沉肩坠肘、气息平稳）",
        "precautions": "注意事项（如：热身充分、循序渐进、避免过度拉伸）"
    },
    
    # 学习资源（3-5个）
    "resources": [
        {
            "type": "video",  # video/demo/article
            "title": "资源标题",
            "url": "资源链接（可以是占位符）",
            "duration": 180  # 视频时长（秒）
        },
        # ... 更多资源
    ],
    
    # 知识点标签（4-6个）
    "knowledge_points": [
        {
            "name": "知识点名称",
            "description": "知识点说明（30-50字）",
            "category": "技法要点",  # 技法要点/文化内涵/历史渊源/表演技巧/训练方法
            "importance_level": 4  # 重要程度 1-5
        },
        # ... 更多知识点
    ]
}
```

---

## 🎨 真实数据示例

### 示例1：京西太平鼓 - 基本步伐模块

```python
{
    "dance_project_name": "京西太平鼓",
    "module_name": "基本步伐模块",
    "module_description": "太平鼓的基本步法训练，包括站立姿势、移动步法、转身技巧等，是学习太平鼓的基础。通过系统练习，掌握正确的重心转移和脚步协调。",
    
    "moves": [
        {
            "name": "马步站桩",
            "description": "双脚分开与肩同宽，屈膝下蹲成马步，双手持鼓置于胸前。要求膝盖不超过脚尖，背部挺直，重心稳定。这是太平鼓最基础的站立姿势，为后续动作打下坚实基础。",
            "difficulty": 2,
            "duration": 240,
            "order_index": 1,
            
            "attributes": {
                "force_parts": "大腿肌肉发力，核心收紧，双脚均匀受力",
                "common_mistakes": "膝盖内扣、弯腰驼背、重心偏向一侧、呼吸急促",
                "key_points": "两脚平行开立，屈膝90度，含胸拔背，气沉丹田，目视前方",
                "precautions": "初学者时间不宜过长，每次3-5分钟，注意膝盖保暖，避免受凉"
            },
            
            "resources": [
                {
                    "type": "video",
                    "title": "马步站桩标准示范",
                    "url": "https://example.com/video/taipinggu_mabu.mp4",
                    "duration": 180
                },
                {
                    "type": "demo",
                    "title": "传承人讲解站桩要点",
                    "url": "https://example.com/demo/master_mabu.mp4",
                    "duration": 300
                },
                {
                    "type": "article",
                    "title": "马步训练的科学方法",
                    "url": "https://example.com/article/mabu_training.pdf",
                    "duration": null
                }
            ],
            
            "knowledge_points": [
                {
                    "name": "重心控制",
                    "description": "掌握身体重心的分布和转移，保持平衡稳定",
                    "category": "技法要点",
                    "importance_level": 5
                },
                {
                    "name": "呼吸调节",
                    "description": "配合动作进行深呼吸，增强耐力和稳定性",
                    "category": "训练方法",
                    "importance_level": 4
                },
                {
                    "name": "腿部力量",
                    "description": "通过站桩锻炼大腿和小腿肌肉力量",
                    "category": "训练方法",
                    "importance_level": 4
                },
                {
                    "name": "传统文化",
                    "description": "马步是中国武术和传统舞蹈的基础功",
                    "category": "文化内涵",
                    "importance_level": 3
                }
            ]
        },
        
        {
            "name": "弓步击鼓",
            "description": "前腿弓、后腿绷，形成弓箭步，同时右手挥槌击鼓。要求前后腿比例约为7:3，上身微向前倾，击鼓有力。此动作体现太平鼓的阳刚之气。",
            "difficulty": 4,
            "duration": 300,
            "order_index": 2,
            
            "attributes": {
                "force_parts": "前腿大腿发力支撑，后腿蹬地，腰部扭转带动手臂击鼓",
                "common_mistakes": "前后脚距离过小、后腿弯曲、击鼓无力、身体晃动",
                "key_points": "前腿屈膝90度，后腿伸直，髋部正对前方，击鼓时腰臂合一",
                "precautions": "注意膝盖方向与脚尖一致，避免扭伤，击鼓力度适中"
            },
            
            "resources": [
                {
                    "type": "video",
                    "title": "弓步击鼓分解教学",
                    "url": "https://example.com/video/gongbu_jigu.mp4",
                    "duration": 240
                },
                {
                    "type": "demo",
                    "title": "老艺人弓步击鼓展示",
                    "url": "https://example.com/demo/master_gongbu.mp4",
                    "duration": 180
                },
                {
                    "type": "article",
                    "title": "弓步在民间舞蹈中的应用",
                    "url": "https://example.com/article/gongbu_application.pdf",
                    "duration": null
                }
            ],
            
            "knowledge_points": [
                {
                    "name": "弓步要领",
                    "description": "掌握标准弓步的姿势要求和发力方式",
                    "category": "技法要点",
                    "importance_level": 5
                },
                {
                    "name": "击鼓技巧",
                    "description": "学习正确的握槌方法和击鼓角度",
                    "category": "技法要点",
                    "importance_level": 5
                },
                {
                    "name": "腰臂协调",
                    "description": "腰部转动与手臂挥动的协调配合",
                    "category": "表演技巧",
                    "importance_level": 4
                },
                {
                    "name": "阳刚之美",
                    "description": "体现北方民间舞蹈的豪放风格",
                    "category": "文化内涵",
                    "importance_level": 3
                },
                {
                    "name": "力量训练",
                    "description": "通过弓步练习增强下肢力量和稳定性",
                    "category": "训练方法",
                    "importance_level": 4
                }
            ]
        }
        
        # ... 继续添加10-13个招式
    ]
}
```

---

## 📊 批量生成建议

### 方案A：逐个项目生成（推荐）

为每个舞蹈项目单独生成完整数据：

```
请为以下舞蹈项目生成完整的知识图谱数据：

项目名称：[项目名称]
项目类别：[民间舞蹈/宫廷舞蹈/宗教祭祀/少数民族]
项目简介：[项目简介]
难度等级：[1-5]

要求：
1. 生成4个基础动作模块
2. 每个模块包含10-15个具体招式
3. 每个招式包含完整的动作属性、3-5个学习资源、4-6个知识点标签
4. 内容要专业、准确，符合该舞蹈的实际特点
5. 招式名称要有传统文化特色
```

### 方案B：按舞蹈类别批量生成

同一类别的舞蹈可以共享部分模块模板：

```
请为[民间舞蹈类]生成通用的动作模块模板：
- 基本步伐模块（包含12个通用招式）
- 手势身段模块（包含12个通用招式）
- 队形变化模块（包含10个通用招式）
- 节奏韵律模块（包含10个通用招式）

然后针对每个具体舞蹈项目，调整招式名称和细节描述。
```

---

## ✅ 质量检查清单

生成数据后，请检查：

- [ ] 招式名称是否符合舞蹈特色（避免过于现代化）
- [ ] 难度等级是否合理递进（从易到难）
- [ ] 动作描述是否专业准确
- [ ] 发力部位描述是否清晰
- [ ] 常见错误是否实用（能帮助学习者避免）
- [ ] 知识点是否有文化深度
- [ ] 学习资源类型是否多样（视频/示范/图文）
- [ ] 数据量是否充足（每个项目至少40个招式）

---

## 🔧 数据导入脚本

生成数据后，可以使用以下Python脚本导入：

```python
import json
from knowledge.models import DanceProject, ActionModule, SpecificMove, MoveAttribute, LearningResource, KnowledgePoint

def import_dance_data(json_file_path):
    """从JSON文件导入舞蹈数据"""
    with open(json_file_path, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    project_name = data['dance_project_name']
    project = DanceProject.objects.get(name=project_name)
    
    for module_data in data['modules']:
        module, created = ActionModule.objects.get_or_create(
            dance_project=project,
            name=module_data['name'],
            defaults={
                'description': module_data['module_description'],
                'order_index': module_data.get('order_index', 1)
            }
        )
        
        for move_data in module_data['moves']:
            move, created = SpecificMove.objects.get_or_create(
                action_module=module,
                name=move_data['name'],
                defaults={
                    'description': move_data['description'],
                    'difficulty': move_data['difficulty'],
                    'duration': move_data['duration'],
                    'order_index': move_data.get('order_index', 1)
                }
            )
            
            # 创建动作属性
            if 'attributes' in move_data:
                MoveAttribute.objects.update_or_create(
                    specific_move=move,
                    defaults=move_data['attributes']
                )
            
            # 创建学习资源
            for res_data in move_data.get('resources', []):
                LearningResource.objects.get_or_create(
                    specific_move=move,
                    title=res_data['title'],
                    defaults={
                        'resource_type': res_data['type'],
                        'url': res_data['url'],
                        'duration': res_data.get('duration')
                    }
                )
            
            # 创建知识点
            for kp_data in move_data.get('knowledge_points', []):
                KnowledgePoint.objects.get_or_create(
                    specific_move=move,
                    name=kp_data['name'],
                    defaults=kp_data
                )
    
    print(f"成功导入项目：{project_name}")

# 使用示例
# import_dance_data('data/京西太平鼓.json')
```

---

## 💡 AI提示词优化建议

### 基础提示词
```
你是一位非遗传统舞蹈专家，精通中国各地民间舞蹈、宫廷舞蹈、宗教祭祀舞蹈和少数民族舞蹈。

请为[舞蹈项目名称]生成专业的知识图谱数据，包括：
1. 4个基础动作模块
2. 每个模块10-15个具体招式
3. 每个招式的详细信息

要求：
- 招式名称要有传统文化韵味
- 动作描述专业准确
- 体现该舞蹈的独特风格
- 难度循序渐进
- 融入文化内涵和历史背景
```

### 进阶提示词（更详细）
```
作为资深舞蹈编导和非遗传承人，请深入分析[舞蹈项目名称]的动作体系：

【背景信息】
- 舞蹈起源：[起源地/历史]
- 舞蹈特点：[风格特色]
- 表演场合：[节庆/仪式/娱乐等]
- 使用道具：[鼓/扇/绸等]

【生成要求】
1. 设计4个逻辑递进的训练模块
2. 每个模块包含基础到进阶的招式
3. 招式要体现该舞蹈的核心技法
4. 动作属性要科学准确（解剖学角度）
5. 常见错误要实用（基于教学经验）
6. 知识点要融合技法和文化传播

【输出格式】
按照上述JSON格式输出，确保数据完整、专业、可执行。
```

---

## 📚 参考资源

为了让AI生成更准确的数据，可以提供以下参考资料：

1. **舞蹈视频链接** - 让AI观察实际动作
2. **传承人访谈记录** - 了解技术要点
3. **学术论文** - 获取专业术语
4. **地方志记载** - 了解历史渊源
5. **现有教材** - 参考教学方法

---

## 🎯 快速开始

**第一步**：选择一个舞蹈项目
**第二步**：复制上面的提示词模板
**第三步**：填充项目信息
**第四步**：发送给AI生成数据
**第五步**：检查并调整生成的数据
**第六步**：使用导入脚本存入数据库

---

祝您数据生成顺利！如有问题，随时调整提示词或提供更多背景信息给AI。
