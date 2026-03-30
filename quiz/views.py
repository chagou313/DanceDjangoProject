from django.shortcuts import render

def quiz_list(request):
    """答题闯关页面"""
    return render(request, 'quiz/quiz_list.html')
