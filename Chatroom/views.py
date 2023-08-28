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

def search_group_messages(request, team_id):
    if request.method == 'GET':
        keyword = request.GET.get('keyword', '')

        if not team_id:
            return HttpResponseBadRequest("team_id parameter is required.")

        try:
            chat_group = ChatGroup.objects.get(team_id=team_id)
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
        if 'file' in request.FILES:
            file = request.FILES['file']
            team_id = request.data.get('team_id')
            group_id = ChatGroup.objects.get(team_id=team_id).id
            message = Message(
                sender=request.user,
                file=file,
                group_id=group_id,
                message_type=Message.FILE
            )
            message.save()

            # 获取文件的URL
            file_url = settings.MEDIA_URL + str(message.file)

            return Response({'file_url': file_url}, status=status.HTTP_200_OK)

        return Response({'detail': 'File not provided.'}, status=status.HTTP_400_BAD_REQUEST)


from django.conf import settings

class UploadImageView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        if 'image' in request.FILES:
            image = request.FILES['image']
            team_id = request.data.get('team_id')
            group_id = ChatGroup.objects.get(team_id=team_id).id
            message = Message(
                sender=request.user,
                image=image,
                group_id=group_id,
                message_type=Message.IMAGE
            )
            message.save()

            # 获取图片的URL
            image_url = settings.MEDIA_URL + str(message.image)

            return Response({'message_id': image_url}, status=status.HTTP_200_OK)

        return Response({'detail': 'Image not provided.'}, status=status.HTTP_400_BAD_REQUEST)


# 分页器, 一次加载20条消息
class MessagePagination(PageNumberPagination):

    page_size = 20
    page_query_param = 'page'
    page_size_query_param = 'page_size'
    max_page_size = 1000

# /chat_messages/?team_id=1&page=2
class ChatMessageListView(ListAPIView):
    serializer_class = MessageSerializer
    pagination_class = MessagePagination

    def get_queryset(self):
        permission_classes = [AllowAny]
        team_id = self.kwargs.get('team_id')
        # 提供一个时间范围内的消息筛选功能, 不必须存在
        start_date = self.request.query_params.get('start_date', None)
        end_date = self.request.query_params.get('end_date', None)
        group_id = ChatGroup.objects.get(team_id=team_id).id
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




