from rest_framework.routers import DefaultRouter
from .views import TaskViewSet

# подключаем роутер для адресов доступа к API

router = DefaultRouter()

app_name = "ziralist"

router.register(
    prefix="tasks",
    viewset=TaskViewSet,
    basename="tasks",
)

urlpatterns = router.urls
