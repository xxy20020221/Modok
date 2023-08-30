from rest_framework import serializers
from .models import User,Task,TeamMembership,Team,Document,Directory
from datetime import datetime
import string
import os 
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

class ShortUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['username','first_name','last_name','email']

class TeamMembershipSerializer(serializers.ModelSerializer):
    username = serializers.SerializerMethodField()
    user_info = ShortUserSerializer(source='user',read_only=True)
    role = serializers.CharField(read_only=True)


    class Meta:
        model = TeamMembership
        fields = ['user_id','team_id','user_info','username','role']

    def get_username(self,obj):
        return obj.user.username

class AvatarUploadSerializer(serializers.Serializer):
    avatar = serializers.ImageField()

class TeamSerializer(serializers.ModelSerializer):
    
    class Meta:
        model = Team
        fields = '__all__'

class ShortTeamSerializer(serializers.ModelSerializer):
    team_id = serializers.IntegerField()
    class Meta:
        model = Team
        fields = ['team_id']

class TaskSerializer(serializers.ModelSerializer):
    # team = ShortTeamSerializer(read_only=True)
    team_id = serializers.IntegerField(write_only=True)
    class Meta:
        model = Task
        fields = ['team_id','task_permission','title','description','expiration_date','created_date','id']

    def create(self, validated_data):
        team_id = validated_data.pop('team_id')  # Extract team_id from validated_data
        task = Task(**validated_data)
        
        if team_id is not None:
            try:
                team = Team.objects.get(id=team_id)
                task.team = team
            except Team.DoesNotExist:
                pass  # Handle the case when team_id doesn't correspond to a valid Team
        
        task.save()
        return task



class DocumentSerializer(serializers.ModelSerializer):

    task_id = serializers.IntegerField(write_only=True)
    creater_id = serializers.IntegerField(write_only=True)
    last_editor_id = serializers.IntegerField(write_only=True)
    creater_name = serializers.SerializerMethodField(read_only=True)
    last_editor_name = serializers.SerializerMethodField(read_only=True)
    directory_id = serializers.IntegerField(write_only=True,required=False)
    class Meta:
        model = Document
        fields = '__all__'
       

    def create(self, validated_data):
        task_id = validated_data.pop('task_id')  # Extract team_id from validated_data
        creater_id = validated_data.pop('creater_id')
        last_editor_id = validated_data.pop('last_editor_id')
        directory_id = validated_data.pop('directory_id',None)
        document = Document(**validated_data)
        
        if task_id is not None:
            try:
                task = Task.objects.get(id=task_id)
                creater = User.objects.get(id=creater_id)
                last_editor = User.objects.get(id=last_editor_id)
                document.task = task
                document.creater = creater
                document.last_editor = last_editor
                if directory_id:
                    document.directory = Directory.objects.get(id=directory_id)
            
            except Task.DoesNotExist:
                pass  # Handle the case when team_id doesn't correspond to a valid Team
        
        document.save()
        return document
    
    def get_creater_name(self,obj):
        return obj.creater.username
    
    def get_last_editor_name(self,obj):
        return obj.last_editor.username
    
    # def update(self, instance, validated_data):
    #     # 在局部更新时，只更新传递的字段
    #     task_id = validated_data.get('task_id')
    #     # creater_id = validated_data.get('creater_id')
    #     if task_id is not None:
    #         instance.task_id = task_id
    #     instance.save()
    #     instance = super.update()
    #     return instance


class DirectorySerializer(serializers.ModelSerializer):
    documents = DocumentSerializer(many=True, read_only=True)
    task_id = serializers.IntegerField(write_only=True)
    creater_id = serializers.IntegerField(write_only=True)
    last_editor_id = serializers.IntegerField(write_only=True)
    creater_name = serializers.SerializerMethodField(read_only=True)
    last_editor_name = serializers.SerializerMethodField(read_only=True)

    def create(self, validated_data):
        task_id = validated_data.pop('task_id')  # Extract team_id from validated_data
        creater_id = validated_data.pop('creater_id')
        last_editor_id = validated_data.pop('last_editor_id')
        directory = Directory(**validated_data)
        
        if task_id is not None:
            
            try:
                
                task = Task.objects.get(id=task_id)
                creater = User.objects.get(id=creater_id)
                last_editor = User.objects.get(id=last_editor_id)
                directory.task = task
                directory.creater = creater
                directory.last_editor = last_editor
            
            except Task.DoesNotExist:
                pass  # Handle the case when team_id doesn't correspond to a valid Team

        directory.save()
        return directory

    class Meta:
        model = Directory
        fields = '__all__'
        extra_kwargs = {
            'task': {'required': False}
        }

    def get_creater_name(self,obj):
        return obj.creater.username
    
    def get_last_editor_name(self,obj):
        return obj.last_editor.username


