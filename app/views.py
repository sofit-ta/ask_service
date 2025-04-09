from django.shortcuts import get_object_or_404, render
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from .models import Profile, Tag, Question, Answer
from django.contrib.auth.models import AnonymousUser


def paginate(objects, request, per_page=20):
    page_number = request.GET.get('page')
    paginator = Paginator(objects, per_page)
    try:
        page = paginator.get_page(page_number)
    except PageNotAnInteger:
        page = paginator.get_page(1)
    except EmptyPage:
        page = paginator.get_page(paginator.num_pages)
    
    return page

def get_base_context(user):
    return {
        'popular_tags': Tag.objects.best(),
        'best_members': Profile.objects.best(),
        'user': user,
        'profile': user.profile if user.is_authenticated and hasattr(user, 'profile') else None
    }


# Create your views here.
def index(request):
    questions = Question.objects.new()
    context = get_base_context(request.user)
    context['questions'] = paginate(questions, request)
    return render(request, 'index.html', context)

def hot_questions(request):
    questions = Question.objects.best()
    context = get_base_context(request.user)
    context['questions'] = paginate(questions, request)
    return render(request, 'hot.html', context)

def question(request, question_id):
    answers = Answer.objects.for_question(question_id)
    context = get_base_context(request.user)
    context['answers'] = paginate(answers, request)
    context['question']= get_object_or_404(Question, id=question_id)
    return render(request, 'question.html', context)

def tag(request, tag_name):
    tag = get_object_or_404(Tag, name = tag_name)
    questions = Question.objects.for_tag(tag_name)
    context = get_base_context(request.user)
    context['questions'] = paginate(questions, request)
    context['tag'] = tag
    return render(request, 'tag.html', context)


def ask(request):
    return render(request, 'ask.html', context=get_base_context(request.user))

def login(request):
    return render(request, 'login.html', context=get_base_context(request.user))

def signup(request):
    return render(request, 'signup.html',  context=get_base_context(request.user))

def settings(request):
    return render(request, 'settings.html',  context=get_base_context(request.user))