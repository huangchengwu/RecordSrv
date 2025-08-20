from .views import *
from rest_framework.routers import DefaultRouter
from django.urls import path, include


# ✅ 添加新的导入
from drf_yasg.views import get_schema_view
from drf_yasg import openapi
from rest_framework import permissions

from .views import *


schema_view = get_schema_view(
    openapi.Info(
        title="API 文档",
        default_version="v1",
        description="接口文档说明",
    ),
    public=True,
    permission_classes=(permissions.AllowAny,),
)


router = DefaultRouter()
router.register(r"Recording", RecordingViewSet)
router.register(r"RecordingGroup", RecordingGroupViewSet, basename="recording_group")


urlpatterns = [
    path("index/", Index),
    path("analyze_recording/", analyze_recording.as_view()),
]


urlpatterns += router.urls  # 将路由器中的所以路由信息追到到django的路由列表中
