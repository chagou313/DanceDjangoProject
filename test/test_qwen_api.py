"""
测试通义千问API是否配置成功
使用方法: python test_qwen_api.py
"""
import os
import sys
import django

# 设置Django环境
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'DancedjangoProject.settings')
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
django.setup()

from django.conf import settings
from dashscope import Generation
import dashscope

def test_api():
    """测试API调用"""
    print("=" * 60)
    print("通义千问API测试")
    print("=" * 60)
    
    # 1. 检查API Key配置
    api_key = getattr(settings, 'QWEN_API_KEY', '')
    print(f"\n1. 检查API Key配置:")
    if api_key:
        print(f"   ✅ API Key已配置: {api_key[:10]}...{api_key[-10:]}")
    else:
        print(f"   ❌ API Key未配置")
        return False
    
    # 2. 设置API Key
    dashscope.api_key = api_key
    print(f"\n2. 设置API Key: ✅")
    
    # 3. 测试API调用
    print(f"\n3. 测试API调用 (使用 qwen-plus-latest 模型):")
    try:
        response = Generation.call(
            model='qwen-plus-latest',
            messages=[
                {'role': 'user', 'content': '你好，请简单介绍一下你自己'}
            ],
            temperature=0.7,
        )
        
        print(f"   状态码: {response.status_code}")
        
        if response.status_code == 200:
            print(f"   ✅ API调用成功！")
            print(f"\n   AI回复:")
            print(f"   {'-' * 50}")
            print(f"   {response.output.text}")
            print(f"   {'-' * 50}")
            return True
        else:
            print(f"   ❌ API调用失败")
            print(f"   错误信息: {response.message}")
            print(f"   错误代码: {response.code}")
            return False
            
    except Exception as e:
        print(f"   ❌ 发生异常: {str(e)}")
        return False

if __name__ == '__main__':
    success = test_api()
    
    print("\n" + "=" * 60)
    if success:
        print("🎉 测试通过！API配置正确，可以正常使用AI问答功能")
    else:
        print("⚠️  测试失败！请检查:")
        print("   1. API Key是否正确")
        print("   2. 应用是否已发布")
        print("   3. 是否开通了通义千问服务")
        print("   4. 是否有可用额度")
    print("=" * 60)
