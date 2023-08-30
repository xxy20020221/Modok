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
    manager_details = serializers.SerializerMethodField(read_only=True)
    members_count = serializers.SerializerMethodField(read_only=True)
    class Meta:
        model = ChatGroup
        fields = ['id', 'team', 'name','manager_details','members_count']
    
    def get_manager_details(self, obj):
        if obj.group_manager:
            return {
                "username": obj.group_manager.username,
                "user_id": obj.group_manager.id
            }
        return None

    def get_members_count(self, obj):
        return obj.members.count()
    


class MentionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Mention
        fields = ['id', 'message', 'mentioned_user', 'read_status']

class EditMessageSerializer(serializers.ModelSerializer):
    class Meta:
        model = EditMessage
        fields = ['id', 'content', 'cursor_position', 'timestamp', 'editor']