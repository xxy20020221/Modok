from rest_framework import serializers
from .models import  Page, Component,Design
from Core.models import Task,User

class DesignSerializer(serializers.ModelSerializer):
    task_id = serializers.IntegerField(write_only=True)
    creater_id = serializers.IntegerField(write_only=True)
    last_editor_id = serializers.IntegerField(write_only=True)
    creater_name = serializers.SerializerMethodField(read_only=True)
    last_editor_name = serializers.SerializerMethodField(read_only=True)
    creater_name = serializers.SerializerMethodField(read_only=True)
    last_editor_name = serializers.SerializerMethodField(read_only=True)
    class Meta:
        model = Design
        fields = '__all__'

    def create(self, validated_data):
        task_id = validated_data.pop('task_id')  # Extract team_id from validated_data
        creater_id = validated_data.pop('creater_id')
        last_editor_id = validated_data.pop('last_editor_id')
        design = Design(**validated_data)
        
        if task_id is not None:
            try:
                task = Task.objects.get(id=task_id)
                creater = User.objects.get(id=creater_id)
                last_editor = User.objects.get(id=last_editor_id)
                design.task = task
                design.creater = creater
                design.last_editor = last_editor
            
            except Task.DoesNotExist:
                pass  # Handle the case when team_id doesn't correspond to a valid Team
        
        design.save()
        return design
    
    def get_creater_name(self,obj):
        return obj.creater.username
    
    def get_last_editor_name(self,obj):
        return obj.last_editor.username
    

class TaskSerializer(serializers.ModelSerializer):
    class Meta:
        model = Task
        fields = '__all__'

class PageSerializer(serializers.ModelSerializer):
    class Meta:
        model = Page
        fields = '__all__'

class ComponentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Component
        fields = '__all__'
