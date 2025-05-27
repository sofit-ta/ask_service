from django.http import JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.urls import reverse, reverse_lazy
from app.forms import AnswerForm, AskForm, LoginForm, ProfileEditForm, SignupForm
from .models import AnswerLike, Profile, QuestionLike, Tag, Question, Answer
from django.contrib.auth.decorators import login_required
from django.contrib import auth
from django.views.decorators.http import require_POST
from django.db.models import Sum
from django.views.decorators.csrf import csrf_protect


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

# @require_POST
# @login_required
# def like(request):
#     model_type = request.POST.get("type")
#     object_id = request.POST.get("id")
#     value = int(request.POST.get("value"))
#     profile = request.user.profile

#     try:
#         if model_type == "question":
#             question = Question.objects.get(id=object_id)
#             like_obj, created = QuestionLike.objects.update_or_create(
#                 user=profile,
#                 question=question,
#                 defaults={'value': value}
#             )
#             total = question.like.aggregate(total=Sum('value'))['total'] or 0
#             question.likes_amount = total
#             question.save(update_fields=['likes_amount'])

#             return JsonResponse({
#                 'success': True,
#                 'likes_amount': total
#             })

#         elif model_type == "answer":
#             answer = Answer.objects.get(id=object_id)
#             like_obj, created = AnswerLike.objects.update_or_create(
#                 user=profile,
#                 answer=answer,
#                 defaults={'value': value}
#             )

#             total = answer.like.aggregate(total=Sum('value'))['total'] or 0
#             print(f"Total for {model_type} {object_id}: {total}")
#             answer.likes_amount = total
#             answer.save(update_fields=['likes_amount'])

#             return JsonResponse({
#                 'success': True,
#                 'likes_amount': total
#             })

#         else:
#             return JsonResponse({'success': False, 'error': 'Invalid type'}, status=400)

#     except Exception as e:
#         return JsonResponse({'success': False, 'error': str(e)}, status=500)

@require_POST
@login_required
def like(request):
    model_type = request.POST.get("type")
    object_id = request.POST.get("id")
    value = int(request.POST.get("value"))
    profile = request.user.profile

    try:
        if model_type == "question":
            question = Question.objects.get(id=object_id)
            like_obj, created = QuestionLike.objects.get_or_create(
                user=profile,
                question=question,
                defaults={'value': value}
            )

            if not created and like_obj.value == value:
                # Удаляем голос, если он совпадает с текущим
                like_obj.delete()
                total = question.like.aggregate(total=Sum('value'))['total'] or 0
                question.likes_amount = total
                question.save(update_fields=['likes_amount'])
                return JsonResponse({
                    'success': True,
                    'likes_amount': total,
                    'user_vote': None  # Пользователь больше не голосовал
                })
            else:
                # Меняем значение голоса
                like_obj.value = value
                like_obj.save()
                total = question.like.aggregate(total=Sum('value'))['total'] or 0
                question.likes_amount = total
                question.save(update_fields=['likes_amount'])
                return JsonResponse({
                    'success': True,
                    'likes_amount': total,
                    'user_vote': value
                })

        elif model_type == "answer":
            answer = Answer.objects.get(id=object_id)
            like_obj, created = AnswerLike.objects.get_or_create(
                user=profile,
                answer=answer,
                defaults={'value': value}
            )

            if not created and like_obj.value == value:
                like_obj.delete()
                total = answer.like.aggregate(total=Sum('value'))['total'] or 0
                answer.likes_amount = total
                answer.save(update_fields=['likes_amount'])
                return JsonResponse({
                    'success': True,
                    'likes_amount': total,
                    'user_vote': None
                })
            else:
                like_obj.value = value
                like_obj.save()
                total = answer.like.aggregate(total=Sum('value'))['total'] or 0
                answer.likes_amount = total
                answer.save(update_fields=['likes_amount'])
                return JsonResponse({
                    'success': True,
                    'likes_amount': total,
                    'user_vote': value
                })

        else:
            return JsonResponse({'success': False, 'error': 'Invalid type'}, status=400)

    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)}, status=500)

