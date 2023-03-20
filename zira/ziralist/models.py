from django.contrib.auth.models import User
from django.db import models
import datetime

from django.db.models.signals import pre_save, post_save
from django.dispatch import receiver

STATUS_DEFAULT = ["Открыто", "В работе", "На проверке", "Завершена", "Удалена"]


# создаём модель таблицы в нашей БД
class Project(models.Model):
    author = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        verbose_name="автор проекта",
    )
    name = models.CharField(max_length=200, verbose_name="название проекта")
    description = models.TextField(
        null=True, blank=True, verbose_name="описание проекта"
    )
    create_date = models.DateTimeField(
        auto_now_add=True, verbose_name="время создания проекта"
    )
    update_date = models.DateTimeField(
        auto_now=True, verbose_name="время обновления проекта"
    )
    finish_date = models.DateTimeField(
        auto_now=False,
        blank=True,
        null=True,
        default=False,
        verbose_name="завершить проект до",
    )
    is_completed = models.BooleanField(default=False, verbose_name="завершён ли проект")
    complete_date = models.DateTimeField(
        auto_now=False,
        blank=True,
        null=True,
        default=False,
        verbose_name="время завершения проекта",
    )
    author_update = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        verbose_name="кто изменил проект",
        related_name="proj_author_update",
    )

    def save(self, *args, **kwargs):
        if self.is_completed:
            if self.complete_date == None:
                self.complete_date = datetime.datetime.now()
        else:
            self.complete_date = None
        return super().save(*args, **kwargs)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = "Проект"
        verbose_name_plural = "Проекты"
        ordering = ["id"]


# прописываем статусы по умолчанию при создании проекта, если таблица статусов пуста
@receiver(post_save, sender=Project)
def check_status_zero(sender, instance, created, **kwargs):
    if Status.objects.count() == 0:
        for stat in STATUS_DEFAULT:
            Status.objects.create(name=stat, author=instance.author, proj=instance)


class Sprint(models.Model):
    name = models.CharField(max_length=200, verbose_name="название спринта")
    author = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        verbose_name="автор спринта",
    )
    description = models.TextField(
        null=True, blank=True, verbose_name="описание спринта"
    )
    create_date = models.DateTimeField(
        auto_now_add=True, verbose_name="время создания спринта"
    )
    update_date = models.DateTimeField(
        auto_now=True, verbose_name="время обновления спринта"
    )
    finish_date = models.DateTimeField(
        auto_now=False,
        blank=True,
        null=True,
        default=False,
        verbose_name="завершить спринт до",
    )
    is_completed = models.BooleanField(default=False, verbose_name="завершён ли спринт")
    complete_date = models.DateTimeField(
        auto_now=False,
        blank=True,
        null=True,
        default=False,
        verbose_name="время завершения спринта",
    )
    author_update = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        verbose_name="кто изменил спринт",
        related_name="sprint_author_update",
    )
    proj = models.ForeignKey(
        Project, on_delete=models.CASCADE, verbose_name="название проекта"
    )

    def save(self, *args, **kwargs):
        if self.is_completed:
            if self.complete_date == None:
                self.complete_date = datetime.datetime.now()
        else:
            self.complete_date = None
        return super().save(*args, **kwargs)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = "Спринт"
        verbose_name_plural = "Спринты"
        ordering = ["id"]


class Status(models.Model):
    name = models.CharField(max_length=200, verbose_name="название статуса")
    author = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        verbose_name="автор статуса",
    )
    create_date = models.DateTimeField(
        auto_now_add=True, verbose_name="время создания статуса"
    )
    update_date = models.DateTimeField(
        auto_now=True, verbose_name="время изменения статуса"
    )
    proj = models.ForeignKey(
        Project, on_delete=models.CASCADE, verbose_name="название проекта"
    )

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = "Статус"
        verbose_name_plural = "Статусы"
        ordering = ["id"]


class Task(models.Model):
    author = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        verbose_name="автор задачи",
        related_name="worker",
    )
    name = models.CharField(max_length=200, verbose_name="название задачи")
    description = models.TextField(
        null=True, blank=True, verbose_name="описание задачи"
    )
    worker = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        verbose_name="исполнитель",
        null=True,
        blank=True,
    )
    create_date = models.DateTimeField(
        auto_now_add=True, verbose_name="время создания задачи"
    )
    update_date = models.DateTimeField(
        auto_now=True, verbose_name="время обновления задачи"
    )
    finish_date = models.DateTimeField(
        auto_now=False,
        blank=True,
        null=True,
        default=False,
        verbose_name="завершить задачу до",
    )
    is_completed = models.BooleanField(
        default=False, verbose_name="завершёна ли задача"
    )
    complete_date = models.DateTimeField(
        auto_now=False,
        blank=True,
        null=True,
        default=False,
        verbose_name="время завершения задачи",
    )
    author_update = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        verbose_name="кто изменил задачу",
        related_name="task_author_update",
    )
    proj = models.ForeignKey(
        Project,
        on_delete=models.CASCADE,
        verbose_name="название проекта",
        related_name="projects",
    )
    spr = models.ForeignKey(
        Sprint,
        on_delete=models.SET_NULL,
        verbose_name="название спринта",
        related_name="sprints",
        null=True,
        blank=True,
    )
    stat = models.ForeignKey(
        Status,
        on_delete=models.SET_NULL,
        verbose_name="статус задачи",
        default="Только создана",
        null=True,
    )

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = "Задача"
        verbose_name_plural = "Задачи"
        ordering = ["id"]

    def save(self, *args, **kwargs):
        if self.is_completed:
            if self.complete_date == None:
                self.complete_date = datetime.datetime.now()
        else:
            self.complete_date = None
        return super().save(*args, **kwargs)
