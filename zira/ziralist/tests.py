import datetime
from datetime import date, timedelta

from django.contrib.auth import get_user_model, authenticate
from django.test import TestCase

from .models import Task, Project, Status


class SigninTest(TestCase):
    def setUp(self):
        self.user = get_user_model().objects.create_user(
            username="test", password="12test12", email="test@example.com"
        )
        self.user.save()

    def tearDown(self):
        self.user.delete()

    def test_correct(self):
        user = authenticate(username="test", password="12test12")
        self.assertTrue((user is not None) and user.is_authenticated)

    def test_wrong_username(self):
        user = authenticate(username="wrong", password="12test12")
        self.assertFalse(user is not None and user.is_authenticated)

    def test_wrong_pssword(self):
        user = authenticate(username="test", password="wrong")
        self.assertFalse(user is not None and user.is_authenticated)


class TaskTest(TestCase):
    def setUp(self):
        self.user = get_user_model().objects.create_user(
            username="test", password="12test12", email="test@example.com"
        )
        self.user.save()
        self.finish_date = date.today()
        self.proj = Project(name="proj_name", finish_date=self.finish_date)
        self.proj.save()
        self.task = Task(
            author=self.user,
            name="task_name",
            worker=self.user,
            finish_date=self.finish_date + timedelta(days=1),
            stat=Status.objects.all().first(),
            proj=self.proj,
        )
        self.task.save()

    def tearDown(self):
        self.user.delete()
        self.proj.delete()

    def test_read_task(self):
        self.assertEqual(self.task.author, self.user)
        self.assertEqual(self.task.name, "task_name")
        self.assertEqual(self.task.worker, self.user)
        self.assertEqual(self.task.finish_date, self.finish_date + timedelta(days=1))

    def test_update_task_description(self):
        self.task.description = "new description"
        self.task.save()
        self.assertEqual(self.task.description, "new description")

    def test_update_task_finish_date(self):
        self.task.finish_date = self.finish_date + timedelta(days=5)
        self.task.save()
        self.assertEqual(self.task.finish_date, self.finish_date + timedelta(days=5))
