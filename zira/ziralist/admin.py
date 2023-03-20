import datetime

from django.contrib import admin

from .models import Project, Sprint, Status, Task, STATUS_DEFAULT


@admin.register(Project)
class ProjectListAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "name",
        "author",
        "description",
        "create_date",
        "update_date",
        "finish_date",
        "is_completed",
        "complete_date",
        "author_update",
    )
    list_editable = ("is_completed",)
    exclude = ("complete_date", "author_update", "author")
    search_fields = ("name", "author")
    list_filter = ("author", "finish_date", "is_completed")

    def save_model(self, request, obj, form, change):
        if getattr(obj, "author", None) is None:
            obj.author = request.user
        obj.author_update = request.user
        obj.save()

        if Status.objects.count() == 0:
            for stat in STATUS_DEFAULT:
                Status.objects.create(name=stat, author=request.user, proj=obj)


@admin.register(Sprint)
class ProjectListAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "name",
        "proj",
        "author",
        "description",
        "create_date",
        "update_date",
        "finish_date",
        "is_completed",
        "complete_date",
        "author_update",
    )
    list_editable = ("is_completed",)
    exclude = ("complete_date", "author", "author_update")
    search_fields = ("name", "author")
    list_filter = ("proj", "author", "finish_date", "is_completed")

    def save_model(self, request, obj, form, change):
        if getattr(obj, "author", None) is None:
            obj.author = request.user
        obj.author_update = request.user
        obj.save()


@admin.register(Status)
class ProjectListAdmin(admin.ModelAdmin):
    list_display = ("id", "name", "author", "proj", "create_date", "update_date")
    exclude = ("author", "proj")
    search_fields = ("name",)
    list_filter = ("proj", "author")


@admin.register(Task)
class ProjectListAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "name",
        "proj",
        "spr",
        "stat",
        "author",
        "worker",
        "description",
        "create_date",
        "update_date",
        "finish_date",
        "is_completed",
        "complete_date",
        "author_update",
    )
    list_editable = ("is_completed",)
    exclude = ("complete_date", "author_update", "author")
    search_fields = ("name", "author")
    list_filter = ("author", "stat", "worker", "finish_date", "is_completed")

    def save_model(self, request, obj, form, change):
        if getattr(obj, "author", None) is None:
            obj.author = request.user
        obj.author_update = request.user
        obj.save()
