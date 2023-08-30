from django.contrib.auth.decorators import login_required
from rest_framework.authentication import TokenAuthentication
from rest_framework.pagination import PageNumberPagination
from rest_framework.generics import ListAPIView
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework import status
from .models import Message, ChatGroup, DirectMessage
from .serializers import MessageSerializer
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from django.views import View
from rest_framework.decorators import action, authentication_classes
from .models import Notification
from django.http import JsonResponse, HttpResponseBadRequest
from .models import Message, DirectMessage, ChatGroup
from .serializers import MessageSerializer, DirectMessageSerializer
from django.db.models import Q
from Core.models import User

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.shortcuts import get_object_or_404
from Core.models import Team
class CreateChatGroupView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            return Response({"detail": "Authentication required."}, status=status.HTTP_401_UNAUTHORIZED)

        team = get_object_or_404(Team, id=request.data.get("team_id"))

        # Check if the user is a member of the team
        if request.user not in team.users.all():  # Assuming Team model has a ManyToMany relationship with User called 'members'
            return Response({"detail": "User is not a member of this team."}, status=status.HTTP_403_FORBIDDEN)

        # Check if a chat group with the same name already exists in the team
        chat_group_name = request.data.get("name")
        if ChatGroup.objects.filter(team=team, name=chat_group_name).exists():
            return Response({"detail": "A chat group with this name already exists in the team."},
                            status=status.HTTP_400_BAD_REQUEST)

        chat_group = ChatGroup.objects.create(
            name=chat_group_name,
            group_manager=request.user,
            team=team,
            is_defalut_chatgroup=False
        )
        chat_group.members.add(request.user)
        return Response({"detail": "Chat group created."}, status=status.HTTP_201_CREATED)


class InviteToChatGroupView(APIView):
    permission_classes = [IsAuthenticated]
    def post(self, request, *args, **kwargs):
        chat_group = get_object_or_404(ChatGroup, id=kwargs.get("chat_group_id"))

        if chat_group.is_defalut_chatgroup:
            return Response({"detail": "Default chat groups cannot invite new members."}, status=status.HTTP_403_FORBIDDEN)

        if chat_group.group_manager != request.user:
            return Response({"detail": "Only the group manager can invite users."}, status=status.HTTP_403_FORBIDDEN)

        user_to_invite = get_object_or_404(User, id=request.data.get("user_id"))
        chat_group.members.add(user_to_invite)
        return Response({"detail": "User invited."}, status=status.HTTP_200_OK)

class DisbandChatGroupView(APIView):
    permission_classes = [IsAuthenticated]
    def post(self, request, *args, **kwargs):
        chat_group = get_object_or_404(ChatGroup, id=kwargs.get("chat_group_id"))

        if chat_group.is_defalut_chatgroup:
            return Response({"detail": "Default chat groups cannot be disbanded."}, status=status.HTTP_403_FORBIDDEN)

        if chat_group.group_manager != request.user:
            return Response({"detail": "Only the group manager can disband the chat group."}, status=status.HTTP_403_FORBIDDEN)

        chat_group.is_disbanded = True
        chat_group.save()
        return Response({"detail": "Chat group disbanded."}, status=status.HTTP_200_OK)

class LeaveChatGroupView(APIView):
    permission_classes = [IsAuthenticated]
    def post(self, request, *args, **kwargs):
        chat_group = get_object_or_404(ChatGroup, id=kwargs.get("chat_group_id"))

        if chat_group.is_defalut_chatgroup:
            return Response({"detail": "Cannot leave default chat groups."}, status=status.HTTP_403_FORBIDDEN)

        if request.user not in chat_group.members.all():
            return Response({"detail": "User is not a member of this chat group."}, status=status.HTTP_400_BAD_REQUEST)
        if chat_group.is_disbanded == True:
            return Response({"detail": "Chat group has been disbanded."}, status=status.HTTP_400_BAD_REQUEST)
        if request.user == chat_group.group_manager:
            return Response({"detail": "Group manager cannot leave group."}, status=status.HTTP_400_BAD_REQUEST)
        chat_group.members.remove(request.user)
        return Response({"detail": "Successfully left the chat group."}, status=status.HTTP_200_OK)

