from rest_framework import serializers

from Core.models import TeamMembership
from .models import Team,  ChatGroup, Message, Mention
from .models import Message, DirectMessage,EditMessage

class MessageSerializer(serializers.ModelSerializer):
    class Meta:
        model = Message
        fields = '__all__'

class DirectMessageSerializer(serializers.ModelSerializer):
    class Meta:
        model = DirectMessage
        fields = '__all__'



class TeamSerializer(serializers.ModelSerializer):
    class Meta:
        model = Team
        fields = ['id', 'name', 'created_by', 'created_at']

class UserTeamRoleSerializer(serializers.ModelSerializer):
    class Meta:
        model = TeamMembership
        fields = ['id', 'user', 'team', 'date_joined']

class ChatGroupSerializer(serializers.ModelSerializer):
    class Meta:
        model = ChatGroup
        fields = ['id', 'team', 'name']


class MentionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Mention
        fields = ['id', 'message', 'mentioned_user', 'read_status']

class EditMessageSerializer(serializers.ModelSerializer):
    class Meta:
        model = EditMessage
        fields = ['id', 'content', 'cursor_position', 'timestamp', 'editor']