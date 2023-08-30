from rest_framework.routers import DefaultRouter
from django.urls import path
app_name = 'Core'

from .views import (
    UserRegisterView,
    UserLoginView,
    UserLogoutView,
    UserDetailView,
    TeamManagerView,
    InviteView,
    GrantAccess,
    RevokeAccess,
    TaskManage,
    DocumentManage,
    DuplicateTask,
    list_all_chatrooms,
    DirectoryManage,
    list_directories_and_documents_for_task,
    restore_from_recycle_bin,
    RecycleBinView,
)

app_name = 'core'
router = DefaultRouter()
router.register(r'teammanage', TeamManagerView, basename='teammanage')
router.register(r'teaminvite', InviteView, basename='teaminvite')
router.register(r'taskmanage', TaskManage, basename='taskmanage')
router.register(r'documentmanage', DocumentManage, basename='documentmanage')
router.register(r'directorymanage', DirectoryManage, basename='directorymanage')
urlpatterns = [
    path('login/', UserLoginView.as_view(), name='login'),
    path('logout/', UserLogoutView.as_view(), name='logout'),
    path('register/', UserRegisterView.as_view(), name='register'),
    path('userchange/', UserDetailView.as_view(), name='userchange'),
    path('grant/', GrantAccess.as_view(), name='grant'),
    path('revoke/', RevokeAccess.as_view(), name='revoke'),
    path('duplicate/',DuplicateTask.as_view(),name='duplicate'),
    path('listallchatrooms/',list_all_chatrooms,name='listallchatrooms'),
    path('listalldocuments/',list_directories_and_documents_for_task,name='listalldocuments'),
    path('listrecyclebin/',RecycleBinView.as_view(),name='listrecyclebin'),
    path('restore/',restore_from_recycle_bin,name='restore')

]+router.urls

