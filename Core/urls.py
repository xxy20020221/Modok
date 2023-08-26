from rest_framework.routers import DefaultRouter
from django.urls import path
app_name = 'Core'

from .views import (
    UserRegisterView,
    UserLoginView,
    UserLogoutView,
    UserChangeView,
    TeamManagerView,
    InviteView,
    GrantAccess,
    RevokeAccess,
    TaskManage,
    DocumentManage,
)

app_name = 'core'
router = DefaultRouter()
router.register(r'teammanage', TeamManagerView, basename='teammanage')
router.register(r'teaminvite', InviteView, basename='teaminvite')
router.register(r'taskmanage', TaskManage, basename='taskmanage')
router.register(r'documentmanage', DocumentManage, basename='documentmanage')
urlpatterns = [
    path('login/', UserLoginView.as_view(), name='login'),
    path('logout/', UserLogoutView.as_view(), name='logout'),
    path('register/', UserRegisterView.as_view(), name='register'),
    path('userchange/', UserChangeView.as_view(), name='userchange'),
    path('grant/', GrantAccess.as_view(), name='grant'),
    path('revoke/', RevokeAccess.as_view(), name='revoke'),

]+router.urls

