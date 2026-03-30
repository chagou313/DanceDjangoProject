"""
传统舞蹈数据导入脚本
用于将国家级非物质文化遗产传统舞蹈数据导入数据库

使用方法：
python manage.py shell < import_dance_data.py

或者在 Django shell 中运行：
from origin.management.commands.import_dance_data import import_dance_origin_data
import_dance_origin_data()
"""

import os
import sys
import django

# 设置 Django 环境
sys.path.append('D:\\Python_study\\DancedjangoProject')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'DancedjangoProject.settings')
django.setup()

from origin.models import Region, DanceProject


def create_regions():
    """创建地区数据"""
    regions_data = [
        ('北京市', '110000'),
        ('河北省', '130000'),
        ('辽宁省', '210000'),
        ('山东省', '370000'),
        ('陕西省', '610000'),
    ]
    
    created_regions = {}
    for name, code in regions_data:
        region, created = Region.objects.get_or_create(
            code=code,
            defaults={
                'name': name,
                'level': 1,  # 省级
            }
        )
        if created:
            print(f"✓ 创建地区：{name}")
        created_regions[name] = region
    
    return created_regions


def import_dance_origin_data():
    """导入传统舞蹈数据"""
    
    # 先创建地区
    regions = create_regions()
    
    # 传统舞蹈数据（根据您提供的数据）
    dances_data = [
        {
            'name': '京西太平鼓',
            'region_name': '北京市',
            'category': '传统舞蹈',
            'announce_time': '2006 (第一批)',
            'type': '新增项目',
            '申報_unit': '北京市门头沟区',
            'protection_unit': '北京市门头沟区公共文化中心（北京市门头沟区文化旅游产业促进中心）',
        },
        {
            'name': '京西太平鼓（石景山太平鼓）',
            'region_name': '北京市',
            'category': '传统舞蹈',
            'announce_time': '2008 (第二批)',
            'type': '扩展项目',
            '申報_unit': '北京市石景山区',
            'protection_unit': '北京市石景山区非物质文化遗产保护中心',
        },
        {
            'name': '京西太平鼓（怪村太平鼓）',
            'region_name': '北京市',
            'category': '传统舞蹈',
            'announce_time': '2008 (第二批)',
            'type': '扩展项目',
            '申報_unit': '北京市丰台区',
            'protection_unit': '北京市丰台区王佐镇怪村村民委员会',
        },
        {
            'name': '秧歌（昌黎地秧歌）',
            'region_name': '河北省',
            'category': '传统舞蹈',
            'announce_time': '2006 (第一批)',
            'type': '新增项目',
            '申報_unit': '河北省昌黎县',
            'protection_unit': '昌黎县文化馆',
        },
        {
            'name': '秧歌（抚顺地秧歌）',
            'region_name': '辽宁省',
            'category': '传统舞蹈',
            'announce_time': '2006 (第一批)',
            'type': '新增项目',
            '申報_unit': '辽宁省抚顺市',
            'protection_unit': '抚顺市非物质文化遗产保护中心',
        },
        {
            'name': '秧歌（鼓子秧歌）',
            'region_name': '山东省',
            'category': '传统舞蹈',
            'announce_time': '2006 (第一批)',
            'type': '新增项目',
            '申報_unit': '山东省商河县',
            'protection_unit': '商河县文化馆（商河县京剧团、商河县美术馆）',
        },
        {
            'name': '秧歌（胶州秧歌）',
            'region_name': '山东省',
            'category': '传统舞蹈',
            'announce_time': '2006 (第一批)',
            'type': '新增项目',
            '申報_unit': '山东省胶州市',
            'protection_unit': '胶州市文化服务中心',
        },
        {
            'name': '秧歌（海阳大秧歌）',
            'region_name': '山东省',
            'category': '传统舞蹈',
            'announce_time': '2006 (第一批)',
            'type': '新增项目',
            '申報_unit': '山东省海阳市',
            'protection_unit': '海阳市文化馆',
        },
        {
            'name': '秧歌（陕北秧歌）',
            'region_name': '陕西省',
            'category': '传统舞蹈',
            'announce_time': '2006 (第一批)',
            'type': '新增项目',
            '申報_unit': '陕西省绥德县',
            'protection_unit': '绥德县文化馆',
        },
        {
            'name': '秧歌（济阳鼓子秧歌）',
            'region_name': '山东省',
            'category': '传统舞蹈',
            'announce_time': '2008 (第二批)',
            'type': '扩展项目',
            '申報_unit': '山东省济阳县',
            'protection_unit': '济阳区文化馆',
        },
    ]
    
    print("\n开始导入传统舞蹈数据...")
    print("=" * 60)
    
    success_count = 0
    for dance_info in dances_data:
        try:
            region_name = dance_info['region_name']
            region = regions.get(region_name)
            
            # 创建或更新舞蹈数据
            dance, created = DanceProject.objects.update_or_create(
                name=dance_info['name'],
                region=region,
                defaults={
                    'dance_type': 'traditional',  # 传统舞蹈
                    'history': f"""【公布时间】{dance_info['announce_time']}
【项目类型】{dance_info['type']}
【类别】{dance_info['category']}
【申报地区】{dance_info['申報_unit']}
【保护单位】{dance_info['protection_unit']}

这是一项珍贵的国家级非物质文化遗产传统舞蹈项目，具有重要的历史文化价值和艺术特色。""",
                    'folk_customs': f"申报地区：{dance_info['申報_unit']}",
                    'characteristics': f"保护单位：{dance_info['protection_unit']}",
                }
            )
            
            if created:
                print(f"✓ 创建成功：{region.name} - {dance.name}")
            else:
                print(f"↻ 更新成功：{region.name} - {dance.name}")
            
            success_count += 1
            
        except Exception as e:
            print(f"✗ 导入失败：{dance_info['name']} - 错误：{str(e)}")
    
    print("=" * 60)
    print(f"\n导入完成！成功：{success_count}/{len(dances_data)}")
    print(f"当前数据库中共有 {DanceProject.objects.count()} 条非遗舞蹈数据")


if __name__ == '__main__':
    import_dance_origin_data()
