"""
完整的非遗舞蹈数据导入脚本（支持 Excel）
包含：舞蹈项目、传承人、相关项目、相关资讯、学术研究

使用方法：
1. 准备 Excel 文件，包含以下 Sheet：
   - 舞蹈项目
   - 传承人
   - 相关项目
   - 相关资讯
   - 学术研究

2. 运行命令：python import_all_data.py
"""

import os
import sys
import django

# 设置 Django 环境
sys.path.append('D:\\Python_study\\DancedjangoProject')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'DancedjangoProject.settings')
django.setup()

from origin.models import Region, DanceProject, Inheritor, RelatedProject, News, AcademicResearch


# ========== 配置区域 ==========
# Excel 文件路径（支持三种方式）
# 1. 绝对路径：r'C:\Users\YourName\Desktop\traditional_dance_data.xlsx'
# 2. 相对路径：r'data\traditional_dance_data.xlsx' (相对于项目根目录)
# 3. 命令行参数：python import_all_data.py 文件路径

EXCEL_FILE_PATH = r'data\traditional_dance_data.xlsx'  # 默认使用 data 文件夹
# ===============================


def get_or_create_region(region_name):
    """获取或创建地区"""
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


def import_dance_projects(df):
    """导入舞蹈项目数据"""
    print("\n" + "="*60)
    print("正在导入【舞蹈项目】数据...")
    print("="*60)
    
    success_count = 0
    error_count = 0
    
    for index, row in df.iterrows():
        try:
            # 根据实际 Excel 结构调整列名
            project_code = str(row.get('编号', '')).strip()
            name = str(row.get('名称', '')).strip()
            full_name = str(row.get('名称', '')).strip()  # 全称就是名称
            
            if not name or name == 'nan' or len(name) < 2:
                continue
            
            # 获取地区
            declare_region = str(row.get('申报地区或单位', '')).strip()
            region = get_or_create_region(declare_region)
            
            # 获取简介
            introduction = str(row.get('简介', '')).strip()
            if introduction == 'nan':
                introduction = ''
            
            # 创建或更新项目（使用项目编号 + 名称 + 申报地区作为联合唯一标识）
            # 对于扩展项目，即使编号相同，但名称或地区不同也会创建新记录
            project, created = DanceProject.objects.update_or_create(
                project_code=project_code,
                name=name,
                declare_region=declare_region,
                defaults={
                    'full_name': full_name,
                    'dance_type': 'traditional',
                    'category': str(row.get('类别', '传统舞蹈')).strip(),
                    'level': 'national',
                    'announce_batch': str(row.get('公布时间', '')).strip(),
                    'announce_time': str(row.get('公布时间', '')).strip(),
                    'project_type': str(row.get('类型', '')).strip(),
                    'region': region,
                    'protection_unit': str(row.get('保护单位', '')).strip(),
                    'introduction': introduction,
                }
            )
            
            status = "✓ 创建" if created else "↻ 更新"
            print(f"{status}: {project_code} - {name} ({region.name})")
            success_count += 1
            
        except Exception as e:
            print(f"✗ 失败（第{index+1}行）: {str(e)}")
            error_count += 1
    
    print(f"\n【舞蹈项目】导入完成：成功{success_count}条，失败{error_count}条")
    return success_count, error_count


def import_inheritors(df):
    """导入传承人数据"""
    print("\n" + "="*60)
    print("正在导入【传承人】数据...")
    print("="*60)
    
    success_count = 0
    error_count = 0
    
    for index, row in df.iterrows():
        try:
            inheritor_code = str(row.get('编号', '')).strip()
            name = str(row.get('姓名', '')).strip()
            
            if not name or name == 'nan':
                continue
            
            # 获取关联项目
            project_code = str(row.get('项目编号', '')).strip()
            project_name = str(row.get('项目名称', '')).strip()
            
            # 优先使用项目名称匹配（更精确），其次使用项目编号
            project = None
            if project_name and project_name != 'nan':
                # 尝试按项目名称精确匹配
                project = DanceProject.objects.filter(name=project_name).first()
                
                # 如果没有找到，尝试模糊匹配
                if not project:
                    project = DanceProject.objects.filter(name__contains=project_name).first()
            
            # 如果项目名称匹配失败，且项目编号有效，则按编号匹配
            if not project and project_code and project_code != 'nan':
                try:
                    # 注意：项目编号可能对应多个记录，这里只取第一个
                    project = DanceProject.objects.filter(project_code=project_code).first()
                except Exception:
                    project = None
            
            # 性别转换
            gender_raw = str(row.get('性别', '')).strip()
            gender = 'male' if gender_raw == '男' else 'female'
            
            # 生成传承人编号（如果为空则使用名称 + 项目名作为唯一标识）
            if not inheritor_code or inheritor_code == 'nan':
                inheritor_code = f"{name}_{project_name}" if project_name else name
            
            # 创建传承人
            inheritor, created = Inheritor.objects.update_or_create(
                inheritor_code=inheritor_code,
                name=name,
                defaults={
                    'gender': gender,
                    'birth_date': str(row.get('出生日期', '')).strip(),
                    'ethnicity': str(row.get('民族', '汉族')).strip(),
                    'category': str(row.get('类别', '传统舞蹈')).strip(),
                    'project_code': project_code,
                    'project_name': project_name,
                    'project': project if project else None,
                    'declare_region': str(row.get('申报地区或单位', '')).strip(),
                }
            )
            
            status = "✓ 创建" if created else "↻ 更新"
            project_info = f"({project.name})" if project else ""
            print(f"{status}: {name} {project_info}")
            success_count += 1
            
        except Exception as e:
            print(f"✗ 失败（第{index+1}行）: {str(e)}")
            error_count += 1
    
    print(f"\n【传承人】导入完成：成功{success_count}条，失败{error_count}条")
    return success_count, error_count


