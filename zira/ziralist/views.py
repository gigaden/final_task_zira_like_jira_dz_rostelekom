from django.contrib.auth import logout, login
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.models import User
from django.contrib.auth.views import LoginView
from django.http import HttpResponseRedirect
from django.shortcuts import render, redirect
from django.urls import reverse_lazy
from django.views.generic import ListView, UpdateView, CreateView, DeleteView

from django.contrib.auth.mixins import LoginRequiredMixin
from rest_framework.schemas.openapi import AutoSchema
from rest_framework import viewsets, mixins

from .filters import TasklistFilterSet
from .forms import (
    TaskUpdateForm,
    RegisterUserForm,
    LoginUserForm,
    ProjectCreateForm,
    TaskCreateForm,
    ProjectUpdateForm,
    SprintCreateForm,
    SprintUpdateForm,
    StatusCreateForm,
    StatusUpdateForm,
)
from .models import Project, Task, Status, Sprint

from django.db.models.signals import pre_save, post_save
from django.dispatch import receiver

from django.core.mail import send_mail

from .serializers import TaskSerializer

import logging

logger = logging.getLogger(__name__)


# ПРОЕКТЫ
# выводим список всех проектов
class AllProjectView(ListView):
    context_object_name = "projects"
    queryset = Project.objects.all()
    template_name = "ziralist/index.html"


# создаём новый проект
class ProjectCreateView(LoginRequiredMixin, CreateView):
    form_class = ProjectCreateForm
    model = Project
    template_name = "ziralist/project_create.html"
    success_url = "/"
    login_url = reverse_lazy("index")

    def form_valid(self, form):
        form.instance.author = self.request.user
        return super().form_valid(form)


# редактируем проект
class ProjectUpdateView(UpdateView):
    model = Project
    form_class = ProjectUpdateForm

    template_name = "ziralist/project_update_form.html"
    success_url = "/"


# выводим список задач проекта
def project_view(request, pk):
    tasks = Task.objects.filter(proj=pk)
    project = Project.objects.filter(pk=pk).first()
    sprints = Sprint.objects.filter(proj=project)
    return render(
        request,
        "ziralist/project.html",
        context={"tasks": tasks, "project": project, "sprints": sprints},
    )


# удаляем проект
class ProjectDeleteView(DeleteView):
    model = Project
    success_url = "/"
    template_name = "ziralist/project_delete.html"
    context_object_name = "project"


# ЗАДАЧИ
# редактируем задачу
class TaskUpdateView(UpdateView):
    model = Task
    form_class = TaskUpdateForm
    template_name = "ziralist/task_update_form.html"
    success_url = "/"

    def form_valid(self, form):
        form.instance.author_update = self.request.user
        super().form_valid(form)
        return HttpResponseRedirect(
            reverse_lazy("project", args=[form.instance.proj.pk])
        )


# создаём новую задачу
class TaskCreateView(LoginRequiredMixin, CreateView):
    form_class = TaskCreateForm
    model = Task
    template_name = "ziralist/task_create.html"
    success_url = "/"
    login_url = reverse_lazy("index")

    def form_valid(self, form):
        form.instance.author = self.request.user
        return super().form_valid(form)


# удаляем задачу
class TaskDeleteView(DeleteView):
    model = Task
    success_url = "/"
    template_name = "ziralist/task_delete.html"
    context_object_name = "task"


# проверяем изменился ли исполнитель у задачи, или статус и отпраляем уведомление исполнителю
# на доработку: избавиться от try-except, переписать условия
@receiver(pre_save, sender=Task)
def check_worker_changed(sender, instance, **kwargs):
    try:
        obj = sender.objects.get(pk=instance.pk)
        prev_user = obj.worker
        from_user = obj.author_update
        to_user = instance.worker
        if prev_user != to_user:
            from_user_email = User.objects.filter(username=from_user).first().email
            to_user_email = User.objects.filter(username=to_user).first().email
            send_mail(
                "Назначена задача на выполнение",
                f"{to_user}, здравствуйте! "
                f"Пользователь {from_user} с почтой {from_user_email} назначил вам задачу. Пожалуйста ознакомьтесь с ней",
                "gigaden@ya.ru",
                [to_user_email],
                fail_silently=False,
            )
        elif obj.stat != instance.stat:
            from_user_email = User.objects.filter(username=from_user).first().email
            to_user_email = User.objects.filter(username=to_user).first().email
            send_mail(
                "Изменился статус задачи",
                f"{to_user}, здравствуйте! "
                f"Пользователь {from_user} с почтой {from_user_email} изменил статус задачи '{obj.name}' на '{instance.stat}'. Пожалуйста ознакомьтесь с ней",
                "gigaden@ya.ru",
                [to_user_email],
                fail_silently=False,
            )
    except:
        print("exception for pre_save")


# отображаем задачи залогиненого пользователя
def user_task_view(request, pk):
    current_user = User.objects.get(id=pk)
    tasks = Task.objects.filter(worker=current_user).all()
    return render(
        request,
        "ziralist/user_task.html",
        context={"tasks": tasks, "current_user": current_user},
    )


# СПРИНТЫ
# Выводим все задачи спринта
def sprint_task_view(request, pk):
    sprints = Sprint.objects.get(pk=pk)
    tasks = Task.objects.filter(spr=sprints).all()
    return render(
        request, "ziralist/sprint.html", context={"tasks": tasks, "sprints": sprints}
    )


