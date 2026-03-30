from django.shortcuts import render

def knowledge_map(request):
    """知识图谱页面"""
    return render(request, 'knowledge/knowledge_map.html')
