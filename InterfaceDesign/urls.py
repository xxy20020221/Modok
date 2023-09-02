from django.urls import path
from rest_framework.routers import DefaultRouter
from .views import TaskList, TaskDetail, PageList, PageDetail, ComponentList, ComponentDetail, SetTaskShared, \
    SetTaskPrivate, GetTaskSharedStatus,DesignManage
router = DefaultRouter()
router.register(r'designmanage', DesignManage, basename='designmanage')
urlpatterns = [
    # path('teams/<int:team_id>/tasks/', TaskList.as_view(), name='task-list'),
    # path('teams/<int:team_id>/tasks/<int:task_id>/', TaskDetail.as_view(), name='task-detail'),
    path('teams/<int:team_id>/tasks/<int:task_id>/pages/', PageList.as_view(), name='page-list'),
    path('teams/<int:team_id>/tasks/<int:task_id>/pages/<int:page_id>/', PageDetail.as_view(), name='page-detail'),
    path('teams/<int:team_id>/tasks/<int:task_id>/pages/<int:page_id>/components/', ComponentList.as_view(), name='component-list'),
    path('teams/<int:team_id>/tasks/<int:task_id>/pages/<int:page_id>/components/<int:component_id>/', ComponentDetail.as_view(), name='component-detail'),
    path('task/<int:task_id>/set_shared/', SetTaskShared.as_view(), name='set-task-shared'),
    path('task/<int:task_id>/set_private/', SetTaskPrivate.as_view(), name='set-task-private'),
    path('task/<int:task_id>/is_shared/', GetTaskSharedStatus.as_view(), name='get-task-shared-status'),
]+router.urls