# создаём новый спринт
class SprintCreateView(CreateView):
    form_class = SprintCreateForm
    model = Sprint
    template_name = "ziralist/sprint_create.html"
    success_url = "/"
    login_url = reverse_lazy("index")

    def form_valid(self, form):
        form.instance.author = self.request.user
        return super().form_valid(form)


# удаляем спринт
class SprintDeleteView(DeleteView):
    model = Sprint
    success_url = "/"
    template_name = "ziralist/sprint_delete.html"
    context_object_name = "sprint"


# редактируем спринт
class SprintUpdateView(UpdateView):
    model = Sprint
    form_class = SprintUpdateForm
    template_name = "ziralist/sprint_update_form.html"
    success_url = "/"

    def form_valid(self, form):
        form.instance.author_update = self.request.user
        super().form_valid(form)
        return HttpResponseRedirect(
            reverse_lazy("project", args=[form.instance.proj.pk])
        )


# СТАТУСЫ
# двигаем статус задачи вперёд
def move_task_forward(request, pk):
    task = Task.objects.get(pk=pk)
    current_stat = task.stat
    stat_list = Status.objects.all()
    next_stat = list(stat_list).index(current_stat) + 1
    if next_stat < len(stat_list):
        task.stat = stat_list[next_stat]
        task.author_update = request.user
        task.save()
    return HttpResponseRedirect(reverse_lazy("project", args=[task.proj.pk]))


# двигаем статус задачи назад
def move_task_back(request, pk):
    task = Task.objects.get(pk=pk)
    current_stat = task.stat
    stat_list = Status.objects.all()
    prev_stat = list(stat_list).index(current_stat) - 1
    if prev_stat >= 0:
        task.stat = stat_list[prev_stat]
        task.author_update = request.user
        task.save()
    return HttpResponseRedirect(reverse_lazy("project", args=[task.proj.pk]))


# меняем статусы местами
def move_status_down(request, pk):
    all_status = Status.objects.all()
    current_stat = Status.objects.get(pk=pk)
    status_list = list(Status.objects.all())
    current_index = status_list.index(current_stat)
    next_index = current_index + 1
    if next_index < len(all_status):
        old_status_name = all_status[current_index].name
        new_status_name = all_status[next_index].name
        current_stat.name = new_status_name
        next_status = all_status[next_index]
        next_status.name = old_status_name
        current_stat.save()
        next_status.save()
    return HttpResponseRedirect(reverse_lazy("status"))


def move_status_up(request, pk):
    all_status = Status.objects.all()
    current_stat = Status.objects.get(pk=pk)
    status_list = list(Status.objects.all())
    current_index = status_list.index(current_stat)
    prev_index = current_index - 1
    if prev_index >= 0:
        old_status_name = all_status[current_index].name
        new_status_name = all_status[prev_index].name
        current_stat.name = new_status_name
        next_status = all_status[prev_index]
        next_status.name = old_status_name
        current_stat.save()
        next_status.save()
    return HttpResponseRedirect(reverse_lazy("status"))


# выводим список статусов
class AllStatusView(ListView):
    context_object_name = "status"
    queryset = Status.objects.all()
    template_name = "ziralist/status.html"


# добавляем новый статус
class StatusCreateView(LoginRequiredMixin, CreateView):
    form_class = StatusCreateForm
    model = Status
    template_name = "ziralist/status_create.html"
    success_url = "/"
    login_url = reverse_lazy("index")

    def form_valid(self, form):
        form.instance.author = self.request.user
        return super().form_valid(form)


# удаляем статус
class StatusDeleteView(DeleteView):
    model = Status
    success_url = reverse_lazy("status")
    template_name = "ziralist/status_delete.html"
    context_object_name = "status"


# редактируем статус
class StatusUpdateView(UpdateView):
    model = Status
    form_class = StatusUpdateForm
    template_name = "ziralist/status_update_form.html"
    success_url = "/"

    def form_valid(self, form):
        form.instance.author_update = self.request.user
        super().form_valid(form)
        return HttpResponseRedirect(reverse_lazy("status"))


# АУТЕНТИФИКАЦИЯ
# Добавляем регистрацию и авторизацию
class RegisterUser(CreateView):
    form_class = RegisterUserForm
    template_name = "ziralist/register.html"
    success_url = reverse_lazy("index")

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        return context

    def form_valid(self, form):
        user = form.save()
        login(self.request, user)
        return redirect("index")


class LoginUser(LoginView):
    form_class = LoginUserForm
    template_name = "ziralist/login.html"

    def get_success_url(self):
        return reverse_lazy("index")


def logout_user(request):
    logout(request)
    return redirect("login")


# DRF
# добавляем viewset drf для возможности работы по API
class TaskViewSet(
    mixins.ListModelMixin,
    mixins.CreateModelMixin,
    mixins.RetrieveModelMixin,
    mixins.DestroyModelMixin,
    mixins.UpdateModelMixin,
    viewsets.GenericViewSet,
):
    queryset = Task.objects.all()
    serializer_class = TaskSerializer
    filterset_class = TasklistFilterSet

    # рисуем схему для API
    schema = AutoSchema(
        tags=["Task"],
        component_name="Task",
        operation_id_base="Task",
    )
