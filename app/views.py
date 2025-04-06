import copy
from django.shortcuts import render, HttpResponse
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
import random
QUESTIONS = [
    {
        'title': f'Question title {i}?',
        'id': i,
        'text': f'{i} Lorem, ipsum dolor sit amet consectetur adipisicing elit. Commodi et aliquid praesentium maiores labore quasi, ducimus maxime quam Lorem ipsum dolor Maxime doloremque veritatis minus, corrupti vero natus mollitia saepe ratione...',
        'img': '/img/profile.jpg',
        'likes': random.randint(-5,20),
        'number_of_answers': random.randint(0,10),
        'answers': [
            {
                'id': j,
                'text': f'{j} Lorem, ipsum dolor sit amet consectetur adipisicing elit. Commodi et aliquid praesentium maiores labore quasi, ducimus maxime quam Lorem ipsum dolor Maxime doloremque veritatis minus, corrupti vero natus mollitia saepe ratione...',
                'img': '/img/profile.jpg',
                'likes': random.randint(-5,20),
            }for j in range(30)
        ],
        'tags': [ f'tag{j}' for j in range(2) ]

    } for i in range(30)
]
PROFILE = [
    {
        'img': '/img/profile.jpg',
        'nickname': 'Dr. Pepper'
    }]
POPULAR_TAGS = [ f'tag{i}' for i in range(10)]
BEST_MEMBERS = [
    {
        'nickname': f'Mr. member {i}',
        'link': '/'
    } for i in range(5)
]

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

# Create your views here.
def index(request):
    questions = QUESTIONS
    page_obj = paginate(questions, request)
    return render(request, 'index.html', {'questions': page_obj, 'popular_tags':POPULAR_TAGS, 'best_members':BEST_MEMBERS, 'user':PROFILE[0]})

def hot_questions(request):
    questions = copy.deepcopy(list(reversed(QUESTIONS)))
    page_obj = paginate(questions, request)
    return render(request, 'hot.html', {'questions': page_obj,'popular_tags':POPULAR_TAGS, 'best_members':BEST_MEMBERS, 'user':PROFILE[0]})

def question(request, question_id):
    answers = QUESTIONS[question_id]['answers'] 
    page_obj = paginate(answers, request)
    return render(request, 'question.html', {'question': QUESTIONS[question_id],'answers': page_obj,'popular_tags':POPULAR_TAGS, 'best_members':BEST_MEMBERS, 'user':PROFILE[0]})

def tag(request, tag_name):
    filtered_questions = []
    for question in QUESTIONS:
        for tag in question['tags']:
            if tag == tag_name:
                filtered_questions.append(question)
                break
    page_obj = paginate(filtered_questions, request)
    return render(request, 'tag.html', {'questions': page_obj,'popular_tags':POPULAR_TAGS, 'best_members':BEST_MEMBERS, 'user':PROFILE[0], 'tag':tag_name})
# надо доделать страницу с поиском по тегу

def ask(request):
    return render(request, 'ask.html', context={'popular_tags':POPULAR_TAGS, 'best_members':BEST_MEMBERS, 'user':PROFILE[0]})

def login(request):
    return render(request, 'login.html', context={'popular_tags':POPULAR_TAGS, 'best_members':BEST_MEMBERS, 'user':PROFILE[0]})

def signup(request):
    return render(request, 'signup.html',  context={'popular_tags':POPULAR_TAGS, 'best_members':BEST_MEMBERS, 'user':PROFILE[0]})