def search_group_messages(request, group_id):
    if request.method == 'GET':
        keyword = request.GET.get('keyword', '')

        if not group_id:
            return HttpResponseBadRequest("team_id parameter is required.")
        if not keyword:
            chat_group = ChatGroup.objects.get(pk=group_id)
            messages = Message.objects.filter(group=chat_group)
            data = [message_to_dict(message) for message in messages]
            return JsonResponse(data, safe=False)
        try:
            chat_group = ChatGroup.objects.get(pk=group_id)
            messages = Message.objects.filter(group=chat_group, content__icontains=keyword)
            data = [message_to_dict(message) for message in messages]
            return JsonResponse(data, safe=False)

        except ChatGroup.DoesNotExist:
            return JsonResponse({"error": "ChatGroup not found."}, status=404)

    return JsonResponse({'detail': 'Invalid request method.'}, status=400)

def search_direct_messages(request, sender_id, receiver_id):
    if request.method == 'GET':
        keyword = request.GET.get('keyword', '')

        if not sender_id or not receiver_id:
            return HttpResponseBadRequest("Both sender_id and receiver_id parameters are required.")
        if not keyword:
            messages = DirectMessage.objects.filter(
                Q(sender_id=sender_id, receiver_id=receiver_id) |
                Q(sender_id=receiver_id, receiver_id=sender_id),
            )

            data = [message_to_dict(message) for message in messages]
            return JsonResponse(data, safe=False)

        messages = DirectMessage.objects.filter(
            Q(sender_id=sender_id, receiver_id=receiver_id) |
            Q(sender_id=receiver_id, receiver_id=sender_id),
            content__icontains=keyword
        )

        data = [message_to_dict(message) for message in messages]
        return JsonResponse(data, safe=False)

    return JsonResponse({'detail': 'Invalid request method.'}, status=400)

def message_to_dict(message):
    return {
        "message_type": message.message_type,
        "content": message.content,
        "username": message.sender.username,
        "user_id": message.sender.id,
        "time": message.timestamp.strftime('%Y-%m-%d %H:%M:%S')
    }


class UploadFileView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        if 'file' not in request.FILES:
            return Response({'detail': 'File not provided.'}, status=status.HTTP_400_BAD_REQUEST)

        file = request.FILES['file']
        group_id = request.data.get('group_id', None)
        receiver_id = request.data.get('receiver_id', None)

        if group_id:  # Save to Message table
            # group_id = ChatGroup.objects.get(team_id=team_id).id
            message = Message(
                sender=request.user,
                file=file,
                group_id=group_id,
                message_type=Message.FILE
            )
            message.save()
            message.content = str(message.file)  # 使用保存后的对象的file字段来更新content字段
            message.save(update_fields=['content'])  # 只更新content字段
            file_url = settings.MEDIA_URL + str(message.file)
            return Response({'file_url': file_url}, status=status.HTTP_200_OK)

        elif receiver_id:  # Save to DirectMessage table
            receiver = User.objects.get(pk=receiver_id)
            direct_message = DirectMessage(
                sender=request.user,
                receiver=receiver,
                file=file,
                message_type=DirectMessage.FILE
            )
            direct_message.save()
            direct_message.content = str(direct_message.file)  # 使用保存后的对象的file字段来更新content字段
            direct_message.save(update_fields=['content'])  # 只更新content字段
            file_url = settings.MEDIA_URL + str(direct_message.file)
            return Response({'file_url': file_url}, status=status.HTTP_200_OK)

        return Response({'detail': 'Both team_id and receiver_id are missing.'}, status=status.HTTP_400_BAD_REQUEST)