from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.decorators import login_required
from .models import Answer, Question

@csrf_exempt
@login_required
def mark_correct_answer(request, answer_id):
    try:
        answer = Answer.objects.select_related('question__author').get(id=answer_id)

        # Проверяем, что пользователь — автор вопроса
        if answer.question.author != request.user.profile:
            return JsonResponse({'success': False, 'error': 'You are not the author of this question'}, status=403)

        is_correct = int(request.POST.get('is_correct', 0))
        Answer.objects.filter(question=answer.question).update(is_correct=False)  # Только один правильный
        answer.is_correct = bool(is_correct)
        answer.save(update_fields=['is_correct'])

        return JsonResponse({'success': True})

    except Answer.DoesNotExist:
        return JsonResponse({'success': False, 'error': 'Answer not found'}, status=404)
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)}, status=500)



# Create your views here.
def index(request):
    questions = Question.objects.new()
    user_votes = {}
    if request.user.is_authenticated:
        user_profile = request.user.profile

        # Получаем все лайки по вопросам
        question_likes = QuestionLike.objects.filter(user=user_profile)
        for like in question_likes:
            user_votes[f"question_{like.question_id}"] = like.value

        # Получаем все лайки по ответам
        answer_likes = AnswerLike.objects.filter(user=user_profile)
        for like in answer_likes:
            user_votes[f"answer_{like.answer_id}"] = like.value


    context = get_base_context(request.user)
    context['questions'] = paginate(questions, request)
    context.update({'user_votes': user_votes})
    return render(request, 'index.html', context)

def hot_questions(request):
    questions = Question.objects.best()
    user_votes = {}
    if request.user.is_authenticated:
        user_profile = request.user.profile

        question_likes = QuestionLike.objects.filter(user=user_profile)
        for like in question_likes:
            user_votes[f"question_{like.question_id}"] = like.value

        # Получаем все лайки по ответам
        answer_likes = AnswerLike.objects.filter(user=user_profile)
        for like in answer_likes:
            user_votes[f"answer_{like.answer_id}"] = like.value
    context = get_base_context(request.user)
    context['questions'] = paginate(questions, request)
    context.update({'user_votes': user_votes})
    return render(request, 'hot.html', context)

def question(request, question_id):
    q = get_object_or_404(Question, id=question_id)
    answers_qs = Answer.objects.for_question(question_id)

    is_author = False
    user_votes = {}

    if request.user.is_authenticated:
        user_profile = request.user.profile
        is_author = q.author == user_profile

        # Собираем голоса пользователя
        question_likes = QuestionLike.objects.filter(user=user_profile)
        for like in question_likes:
            user_votes[f"question_{like.question_id}"] = like.value

        answer_likes = AnswerLike.objects.filter(user=user_profile, answer__in=answers_qs)
        for like in answer_likes:
            user_votes[f"answer_{like.answer_id}"] = like.value

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
    context.update({
        'question': q,
        'answers': paginated_answers,
        'form': form,
        'is_author': is_author,
        'user_votes': user_votes
    })

    return render(request, 'question.html', context)

def tag(request, tag_name):
    tag = get_object_or_404(Tag, name = tag_name)
    questions = Question.objects.for_tag(tag_name)
    user_votes = {}
    if request.user.is_authenticated:
        user_profile = request.user.profile

        # Получаем все лайки по вопросам
        question_likes = QuestionLike.objects.filter(user=user_profile)
        for like in question_likes:
            user_votes[f"question_{like.question_id}"] = like.value

        # Получаем все лайки по ответам
        answer_likes = AnswerLike.objects.filter(user=user_profile)
        for like in answer_likes:
            user_votes[f"answer_{like.answer_id}"] = like.value
    context = get_base_context(request.user)
    context['questions'] = paginate(questions, request)
    context['tag'] = tag
    context.update({'user_votes': user_votes})
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