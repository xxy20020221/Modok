from django.urls import path
from .views import ChatMessageListView, search_group_messages, search_direct_messages, \
    UploadFileView, UploadImageView
from . import views


urlpatterns = [
    path('chatroom/messages/<int:team_id>/', ChatMessageListView.as_view(), name='chat_message_list'),
    path('chatroom/notifications/', views.NotificationListView.as_view(), name='notification-list'),
    path('chatroom/notifications/<int:notification_id>/', views.NotificationDetailView.as_view(), name='notification-detail'),
    path('chatroom/search/group/<int:team_id>/', search_group_messages, name='search-group-messages'),
    path('chatroom/search/direct/<int:sender_id>/<int:receiver_id>/', search_direct_messages, name='search-direct-messages'),
    path('chatroom/uploadfile/', UploadFileView.as_view()),
    path('chatroom/uploadimage/', UploadImageView.as_view()),
]
