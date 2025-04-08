from django.db import models
from django.db.models import Count
from django.contrib.auth.models import User
from django.urls import reverse
import random

class QuestionManager(models.Manager):
    def best(self):
        return self.annotate(likes_amount=Count('like')).order_by('-likes_amount')
    
    def new(self):
        return self.order_by('-created_at')
    
    def for_tag(self, tag_name):
        return self.filter(tags__name=tag_name).annotate(likes_amount=Count('like')).order_by('-likes_amount')
    
class TagManager(models.Manager):
    def best(self):
        return self.annotate(num_questions=Count('question')).order_by('-num_questions')[:10]

class ProfileManager(models.Manager):
    def best(self):
        return self.annotate(num_questions=Count('question')).order_by('-num_questions')[:10]
    
class AnswerManager(models.Manager):
    def for_question(self, question_id):
        return self.filter(question__id=question_id).select_related('author').annotate(likes_amount=Count('like')).order_by('-likes_amount')
    
class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    img = models.ImageField(upload_to='static/img', null=True, blank=True)
    nickname = models.CharField(max_length=255)

    objects = ProfileManager()

    def __str__(self):
        return self.user.username

class Question(models.Model):
    title = models.CharField(max_length=255)
    text = models.TextField()
    author = models.ForeignKey('Profile', on_delete=models.SET_NULL, null=True, related_name='question')
    created_at = models.DateTimeField(auto_now_add=True)
    tags = models.ManyToManyField('Tag', related_name='question')

    objects = QuestionManager()
    def get_absolute_url(self):
        return reverse('question', kwargs={'question_id': self.id})
    def short_text(self, length=250):
        return self.text[:length] + '...' if len(self.text) > length else self.text

class Tag(models.Model):
    name = models.CharField(max_length=50, unique=True)

    objects = TagManager()
    def get_absolute_url(self):
        return reverse('tag', kwargs={'tag_name': self.name})

class Answer(models.Model):
    text = models.TextField()
    author = models.ForeignKey(Profile, on_delete=models.SET_NULL, null=True, related_name='answer')
    created_at = models.DateTimeField(auto_now_add=True)
    question = models.ForeignKey(Question, on_delete=models.CASCADE, related_name='answers')

    objects = AnswerManager()


class QuestionLike(models.Model):
    user =  models.ForeignKey('Profile', on_delete=models.SET_NULL, null=True)
    question = models.ForeignKey(Question, on_delete=models.CASCADE, related_name='like')
    VALUE_CHOICES = {
        (1, 'Like'),
        (-1, 'Dislike')
    }
    value = models.IntegerField(choices=VALUE_CHOICES)
    class Meta():
        unique_together = ["user", "question"]


class AnswerLike(models.Model):
    user =  models.ForeignKey('Profile', on_delete=models.SET_NULL, null=True)
    answer = models.ForeignKey(Answer, on_delete=models.CASCADE, related_name='like')
    VALUE_CHOICES = {
        (1, 'Like'),
        (-1, 'Dislike')
    }
    value = models.IntegerField(choices=VALUE_CHOICES)
    class Meta():
        unique_together = ["user", "answer"]