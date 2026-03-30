"""
生成交流社区测试帖子数据
"""
from django.core.management.base import BaseCommand
from community.models import Topic, Post
from django.contrib.auth.models import User
import random


class Command(BaseCommand):
    help = '生成 10 个非遗舞蹈相关的测试帖子'

    def handle(self, *args, **kwargs):
        self.stdout.write('=' * 60)
        self.stdout.write('开始生成测试帖子数据...')
        self.stdout.write('=' * 60)
        
        # 获取或创建话题分类
        topics_data = [
            {'name': '舞蹈技巧', 'description': '分享舞蹈学习技巧与心得', 'icon': 'fa-star', 'color': '#D8BF64'},
            {'name': '文化传承', 'description': '探讨非遗文化的传承与发展', 'icon': 'fa-book', 'color': '#E8D59B'},
            {'name': '演出活动', 'description': '发布各类舞蹈演出和交流活动', 'icon': 'fa-calendar', 'color': '#F5EDC8'},
            {'name': '民俗风情', 'description': '展示各地民族舞蹈特色', 'icon': 'fa-globe', 'color': '#D4AF37'},
            {'name': '教学分享', 'description': '舞蹈教学资源与方法分享', 'icon': 'fa-chalkboard-teacher', 'color': '#C9A961'},
        ]
        
        topics = []
        for topic_data in topics_data:
            topic, created = Topic.objects.get_or_create(
                name=topic_data['name'],
                defaults={
                    'description': topic_data['description'],
                    'icon': topic_data['icon'],
                    'color': topic_data['color'],
                    'sort_order': random.randint(1, 10)
                }
            )
            topics.append(topic)
            if created:
                self.stdout.write(f'✓ 创建话题：{topic.name}')
            else:
                self.stdout.write(f'• 使用已存在话题：{topic.name}')
        
        # 获取用户
        users = list(User.objects.all()[:5])
        if not users:
            self.stdout.write('错误：数据库中没有用户，请先注册用户')
            return
        
        # 帖子数据
        posts_data = [
            {
                'title': '秧歌舞的基本步伐与韵律解析',
                'content': '''大家好！今天想和大家详细聊聊秧歌舞的基本步伐。

秧歌作为中国北方最具代表性的民间舞蹈之一，有着悠久的历史和丰富的表现形式。在学习秧歌时，掌握正确的步伐是至关重要的。

【基本步伐要点】
1. 十字步：这是秧歌最基础的步伐，要求脚步稳健有力
2. 进退步：前进后退要流畅自然，保持身体平衡
3. 旋转步：转身时要轻盈灵活，注意重心转换

【韵律把握】
秧歌的韵律感很强，通常跟随锣鼓点起舞。建议大家多听音乐，培养节奏感。

欢迎大家一起交流讨论，分享你们的秧歌学习经验！''',
                'topic_name': '舞蹈技巧',
                'tags': '秧歌，步伐技巧，民间舞蹈',
                'views': random.randint(50, 200),
                'likes': random.randint(5, 30),
                'collections': random.randint(2, 15),
                'is_featured': True,
            },
            {
                'title': '探寻云南花鼓灯的文化内涵',
                'content': '''花鼓灯是云南地区独特的民间舞蹈形式，融合了当地多民族文化特色。

【历史渊源】
花鼓灯起源于明清时期，最初是农民庆祝丰收的祭祀舞蹈，后来逐渐发展成为一种艺术表演形式。

【艺术特色】
1. 服饰精美：舞者头戴花冠，身穿彩衣，手持花鼓
2. 动作优美：舞姿轻盈，步伐灵动，充满生活气息
3. 音乐欢快：以花鼓为主要伴奏乐器，节奏明快

【传承意义】
作为非物质文化遗产，花鼓灯不仅是一种舞蹈艺术，更是研究当地民俗文化的重要载体。

有机会一定要去云南实地看看正宗的花鼓灯表演！''',
                'topic_name': '文化传承',
                'tags': '花鼓灯，云南，非遗文化',
                'views': random.randint(80, 250),
                'likes': random.randint(10, 40),
                'collections': random.randint(5, 20),
                'is_featured': True,
            },
            {
                'title': '【活动预告】第十届国际非遗舞蹈节即将开幕',
                'content': '''激动人心的消息！第十届国际非遗舞蹈节将于下月在我市举行！

【活动时间】
2026 年 4 月 15 日 -4 月 20 日

【活动地点】
市文化艺术中心大剧院

【精彩看点】
✨ 来自 20 多个国家的非遗舞蹈团体参演
✨ 传统秧歌、龙舞、狮舞等经典节目
✨ 国际舞蹈大师工作坊
✨ 非遗文化展览

【门票信息】
学生票：50 元
成人票：120 元
家庭套票（2 大 1 小）：280 元

想要报名志愿者的朋友可以在评论区留言哦！

这是一个难得的学习和交流机会，大家不要错过！''',
                'topic_name': '演出活动',
                'tags': '舞蹈节，演出资讯，国际交流',
                'views': random.randint(150, 400),
                'likes': random.randint(20, 60),
                'collections': random.randint(10, 35),
                'is_top': True,
            },
            {
                'title': '蒙古族安代舞的独特魅力',
                'content': '''安代舞是蒙古族的传统舞蹈，具有浓郁的草原文化特色。

【舞蹈特点】
安代舞 originally 是一种治病驱邪的宗教仪式舞蹈，现在已发展成为表达欢乐情感的群众性舞蹈。

主要特征：
- 动作豪迈奔放
- 节奏鲜明有力  
- 参与性强
- 富有感染力

【表演形式】
传统的安代舞表演时，舞者围成圆圈，随着歌声和乐器节奏起舞。动作主要包括：
1. 甩巾：挥舞彩色毛巾
2. 踏步：有力的跺脚动作
3. 跳跃：欢快的跳跃步伐

【文化价值】
2006 年，安代舞被列入首批国家级非物质文化遗产名录。

想学习安代舞的朋友可以找个好老师，亲身感受草原舞蹈的魅力！''',
                'topic_name': '民俗风情',
                'tags': '蒙古族，安代舞，草原文化',
                'views': random.randint(60, 180),
                'likes': random.randint(8, 25),
                'collections': random.randint(3, 12),
            },
            {
                'title': '如何选择合适的舞蹈鞋？',
                'content': '''很多初学者都会问：应该选择什么样的舞蹈鞋？今天就来详细说说。

【不同舞种的用鞋】

🩰 芭蕾舞鞋
- 软底鞋：适合初学者和日常训练
- 足尖鞋：专业舞者使用，需要定制

👞 民族舞鞋
- 布鞋：适合汉族民间舞
- 靴子：适合蒙古族、藏族舞蹈
- 草鞋：某些特定民族舞蹈专用

💃 现代舞鞋
- 赤足或穿软底练功鞋
- 注重脚部与地面的接触感

【选鞋要点】
1. 合脚：不能太紧也不能太松
2. 舒适：内里柔软，透气性好
3. 功能性：根据舞种和动作难度选择
4. 质量：选择正规品牌，做工精细

【保养建议】
- 定期清洁
- 避免暴晒
- 专鞋专用

一双好的舞蹈鞋能让你的舞蹈表现更出色！大家有什么选鞋经验也可以分享~''',
                'topic_name': '教学分享',
                'tags': '舞蹈鞋，装备选择，初学者指南',
                'views': random.randint(100, 300),
                'likes': random.randint(15, 45),
                'collections': random.randint(8, 25),
                'is_featured': True,
            },
            {
                'title': '胶州秧歌的艺术特色与传承',
                'content': '''胶州秧歌是山东胶东地区的传统舞蹈，具有鲜明的地方特色。

【历史背景】
胶州秧歌有 200 多年历史，形成于清代，是胶东人民在劳动生产中创造的民间艺术。

【艺术特征】
1. 表演形式：分为"场秧歌"和"排秧歌"
2. 角色分工：有伞头、鼓手、锣手等不同角色
3. 动作特点：舒展大方，刚劲有力
4. 音乐特色：以打击乐为主，节奏强烈

【代表剧目】
- 《大秧歌》
-《跑四川》
- 《三打祝家庄》

【传承现状】
目前胶州秧歌已列入国家级非遗名录，当地政府和社会各界都在积极推动其传承发展。

作为舞蹈爱好者，我们有责任了解和传播这些优秀的传统文化！''',
                'topic_name': '文化传承',
                'tags': '胶州秧歌，山东，传统艺术',
                'views': random.randint(40, 150),
                'likes': random.randint(5, 20),
                'collections': random.randint(2, 10),
            },
            {
                'title': '广场舞比赛经验分享',
                'content': '''上个月参加了市里的广场舞大赛，获得了二等奖，想和大家分享一些经验。

【赛前准备】
1. 曲目选择：选择节奏明快、正能量的歌曲
2. 编排设计：动作要有变化，队形要丰富
3. 服装道具：统一美观，符合主题
4. 充分排练：至少提前 2 个月开始准备

【比赛技巧】
✨ 表情管理：保持微笑，展现自信
✨ 动作整齐：团队配合最重要
✨ 舞台利用：充分利用整个舞台空间
✨ 互动感染：与观众和评委进行眼神交流

【注意事项】
- 提前到场热身
- 检查音响设备
- 准备备用服装
- 保持良好心态

【心得体会】
比赛结果不是最重要的，重要的是享受过程，展现团队风采。

有想参加比赛的姐妹们可以留言交流哦！''',
                'topic_name': '舞蹈技巧',
                'tags': '广场舞，比赛，经验分享',
                'views': random.randint(120, 350),
                'likes': random.randint(18, 50),
                'collections': random.randint(10, 30),
            },
            {
                'title': '藏族群舞《扎西德勒》赏析',
                'content': '''《扎西德勒》是一部经典的藏族群舞作品，展现了西藏人民的幸福生活。

【作品背景】
该作品创作于 2010 年，由中央民族大学舞蹈学院编导，曾在多个重要比赛中获奖。

【艺术特色】

🎭 主题表达
以"祝福"为主题，通过欢快的舞蹈表达对美好生活的向往。

💃 动作特点
- 颤膝：藏族舞蹈特有的膝盖颤动
- 甩袖：长袖善舞，飘逸优美
- 踏步：节奏明快的脚步动作

🎵 音乐编配
融合传统藏族音乐元素与现代作曲技法，气势恢宏。

【舞台呈现】
- 服装：传统藏袍改良版，色彩艳丽
- 灯光：运用现代舞台灯光技术
- 舞美：融入雪山、经幡等藏族元素

【教育意义】
这部作品不仅是艺术精品，也是民族团结教育的生动教材。

推荐大家都去看看这个精彩的舞蹈！''',
                'topic_name': '民俗风情',
                'tags': '藏族舞蹈，作品赏析，扎西德勒',
                'views': random.randint(70, 220),
                'likes': random.randint(10, 35),
                'collections': random.randint(5, 18),
                'is_featured': True,
            },
            {
                'title': '儿童舞蹈启蒙教育方法谈',
                'content': '''作为一名少儿舞蹈教师，想和大家分享一些儿童舞蹈启蒙的经验。

【启蒙阶段的重要性】
3-6 岁是儿童舞蹈启蒙的黄金期，这个阶段的培养会影响孩子一生的舞蹈兴趣和能力。

【教学方法】

🌟 游戏化教学
将舞蹈动作融入游戏中，让孩子在玩中学。
例如：模仿小动物、讲故事配动作等。

🌟 音乐感知
培养孩子的音乐感和节奏感。
方法：拍手游戏、节奏练习、音乐欣赏等。

🌟 想象力开发
鼓励孩子自由表达，不要过分强调动作标准。
提问："你觉得这个音乐像在做什么？"

【注意事项】
⚠️ 不要过早进行技巧训练
⚠️ 避免过度压腿、下腰等危险动作
⚠️ 以培养兴趣为主
⚠️ 选择适合的音樂和服装

【家长配合】
- 多鼓励少批评
- 创造良好的练习环境
- 坚持送孩子上课
- 参加亲子舞蹈活动

希望每个孩子都能在舞蹈中收获快乐和成长！''',
                'topic_name': '教学分享',
                'tags': '儿童舞蹈，启蒙教育，教学方法',
                'views': random.randint(90, 280),
                'likes': random.randint(12, 40),
                'collections': random.randint(6, 22),
            },
            {
                'title': '【讨论】传统舞蹈如何吸引年轻人？',
                'content': '''最近一直在思考这个问题，想听听大家的看法。

【现状分析】
现在很多传统舞蹈面临传承困难的问题：
- 年轻人不感兴趣
- 学习周期长，见效慢
- 表演机会少
- 经济收益低

【可能的解决方案】

💡 创新表现形式
- 融合现代舞元素
- 结合流行音乐
- 运用科技手段（VR/AR）
- 短视频平台推广

💡 降低学习门槛
- 开发简化版本
- 线上教学课程
- 举办体验活动
- 建立社团组织

💡 增加展示平台
- 校园巡演
- 文化节庆活动
- 网络直播平台
- 综艺节目参演

💡 政策支持
- 政府资金扶持
- 非遗传承人培养
- 学校课程设置
- 社会宣传推广

【成功案例】
有些地方的秧歌队通过抖音等平台直播，吸引了大量年轻粉丝。

大家觉得还有什么好方法？欢迎在评论区畅所欲言！''',
                'topic_name': '文化传承',
                'tags': '传统舞蹈，年轻人，传承发展',
                'views': random.randint(200, 500),
                'likes': random.randint(25, 70),
                'collections': random.randint(12, 40),
                'is_top': True,
            },
        ]
        
        # 创建帖子
        self.stdout.write('\n📝 开始创建帖子:')
        
        for i, post_data in enumerate(posts_data, 1):
            topic_name = post_data.pop('topic_name')
            topic = Topic.objects.get(name=topic_name)
            
            author = random.choice(users)
            
            post = Post.objects.create(
                title=post_data['title'],
                content=post_data['content'],
                author=author,
                topic=topic,
                tags=post_data['tags'],
                views=post_data['views'],
                likes=post_data['likes'],
                collections=post_data['collections'],
                is_featured=post_data.get('is_featured', False),
                is_top=post_data.get('is_top', False),
                status='published',
            )
            
            # 更新评论数（随机生成）
            post.comments_count = random.randint(0, 20)
            post.save(update_fields=['comments_count'])
            
            self.stdout.write(f'✓ 创建帖子 #{i}: {post.title[:30]}...')
        
        # 统计结果
        total_posts = Post.objects.count()
        self.stdout.write(f'\n✅ 成功创建 {len(posts_data)} 个测试帖子')
        self.stdout.write(f'📊 数据库中共有 {total_posts} 个帖子')
        
        self.stdout.write('\n' + '=' * 60)
        self.stdout.write('✨ 测试帖子数据生成完成！')
        self.stdout.write('=' * 60)
