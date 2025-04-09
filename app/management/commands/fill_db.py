import random
from django.core.management.base import BaseCommand
from app.models import AnswerLike, Profile, QuestionLike, User, Question, Answer, Tag
from django.db import transaction

class Command(BaseCommand):

    def add_arguments(self, parser):
        parser.add_argument('ratio', type=int, help='Коэффициент заполнения сущностей')
        parser.add_argument('--delete', action='store_true', help='Удалить всех пользователей')

    def handle(self, *args, **kwargs):
        ratio = kwargs['ratio']
        delete_users = kwargs['delete']

        user_count = ratio
        question_count = ratio * 10
        answer_count = ratio * 100
        tag_count = ratio
        likes_count = ratio * 200

        if delete_users:
            User.objects.all().delete()
            Question.objects.all().delete()
            Tag.objects.all().delete()
            self.stdout.write('Все данные удалены')
            return
        


        # профили и пользователи
        password='password123'
        img = '/static/img/profile.jpg'
        profiles = []
        users = []
        for i in range(user_count):
            username=f'user{i}'
            email = f'{username}@mail.ru'
            profiles.append(Profile(nickname = f'Mr. {username}',img = img))
            users.append(User(username = username,password = password,email = email))
        for user in users:
                user.save()
        
        with transaction.atomic():
            for i, profile in enumerate(profiles):
                profile.user = users[i]
        for profile in profiles:
                profile.save()

        self.stdout.write(f'Добавлено {user_count} пользователей с профилями')

        # теги
        tags = [Tag(name=f'Tag{i}') for i in range(tag_count)]
        Tag.objects.bulk_create(tags)
        self.stdout.write(f'Добавлено {tag_count} тегов')
        tags = list(Tag.objects.all())

        #вопросы
        profiles = profiles[:user_count // 10]
        tags = tags[:tag_count // 10]
        text = 'Etiam imperdiet dapibus urna, sed pharetra orci fringilla a. Integer porta lobortis felis, sed auctor tellus posuere at. Proin quam quam, consectetur facilisis velit nec, ultrices tincidunt eros. Pellentesque porttitor tristique nisi, non commodo lectus rhoncus nec. Nunc ac diam arcu. Duis posuere turpis et velit lobortis, consequat placerat magna ultricies. Cras facilisis, ante a congue molestie, dui lorem feugiat mauris, ac elementum diam magna eget ligula. Nam at metus laoreet, iaculis neque eget, scelerisque elit. Mauris ultricies tincidunt semper. Suspendisse pellentesque tristique lobortis. Vestibulum ac gravida metus. Praesent lobortis massa sed odio dictum, a hendrerit sem convallis. Duis quis lacinia dui, eget imperdiet erat. Vestibulum in fermentum ante, egestas sollicitudin orci. Aenean nisi velit, dictum id pharetra eu, hendrerit non est. Integer nec urna id mi pulvinar dictum vitae eu elit.'
        questions = []
        for i in range(question_count):
            author=random.choice(profiles)
            title=f'Почему так происходит {i}?'
            questions.append(Question(author = author, title = title, text = text))
        batch_size = 10000
        for i in range(0, len(questions), batch_size):
            Question.objects.bulk_create(questions[i:i+batch_size])
        questions = list(Question.objects.all())
        for question in questions:
            question_tags = random.sample(tags, random.randint(1, 3))
            question.tags.set(question_tags)
        self.stdout.write(f'Добавлено {question_count} вопросов')

        # ответы
        text = 'Donec lacinia eros et risus consectetur, et interdum mauris lacinia. Nam varius commodo arcu. Donec faucibus sem velit, eu consectetur elit porta varius. Mauris dolor velit, sollicitudin egestas rhoncus sit amet, efficitur eget quam. In placerat dui sit amet dolor pulvinar bibendum.'
        questions = questions[:question_count // 10]
        answers = []
        for i in range(answer_count):
            author=random.choice(profiles)
            question = random.choice(questions)
            answers.append(Answer(author = author, question = question, text = text))
        for i in range(0, len(answers), batch_size):
            Answer.objects.bulk_create(answers[i:i+batch_size])
        answers = list(Answer.objects.all())
        self.stdout.write(f'Добавлено {answer_count} ответов')

        # лайки
        answers = list(Answer.objects.all())
        questions = list(Question.objects.all())
        profiles = list(Profile.objects.all())
        likes_questions = []
        likes_answers = []
        existing_question_likes = set()
        existing_answer_likes = set()

        target_question_likes = likes_count // 2
        target_answer_likes = likes_count // 2
        created_question_likes = 0
        created_answer_likes = 0

        while created_question_likes < target_question_likes or created_answer_likes < target_answer_likes:
            if created_question_likes < target_question_likes:
                user = random.choice(profiles)
                question = random.choice(questions)
                question_like_key = (user.id, question.id)
                value = random.choice([1, -1])
                if question_like_key not in existing_question_likes:
                    likes_questions.append(QuestionLike(user=user, value=value, question=question))
                    existing_question_likes.add(question_like_key)
                    created_question_likes += 1

            if created_answer_likes < target_answer_likes:
                user = random.choice(profiles)
                answer = random.choice(answers)
                answer_like_key = (user.id, answer.id)
                value = random.choice([1, -1])
                if answer_like_key not in existing_answer_likes:
                    likes_answers.append(AnswerLike(user=user, value=value, answer=answer))
                    existing_answer_likes.add(answer_like_key)
                    created_answer_likes += 1

        for i in range(0, len(likes_answers), batch_size):
            AnswerLike.objects.bulk_create(likes_answers[i:i+batch_size])
        for i in range(0, len(likes_questions), batch_size):
            QuestionLike.objects.bulk_create(likes_questions[i:i+batch_size])

        self.stdout.write(f'Добавлено {likes_count} оценок пользователей')
