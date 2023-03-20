from django.contrib import admin
from django.urls import path, include
from rest_framework.schemas import get_schema_view

urlpatterns = [
    path("admin/", admin.site.urls),
    path("", include("ziralist.urls")),
    path("api/", include("ziralist.api_urls")),
    path(
        "openapi/",
        get_schema_view(
            title="Studying", description="API for all things …", version="1.0.0"
        ),
        name="openapi-schema",
    ),
]
