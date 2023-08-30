from django.urls import path
from .views import ChatMessageListView, search_group_messages, search_direct_messages, \
    UploadFileView, UploadImageView, GetChatGroupUsers, GetChatGroupByTeamID
from . import views
from .views import CreateChatGroupView, InviteToChatGroupView, DisbandChatGroupView, LeaveChatGroupView

urlpatterns = [
    path('chatroom/messages/<int:group_id>/', ChatMessageListView.as_view(), name='chat_message_list'),
    path('chatroom/notifications/', views.NotificationListView.as_view(), name='notification-list'),
    path('chatroom/notifications/<int:notification_id>/', views.NotificationDetailView.as_view(), name='notification-detail'),
    path('chatroom/search/group/<int:group_id>/', search_group_messages, name='search-group-messages'),
    path('chatroom/search/direct/<int:sender_id>/<int:receiver_id>/', search_direct_messages, name='search-direct-messages'),
    path('chatroom/uploadfile/', UploadFileView.as_view()),
    path('chatroom/uploadimage/', UploadImageView.as_view()),
    path('chatroom/create_group/', CreateChatGroupView.as_view(), name='create_chat_group'),
    path('chatroom/invite_to_group/<int:chat_group_id>/', InviteToChatGroupView.as_view(), name='invite_to_chat_group'),
    path('chatroom/disband_group/<int:chat_group_id>/', DisbandChatGroupView.as_view(), name='disband_chat_group'),
    path('chatroom/leave_group/<int:chat_group_id>/', LeaveChatGroupView.as_view(), name='leave_chat_group'),
    path('chatroom/group/<int:group_id>/users/', GetChatGroupUsers.as_view(), name='chat_group_users'),
    path('chatroom/team/<int:team_id>/chatgroups/', GetChatGroupByTeamID.as_view(), name='chat_groups_by_team'),
]
