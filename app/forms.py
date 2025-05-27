from django import forms
import re
from django.contrib.auth import authenticate
from .models import Answer, Profile, Question, Tag
from django.contrib.auth.models import User
from django.contrib.auth.password_validation import validate_password

class LoginForm(forms.Form):
    username = forms.CharField()
    password = forms.CharField(widget=forms.PasswordInput)

    def clean_username(self):
        username = self.cleaned_data.get('username', '')
        if not re.match(r'^[a-z0-9_]{5,30}$', username):
            raise forms.ValidationError(
                "Invalid login"
            )
        return username
    def clean_password(self):
        password = self.cleaned_data.get('password', '')
        if len(password) < 8 or len(password) > 20:
            raise forms.ValidationError(
                "Invalid password"
            )
        return password
    def clean(self):
        cleaned_data = super().clean()
        username = cleaned_data.get('username')
        password = cleaned_data.get('password')

        if username and password:
            user = authenticate(username=username, password=password)
            if not user:
                raise forms.ValidationError("Wrong login or password!")
            self.user = user
        return cleaned_data

class SignupForm(forms.ModelForm):
    username = forms.CharField()
    email = forms.EmailField()
    nickname = forms.CharField()
    password = forms.CharField(widget=forms.PasswordInput)
    confirm_password = forms.CharField(widget=forms.PasswordInput)
    img = forms.ImageField(required=False)

    class Meta:
        model = User
        fields = ('username', 'email', 'password')

    def clean_username(self):
        username = self.cleaned_data['username']
        if not re.match(r'^[a-z0-9_]{5,30}$', username):
            raise forms.ValidationError(
                "Invalid login"
            )
        if User.objects.filter(username=username).exists():
            raise forms.ValidationError("This login is already taken.")
        return username

    def clean_email(self):
        email = self.cleaned_data['email']
        if User.objects.filter(email=email).exists():
            raise forms.ValidationError("Account with this email already exists.")
        return email
    
    def clean_password(self):
        password = self.cleaned_data.get('password', '')
        if len(password) < 8 or len(password) > 20:
            raise forms.ValidationError(
                "Invalid password"
            )
        return password
    
    def clean_nickname(self):
        nickname = self.cleaned_data['nickname']
        if len(nickname) < 5:
            raise forms.ValidationError(
                "Invalid nickname"
            )
        return nickname

    def clean(self):
        cleaned_data = super().clean()
        password = cleaned_data.get("password")
        confirm_password = cleaned_data.get("confirm_password")
        if password and confirm_password and password != confirm_password:
            raise forms.ValidationError("Passwords do not match.")
        return cleaned_data

    def save(self, commit=True):
        user = super().save(commit=False)
        # Хэшируем пароль
        user.set_password(self.cleaned_data['password'])
        if commit:
            user.save()
            Profile.objects.create(
                user=user,
                nickname=self.cleaned_data['nickname'],
                img=self.cleaned_data.get('img')
            )
        return user
    
class ProfileEditForm(forms.ModelForm):
    email = forms.EmailField()
    username = forms.CharField()
    nickname = forms.CharField()
    img = forms.ImageField(required=False)

    class Meta:
        model = Profile
        fields = ['nickname', 'img']

    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop('user')
        super().__init__(*args, **kwargs)
        self.fields['email'].initial = self.user.email
        self.fields['username'].initial = self.user.username

    def clean_email(self):
        email = self.cleaned_data.get('email', '')
        if not email or '@' not in email:
            raise forms.ValidationError("Enter a valid email.")
        return email

    def clean_username(self):
        username = self.cleaned_data.get('username', '')
        if not re.match(r'^[a-zA-Z0-9_]{5,30}$', username):
            raise forms.ValidationError("Username must be 5–30 characters, letters, numbers, underscores.")
        if username != self.user.username and User.objects.filter(username=username).exists():
            raise forms.ValidationError("Username already taken.")
        return username

    def save(self, commit=True):
        profile = super().save(commit=False)
        if commit:
            if profile.img and 'img' in self.changed_data:
                old_img = Profile.objects.get(pk=profile.pk).img
                if old_img and old_img.name != profile.img.name:
                    old_img.delete(save=False)
            profile.save()
        return profile
    
class AskForm(forms.Form):
    title = forms.CharField(max_length=50)
    text = forms.CharField(widget=forms.Textarea)
    tags = forms.CharField()

    def clean_title(self):
        title = self.cleaned_data.get('title', '').strip()
        if not title:
            raise forms.ValidationError("Title cannot be empty.")
        if len(title) > 50:
            raise forms.ValidationError("Title must be 50 characters or fewer.")
        return title

    def clean_text(self):
        text = self.cleaned_data.get('text', '').strip()
        if not text:
            raise forms.ValidationError("Text cannot be empty.")
        return text

    def clean_tags(self):
        tags = self.cleaned_data.get('tags', '').strip()
        if not tags:
            raise forms.ValidationError("Tags are required.")
        
        tag_list = [t.strip().lower() for t in tags.split(',') if t.strip()]
        if len(tag_list) == 0:
            raise forms.ValidationError("At least one tag is required.")
        if len(tag_list) > 5:
            raise forms.ValidationError("You can enter up to 5 tags.")
        
        for tag in tag_list:
            if not re.match(r'^[a-z0-9]{1,30}$', tag):
                raise forms.ValidationError(
                    "Tags must be lowercase letters, numbers, up to 30 characters."
                )
        
        # Сохраняем в виде строки через запятую
        return ','.join(tag_list)

class AnswerForm(forms.ModelForm):
    class Meta:
        model = Answer
        fields = ['text']
        widgets = {
            'text': forms.Textarea(attrs={
                'class': 'form-control w-100',
                'rows': 4,
                'placeholder': 'Enter your answer here...'
            }),
        }
        labels = {
            'text': ''
        }

    def clean_text(self):
        text = self.cleaned_data.get('text', '').strip()
        if not text:
            raise forms.ValidationError("Answer text cannot be empty.")
        return text


class VoteForm(forms.Form):
    value = forms.IntegerField()

    def clean_value(self):
        value = self.cleaned_data['value']
        if value not in [1, -1]:
            raise forms.ValidationError("Vote must be either 1 or -1.")
        return value