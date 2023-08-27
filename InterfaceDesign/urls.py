from django.urls import path
from . import views

urlpatterns = [
    path('teams/<int:team_id>/tasks/', views.TaskList.as_view(), name='task-list'),
    path('teams/<int:team_id>/tasks/<int:task_id>/pages/', views.PageList.as_view(), name='page-list'),
    path('teams/<int:team_id>/tasks/<int:task_id>/pages/<int:page_id>/components/', views.ComponentList.as_view(), name='component-list'),
    path('teams/<int:team_id>/tasks/<int:task_id>/pages/<int:page_id>/components/<int:component_id>/', views.ComponentDetail.as_view(), name='component-detail'),
    path('teams/<int:team_id>/tasks/<int:task_id>/pages/<int:page_id>/', views.PageDetail.as_view(), name='page-detail'),
]
