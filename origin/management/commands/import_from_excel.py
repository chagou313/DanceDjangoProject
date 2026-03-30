"""
从 Excel/CSV 文件导入传统舞蹈数据

使用说明：
1. 准备 Excel 文件，包含以下列：
   - 编号 (如：Ⅲ-1)
   - 名称 (如：京西太平鼓)
   - 类别 (如：传统舞蹈)
   - 公布时间 (如：2006 (第一批))
   - 类型 (如：新增项目)
   - 申报地区或单位 (如：北京市门头沟区)
   - 保护单位 (如：北京市门头沟区公共文化中心）

2. 将 Excel 文件保存为 .xlsx 或 .csv 格式
3. 运行命令：python manage.py shell < import_from_excel.py

或者修改下方的 EXCEL_FILE_PATH 变量，然后直接运行：
python import_from_excel.py
"""

import os
import sys
import django

# 设置 Django 环境
sys.path.append('D:\\Python_study\\DancedjangoProject')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'DancedjangoProject.settings')
django.setup()

from origin.models import Region, DanceProject


# ========== 配置区域 ==========
EXCEL_FILE_PATH = r'D:\Python_study\DancedjangoProject\traditional_dance_data.xlsx'  # Excel 文件路径
# ===============================


def get_or_create_region(region_name):
    """获取或创建地区"""
    # 简化处理，提取省级行政区
    province_map = {
        '北京': ('北京市', '110000'),
        '河北': ('河北省', '130000'),
        '辽宁': ('辽宁省', '210000'),
        '山东': ('山东省', '370000'),
        '陕西': ('陕西省', '610000'),
        '江苏': ('江苏省', '320000'),
        '浙江': ('浙江省', '330000'),
        '广东': ('广东省', '440000'),
        '四川': ('四川省', '510000'),
        '湖北': ('湖北省', '420000'),
        '湖南': ('湖南省', '430000'),
        '河南': ('河南省', '410000'),
        '安徽': ('安徽省', '340000'),
        '福建': ('福建省', '350000'),
        '江西': ('江西省', '360000'),
        '云南': ('云南省', '530000'),
        '贵州': ('贵州省', '520000'),
        '甘肃': ('甘肃省', '620000'),
        '青海': ('青海省', '630000'),
        '内蒙古': ('内蒙古自治区', '150000'),
        '广西': ('广西壮族自治区', '450000'),
        '西藏': ('西藏自治区', '540000'),
        '宁夏': ('宁夏回族自治区', '640000'),
        '新疆': ('新疆维吾尔自治区', '650000'),
        '黑龙江': ('黑龙江省', '230000'),
        '吉林': ('吉林省', '220000'),
        '山西': ('山西省', '140000'),
        '重庆': ('重庆市', '500000'),
        '天津': ('天津市', '120000'),
        '上海': ('上海市', '310000'),
        '海南': ('海南省', '460000'),
    }
    
    for short, (full_name, code) in province_map.items():
        if short in region_name:
            region, created = Region.objects.get_or_create(
                code=code,
                defaults={'name': full_name, 'level': 1}
            )
            return region
    
    # 如果找不到匹配，使用"其他地区"
    region, created = Region.objects.get_or_create(
        code='990000',
        defaults={'name': '其他地区', 'level': 1}
    )
    return region


def import_from_excel():
    """从 Excel 文件导入数据"""
    
    # 检查文件是否存在
    if not os.path.exists(EXCEL_FILE_PATH):
        print(f"✗ 错误：文件不存在 - {EXCEL_FILE_PATH}")
        print("\n请确保 Excel 文件已保存到指定路径")
        return
    
    try:
        # 尝试使用 pandas 读取 Excel
        import pandas as pd
        
        print(f"正在读取 Excel 文件：{EXCEL_FILE_PATH}")
        print("=" * 60)
        
        # 读取 Excel
        df = pd.read_excel(EXCEL_FILE_PATH)
        
        success_count = 0
        error_count = 0
        
        for index, row in df.iterrows():
            try:
                # 提取数据
                name = str(row.get('名称', '')).strip()
                if not name or name == 'nan':
                    continue
                
                category = str(row.get('类别', '传统舞蹈')).strip()
                announce_time = str(row.get('公布时间', '')).strip()
                dance_type = str(row.get('类型', '新增项目')).strip()
                declare_region = str(row.get('申报地区或单位', '')).strip()
                protection_unit = str(row.get('保护单位', '')).strip()
                
                # 获取地区
                region = get_or_create_region(declare_region)
                
                # 构建历史渊源文本
                history_text = f"""【项目编号】{row.get('编号', '')}
【公布时间】{announce_time}
【项目类型】{dance_type}
【类别】{category}
【申报地区】{declare_region}
【保护单位】{protection_unit}

这是一项珍贵的国家级非物质文化遗产传统舞蹈项目，具有重要的历史文化价值和艺术特色。"""
                
                # 创建或更新舞蹈数据
                dance, created = DanceProject.objects.update_or_create(
                    name=name,
                    region=region,
                    defaults={
                        'dance_type': 'traditional',
                        'history': history_text,
                        'folk_customs': f"申报地区：{declare_region}",
                        'characteristics': f"保护单位：{protection_unit}",
                    }
                )
                
                status = "✓ 创建成功" if created else "↻ 更新成功"
                print(f"{status}: {region.name} - {name}")
                success_count += 1
                
            except Exception as e:
                print(f"✗ 导入失败（第{index+1}行）: {str(e)}")
                error_count += 1
        
        print("=" * 60)
        print(f"\n导入完成！")
        print(f"成功：{success_count} 条")
        print(f"失败：{error_count} 条")
        print(f"当前数据库中共有 {DanceProject.objects.count()} 条非遗舞蹈数据")
        
    except ImportError:
        print("✗ 错误：需要安装 pandas 和 openpyxl 库")
        print("\n请运行以下命令安装依赖：")
        print("pip install pandas openpyxl")
        print("\n或者使用手动方式导入数据（参考 import_dance_data.py 脚本）")
    
    except Exception as e:
        print(f"✗ 错误：{str(e)}")
        print("\n请检查 Excel 文件格式是否正确")


if __name__ == '__main__':
    import_from_excel()
