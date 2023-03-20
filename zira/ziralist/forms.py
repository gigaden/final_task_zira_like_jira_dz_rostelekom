import datetime

from django import forms
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth.models import User

from .models import Task, Status, Project, Sprint


class TaskUpdateForm(forms.ModelForm):
    class Meta:
        model = Task
        fields = ["name", "is_completed", "stat", "worker", "spr"]


class TaskCreateForm(forms.ModelForm):
    finish_date = forms.DateTimeField(
        label="Завершить до",
        required=False,
        widget=forms.DateInput(attrs={"type": "datetime-local"}),
        initial=format(datetime.date.today(), "%Y-%m-%dT%H:%M"),
        localize=True,
    )

    class Meta:
        model = Task
        fields = ["name", "description", "worker", "spr", "proj", "stat", "finish_date"]


class ProjectCreateForm(forms.ModelForm):
    finish_date = forms.DateTimeField(
        label="Завершить до",
        required=False,
        widget=forms.DateInput(attrs={"type": "datetime-local"}),
        initial=format(datetime.date.today(), "%Y-%m-%dT%H:%M"),
        localize=True,
    )

    class Meta:
        model = Project
        fields = ["name", "description", "finish_date"]


class ProjectUpdateForm(forms.ModelForm):
    finish_date = forms.DateTimeField(
        label="Завершить до",
        required=False,
        widget=forms.DateInput(attrs={"type": "datetime-local"}),
        initial=format(datetime.date.today(), "%Y-%m-%dT%H:%M"),
        localize=True,
    )

    class Meta:
        model = Project
        fields = ["name", "description", "finish_date", "is_completed"]


class SprintCreateForm(forms.ModelForm):
    finish_date = forms.DateTimeField(
        label="Завершить до",
        required=False,
        widget=forms.DateInput(attrs={"type": "datetime-local"}),
        initial=format(datetime.date.today(), "%Y-%m-%dT%H:%M"),
        localize=True,
    )

    class Meta:
        model = Sprint
        fields = ["name", "description", "finish_date", "proj"]


class SprintUpdateForm(forms.ModelForm):
    finish_date = forms.DateTimeField(
        label="Завершить до",
        required=False,
        widget=forms.DateInput(attrs={"type": "datetime-local"}),
        initial=format(datetime.date.today(), "%Y-%m-%dT%H:%M"),
        localize=True,
    )

    class Meta:
        model = Sprint
        fields = ["name", "description", "finish_date"]


class StatusCreateForm(forms.ModelForm):
    class Meta:
        model = Status
        fields = ["name", "proj"]


class StatusUpdateForm(forms.ModelForm):
    class Meta:
        model = Status
        fields = ["name"]


# Регистрация и авторизация
class RegisterUserForm(UserCreationForm):
    username = forms.CharField(label="Логин", widget=forms.TextInput())
    password1 = forms.CharField(label="Пароль", widget=forms.PasswordInput())
    password2 = forms.CharField(
        label="Подтверждение пароля", widget=forms.PasswordInput()
    )
    email = forms.EmailField(label="Электронная почта", widget=forms.EmailInput())

    class Meta:
        model = User
        fields = ("username", "password1", "password2", "is_staff")


class LoginUserForm(AuthenticationForm):
    username = forms.CharField(label="Логин", widget=forms.TextInput())
    password = forms.CharField(label="Пароль", widget=forms.PasswordInput())