from django.conf import settings


class UploadImageView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        if 'image' not in request.FILES:
            return Response({'detail': 'Image not provided.'}, status=status.HTTP_400_BAD_REQUEST)

        image = request.FILES['image']
        # !
        group_id = request.data.get('group_id', None)
        receiver_id = request.data.get('receiver_id', None)

        if group_id:  # Save to Message table
            # group_id = ChatGroup.objects.get(team_id=team_id).id
            message = Message(
                sender=request.user,
                image=image,
                group_id=group_id,
                message_type=Message.IMAGE
            )
            message.save()
            message.content = str(message.image)  # 使用保存后的对象的image字段来更新content字段
            message.save(update_fields=['content'])  # 只更新content字段
            image_url = settings.MEDIA_URL + str(message.image)
            return Response({'image_url': image_url}, status=status.HTTP_200_OK)

        elif receiver_id:  # Save to DirectMessage table
            receiver = User.objects.get(pk=receiver_id)
            direct_message = DirectMessage(
                sender=request.user,
                receiver=receiver,
                image=image,
                message_type=DirectMessage.IMAGE
            )
            direct_message.save()
            direct_message.content = str(direct_message.image)  # 使用保存后的对象的image字段来更新content字段
            direct_message.save(update_fields=['content'])  # 只更新content字段
            image_url = settings.MEDIA_URL + str(direct_message.image)
            return Response({'image_url': image_url}, status=status.HTTP_200_OK)


# 分页器, 一次加载20条消息
class MessagePagination(PageNumberPagination):

    page_size = 20
    page_query_param = 'page'
    page_size_query_param = 'page_size'
    max_page_size = 1000

# /chat_messages/?group_id=1&page=2
class ChatMessageListView(ListAPIView):
    serializer_class = MessageSerializer
    pagination_class = MessagePagination

    def get_queryset(self):
        permission_classes = [AllowAny]
        group_id = self.kwargs.get('group_id')
        # 提供一个时间范围内的消息筛选功能, 不必须存在
        start_date = self.request.query_params.get('start_date', None)
        end_date = self.request.query_params.get('end_date', None)
        # group_id = ChatGroup.objects.get(pk=group_id).id
        queryset = Message.objects.filter(group_id=group_id).order_by('timestamp')

        if start_date:
            queryset = queryset.filter(created_at__gte=start_date)
        if end_date:
            queryset = queryset.filter(created_at__lte=end_date)

        return queryset

# 只有@才有
class NotificationListView(View):
    @method_decorator(csrf_exempt)
    def dispatch(self, *args, **kwargs):
        return super().dispatch(*args, **kwargs)

    def get(self, request):
        permission_classes = [AllowAny]
        user_id = request.user.id
        notifications = Notification.objects.filter(user_id=user_id).values()
        return JsonResponse(list(notifications), safe=False)

class NotificationDetailView(View):
    @method_decorator(csrf_exempt)
    def dispatch(self, *args, **kwargs):
        return super().dispatch(*args, **kwargs)

    @action(detail=False, methods = ['post'])
    def put(self, request, notification_id):
        permission_classes = [AllowAny]
        try:
            notification = Notification.objects.get(pk=notification_id, user_id=request.user.id)
            notification.is_read = True
            notification.save()
            return JsonResponse({'status': 'success', 'message': 'Notification marked as read.'})
        except Notification.DoesNotExist:
            return JsonResponse({'status': 'error', 'message': 'Notification not found.'}, status=404)

    @action(detail=False, methods=['delete'])
    def delete(self, request, notification_id):
        permission_classes = [AllowAny]
        try:
            notification = Notification.objects.get(pk=notification_id, user_id=request.user.id)
            notification.delete()
            return JsonResponse({'status': 'success', 'message': 'Notification deleted.'})
        except Notification.DoesNotExist:
            return JsonResponse({'status': 'error', 'message': 'Notification not found.'}, status=404)
        
    




