import random
from django.core.management.base import BaseCommand
from app.models import AnswerLike, Profile, QuestionLike, User, Question, Answer, Tag
from django.db import transaction
from django.db.models import Sum
from django.contrib.auth.hashers import make_password

class Command(BaseCommand):

    def add_arguments(self, parser):
        parser.add_argument('ratio', type=int, help='Коэффициент заполнения сущностей')
        parser.add_argument('--delete', action='store_true', help='Удалить всю информацию из бд')
        parser.add_argument('--deleteusers', action='store_true', help='Удалить всех пользователей')

    def handle(self, *args, **kwargs):
        ratio = kwargs['ratio']
        delete_everything = kwargs['delete']
        delete_users = kwargs['deleteusers']

        user_count = ratio
        question_count = ratio * 10
        answer_count = ratio * 100
        tag_count = ratio
        likes_count = ratio * 200

        if delete_users:
            Profile.objects.all().delete()
            User.objects.all().delete()
            self.stdout.write(self.style.SUCCESS('Все пользователи успешно удалены'))
            return
        
        if delete_everything:
            AnswerLike.objects.all().delete()
            QuestionLike.objects.all().delete()
            Answer.objects.all().delete()
            Question.objects.all().delete()
            Tag.objects.all().delete()
            Profile.objects.all().delete()
            User.objects.all().delete()
            self.stdout.write(self.style.SUCCESS('Все данные успешно удалены'))
            return

        password = 'password123'
        img = '/img/profile.jpg'
        profiles = []
        users = []

        for i in range(user_count):
            username = f'user{i}'
            email = f'{username}@mail.ru'
            user = User(username=username, password=make_password(password), email=email)
            user.save()
            Profile.objects.create(user=user, nickname=f'Mr. {username}', img=img)

        for user in users:
            user.save()

        for i, profile in enumerate(profiles):
            profile.user = users[i]

        for profile in profiles:
            profile.save()

        self.stdout.write(f'Добавлено {user_count} пользователей с профилями')

        #теги
        tags = [Tag(name=f'Tag{i}') for i in range(tag_count)]
        Tag.objects.bulk_create(tags)
        self.stdout.write(f'Добавлено {tag_count} тегов')
        tags = list(Tag.objects.all())

        #вопросы
        profiles = list(Profile.objects.all())[:user_count // 10]
        tags = tags[:tag_count // 10]
        text = 'Etiam imperdiet dapibus urna, sed pharetra orci fringilla a...'

        questions = []
        for i in range(question_count):
            author = random.choice(profiles)
            title = f'Почему так происходит {i}?'
            questions.append(Question(author=author, title=title, text=text))

        batch_size = 10000
        for i in range(0, len(questions), batch_size):
            Question.objects.bulk_create(questions[i:i+batch_size])

        questions = list(Question.objects.all())
        for question in questions:
            question_tags = random.sample(tags, random.randint(1, 3))
            question.tags.set(question_tags)

        self.stdout.write(f'Добавлено {question_count} вопросов')

        #ответы
        text = 'Donec lacinia eros et risus consectetur...'
        answers = []
        for i in range(answer_count):
            author = random.choice(profiles)
            question = random.choice(questions)
            answers.append(Answer(author=author, question=question, text=text))

        for i in range(0, len(answers), batch_size):
            Answer.objects.bulk_create(answers[i:i+batch_size])

        answers = list(Answer.objects.all())
        self.stdout.write(f'Добавлено {answer_count} ответов')

        #лайки
        profiles = list(Profile.objects.all())
        questions = list(Question.objects.all())
        answers = list(Answer.objects.all())

        target_likes = likes_count 
        created_question_likes = 0
        created_answer_likes = 0
        existing_q_likes = set()
        existing_a_likes = set()

        likes_questions = []
        likes_answers = []

        while created_question_likes + created_answer_likes < target_likes:
            user = random.choice(profiles)
            if random.random() > 0.5 and created_question_likes < (target_likes // 2):
                question = random.choice(questions)
                key = (user.id, question.id)
                if key not in existing_q_likes:
                    value = random.choice([1, -1])
                    likes_questions.append(QuestionLike(user=user, question=question, value=value))
                    existing_q_likes.add(key)
                    created_question_likes += 1
            else:
                if created_answer_likes < (target_likes // 2):
                    answer = random.choice(answers)
                    key = (user.id, answer.id)
                    if key not in existing_a_likes:
                        value = random.choice([1, -1])
                        likes_answers.append(AnswerLike(user=user, answer=answer, value=value))
                        existing_a_likes.add(key)
                        created_answer_likes += 1

        #сохраняем все лайки
        for i in range(0, len(likes_questions), batch_size):
            QuestionLike.objects.bulk_create(likes_questions[i:i+batch_size])

        for i in range(0, len(likes_answers), batch_size):
            AnswerLike.objects.bulk_create(likes_answers[i:i+batch_size])

        self.stdout.write(f'Добавлено {len(likes_questions)} лайков к вопросам')
        self.stdout.write(f'Добавлено {len(likes_answers)} лайков к ответам')

        all_questions = Question.objects.all()
        for question in all_questions:
            answers_for_question = Answer.objects.filter(question=question)
            if answers_for_question.exists():
                Answer.objects.filter(question=question).update(is_correct=False)
                correct_answer = random.choice(list(answers_for_question))
                correct_answer.is_correct = True
                correct_answer.save(update_fields=['is_correct'])

        self.stdout.write(f'Помечено {len(all_questions)} правильных ответов')

        #обновляем вопросы
        for question in Question.objects.all():
            total = question.like.aggregate(total=Sum('value'))['total'] or 0
            question.likes_amount = total
            question.save(update_fields=['likes_amount'])

        #ответы
        for answer in Answer.objects.all():
            total = answer.like.aggregate(total=Sum('value'))['total'] or 0
            answer.likes_amount = total
            answer.save(update_fields=['likes_amount'])

        self.stdout.write('likes_amount обновлены у всех вопросов и ответов')
