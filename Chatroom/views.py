from rest_framework.pagination import PageNumberPagination
from rest_framework.generics import ListAPIView
from .models import Message, ChatGroup, DirectMessage
from .serializers import MessageSerializer
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from django.views import View
from rest_framework.decorators import action
from .models import Notification
from django.http import JsonResponse, HttpResponseBadRequest
from .models import Message, DirectMessage, ChatGroup
from .serializers import MessageSerializer, DirectMessageSerializer
from django.db.models import Q

def search_group_messages(request):
    if request.method == 'GET':
        team_id = request.GET.get('team_id')
        keyword = request.GET.get('keyword', '')

        if not team_id:
            return HttpResponseBadRequest("team_id parameter is required.")

        try:
            chat_group = ChatGroup.objects.get(team_id=team_id)
            messages = Message.objects.filter(group=chat_group, content__icontains=keyword)

            # 使用序列化器序列化消息列表
            serializer = MessageSerializer(messages, many=True)
            return JsonResponse(serializer.data, safe=False)

        except ChatGroup.DoesNotExist:
            return JsonResponse({"error": "ChatGroup not found."}, status=404)

    return JsonResponse({'detail': 'Invalid request method.'}, status=400)

def search_direct_messages(request):
    if request.method == 'GET':
        sender_id = request.GET.get('sender_id')
        receiver_id = request.GET.get('receiver_id')
        keyword = request.GET.get('keyword', '')

        if not sender_id or not receiver_id:
            return HttpResponseBadRequest("Both sender_id and receiver_id parameters are required.")

        messages = DirectMessage.objects.filter(
            Q(sender_id=sender_id, receiver_id=receiver_id) |
            Q(sender_id=receiver_id, receiver_id=sender_id),
            content__icontains=keyword
        )

        # 使用序列化器序列化消息列表
        serializer = DirectMessageSerializer(messages, many=True)
        return JsonResponse(serializer.data, safe=False)

    return JsonResponse({'detail': 'Invalid request method.'}, status=400)



def upload_file(request):
    if request.method == "POST" and request.FILES['file']:
        file = request.FILES['file']
        message = Message(
            sender=request.user,
            file=file,
            team_id=request.POST['team_id'],
            message_type=Message.FILE
        )
        message.save()
        return JsonResponse({'file_id': message.id})

def upload_image(request):
    if request.method == "POST" and request.FILES['image']:
        image = request.FILES['image']
        message = Message(
            sender=request.user,
            image=image,
            team_id=request.POST['team_id'],
            message_type=Message.IMAGE
        )
        message.save()
        return JsonResponse({'image_id': message.id})

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
        team_id = self.kwargs.get('team_id')
        # 提供一个时间范围内的消息筛选功能, 不必须存在
        start_date = self.request.query_params.get('start_date', None)
        end_date = self.request.query_params.get('end_date', None)

        queryset = Message.objects.filter(team_id=team_id).order_by('-created_at')

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
        user_id = request.user.id
        notifications = Notification.objects.filter(user_id=user_id).values()
        return JsonResponse(list(notifications), safe=False)

class NotificationDetailView(View):
    @method_decorator(csrf_exempt)
    def dispatch(self, *args, **kwargs):
        return super().dispatch(*args, **kwargs)

    @action(detail=False, methods = ['post'])
    def put(self, request, notification_id):

        try:
            notification = Notification.objects.get(pk=notification_id, user_id=request.user.id)
            notification.is_read = True
            notification.save()
            return JsonResponse({'status': 'success', 'message': 'Notification marked as read.'})
        except Notification.DoesNotExist:
            return JsonResponse({'status': 'error', 'message': 'Notification not found.'}, status=404)

    @action(detail=False, methods=['delete'])
    def delete(self, request, notification_id):
        try:
            notification = Notification.objects.get(pk=notification_id, user_id=request.user.id)
            notification.delete()
            return JsonResponse({'status': 'success', 'message': 'Notification deleted.'})
        except Notification.DoesNotExist:
            return JsonResponse({'status': 'error', 'message': 'Notification not found.'}, status=404)




