from pyexpat.errors import messages
from django.shortcuts import get_object_or_404, redirect, render
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.urls import reverse, reverse_lazy
from app.forms import AnswerForm, AskForm, LoginForm, ProfileEditForm, SignupForm
from .models import Profile, Tag, Question, Answer
from django.contrib.auth.decorators import login_required
from django.contrib import auth


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
    q = get_object_or_404(Question, id=question_id)
    answers_qs = Answer.objects.for_question(question_id)

    if request.method == 'POST':
        form = AnswerForm(request.POST)
        if form.is_valid():
            answer = form.save(commit=False)
            answer.question = q
            answer.author = request.user.profile
            answer.save()
            updated_answers = Answer.objects.for_question(question_id)
            paginator = Paginator(updated_answers, 20)
            answer_ids = list(updated_answers.values_list('id', flat=True))
            answer_index = answer_ids.index(answer.id)
            page_number = (answer_index // paginator.per_page) + 1

            return redirect(f"{q.get_absolute_url()}?page={page_number}#answer-{answer.id}")
    else:
        form = AnswerForm()

    paginated_answers = paginate(answers_qs, request)

    context = get_base_context(request.user)
    context.update({ 'question': q, 'answers': paginated_answers, 'form': form})
    return render(request, 'question.html', context)

def tag(request, tag_name):
    tag = get_object_or_404(Tag, name = tag_name)
    questions = Question.objects.for_tag(tag_name)
    context = get_base_context(request.user)
    context['questions'] = paginate(questions, request)
    context['tag'] = tag
    return render(request, 'tag.html', context)

@login_required(login_url=reverse_lazy('login'))
def ask(request):
    if request.method == 'POST':
        form = AskForm(request.POST)
        if form.is_valid():
            question = Question.objects.create(
                author=request.user.profile,
                title=form.cleaned_data['title'],
                text=form.cleaned_data['text']
            )
            tag_names = [tag.strip() for tag in form.cleaned_data['tags'].split(',')]
            for tag_name in tag_names:
                tag, _ = Tag.objects.get_or_create(name=tag_name)
                question.tags.add(tag)
            return redirect('question', question_id=question.id)
    else:
        form = AskForm()

    context = { 'form': form, **get_base_context(request.user)}
    return render(request, 'ask.html', context)

def login(request):
    redirection_path = (
        request.GET.get('next') 
        or request.POST.get('next') 
        or request.GET.get('continue') 
        or request.POST.get('continue') 
        or reverse('settings')
    )
    if not redirection_path.startswith('/'):
        redirection_path = reverse('settings')

    if request.method == 'POST':
        form = LoginForm(request.POST)
        if form.is_valid():
            auth.login(request, form.user)
            return redirect(redirection_path) 
    else:
        form = LoginForm()

    return render(request, 'login.html', {'form': form, 'continue': redirection_path,  **get_base_context(request.user) })

@login_required(login_url=reverse_lazy('login'))
def logout(request):
    redirection_path = request.GET.get('continue') or reverse('index')
    auth.logout(request)
    return redirect(redirection_path)

def signup(request):
    if request.method == "POST":
        form = SignupForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            return redirect(reverse('index'))
        return render(request, 'signup.html', {'form': form, **get_base_context(request.user)})
    else:
        form = SignupForm()
    return render(request, 'signup.html', {'form': form, **get_base_context(request.user)})

@login_required(login_url=reverse_lazy('login'))
def settings(request):
    profile = request.user.profile
    success = False

    if request.method == 'POST':
        form = ProfileEditForm(request.POST, request.FILES, instance=profile, user=request.user)
        if form.is_valid():
            request.user.email = form.cleaned_data['email']
            request.user.username = form.cleaned_data['username']
            request.user.save()
            form.save()
            success = True
    else:
        form = ProfileEditForm(instance=profile, user=request.user)

    context = {
        'form': form,
        'user': request.user,
        'profile': profile,
        'success': success,
        **get_base_context(request.user),
    }
    return render(request, 'settings.html', context)