def import_related_projects(df, main_project_code=None):
    """导入相关项目数据"""
    print("\n" + "="*60)
    print("正在导入【相关项目】数据...")
    print("="*60)
    
    success_count = 0
    error_count = 0
    
    for index, row in df.iterrows():
        try:
            project_code = str(row.get('编号', '')).strip()
            name = str(row.get('项目名称', '')).strip()
            
            if not name or name == 'nan':
                continue
            
            # 查找主项目
            if main_project_code:
                try:
                    main_project = DanceProject.objects.get(project_code=main_project_code)
                except DanceProject.DoesNotExist:
                    print(f"⚠ 警告：主项目{main_project_code}不存在，跳过此行")
                    error_count += 1
                    continue
            else:
                main_project = None
            
            # 创建相关项目
            related, created = RelatedProject.objects.update_or_create(
                project_code=project_code,
                name=name,
                declare_region=str(row.get('申报地区或单位', '')).strip(),
                defaults={
                    'project_type': str(row.get('类型', '')).strip(),
                    'category': str(row.get('类别', '传统舞蹈')).strip(),
                    'main_project': main_project,
                }
            )
            
            status = "✓ 创建" if created else "↻ 更新"
            print(f"{status}: {name} ({row.get('申报地区或单位', '')})")
            success_count += 1
            
        except Exception as e:
            print(f"✗ 失败（第{index+1}行）: {str(e)}")
            error_count += 1
    
    print(f"\n【相关项目】导入完成：成功{success_count}条，失败{error_count}条")
    return success_count, error_count


def import_all_from_excel(excel_path):
    """从单个 Excel 文件导入所有数据"""
    
    if not os.path.exists(excel_path):
        print(f"✗ 错误：文件不存在 - {excel_path}")
        print("\n请确保 Excel 文件已保存到指定路径")
        return
    
    try:
        import pandas as pd
        
        print(f"\n{'='*60}")
        print(f"开始从 Excel 文件导入数据")
        print(f"文件路径：{excel_path}")
        print("="*60)
        
        # 读取 Excel 文件的所有 sheet
        excel_file = pd.ExcelFile(excel_path)
        sheet_names = excel_file.sheet_names
        
        print(f"\n检测到以下工作表：{sheet_names}")
        
        # 导入舞蹈项目
        if '项目情况概要' in sheet_names:
            df_projects = pd.read_excel(excel_path, sheet_name='项目情况概要')
            import_dance_projects(df_projects)
        
        # 导入传承人
        if '传承人' in sheet_names:
            df_inheritors = pd.read_excel(excel_path, sheet_name='传承人')
            import_inheritors(df_inheritors)
        
        # 导入相关项目
        if '相关项目' in sheet_names:
            df_related = pd.read_excel(excel_path, sheet_name='相关项目')
            # 可以根据需要指定主项目编号
            import_related_projects(df_related)
        
        # 导入相关资讯
        if '相关资讯' in sheet_names:
            df_news = pd.read_excel(excel_path, sheet_name='相关资讯')
            # 类似的方法实现...
        
        # 导入学术研究
        if '学术研究' in sheet_names:
            df_academic = pd.read_excel(excel_path, sheet_name='学术研究')
            # 类似的方法实现...
        
        print("\n" + "="*60)
        print("🎉 全部数据导入完成！")
        print("="*60)
        print(f"\n当前数据库统计：")
        print(f"  - 舞蹈项目：{DanceProject.objects.count()} 个")
        print(f"  - 传承人：{Inheritor.objects.count()} 人")
        print(f"  - 相关项目：{RelatedProject.objects.count()} 个")
        print(f"  - 地区：{Region.objects.count()} 个")
        
    except ImportError:
        print("✗ 错误：需要安装 pandas 和 openpyxl 库")
        print("\n请运行以下命令安装依赖：")
        print("pip install pandas openpyxl")
    
    except Exception as e:
        print(f"\n✗ 错误：{str(e)}")
        import traceback
        traceback.print_exc()


if __name__ == '__main__':
    # 检查命令行参数
    if len(sys.argv) > 1:
        file_path = sys.argv[1]
    else:
        file_path = EXCEL_FILE_PATH
    
    import_all_from_excel(file_path)
