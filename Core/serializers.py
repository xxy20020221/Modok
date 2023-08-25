from rest_framework import serializers
from .models import User,Task,TeamMembership,Team
from datetime import datetime
import string
class UserSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)
    def create(self, validated_data):
        password = validated_data.pop('password', '')
        instance = self.Meta.model(**validated_data)
        if password:
            instance.set_password(password)
            print(password)
        instance.save()
        return instance

    class Meta:
        model = User
        fields = '__all__'

class TeamMembershipSerializer(serializers.ModelSerializer):
    username = serializers.SerializerMethodField()
    class Meta:
        model = TeamMembership
        fields = ['user_id','team_id','username']

    def get_username(self,obj):
        return obj.user.username



class TeamSerializer(serializers.ModelSerializer):
    
    class Meta:
        model = Team
        fields = '__all__'



