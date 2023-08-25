from rest_framework import serializers
from .models import User,Task
from datetime import datetime
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

class AdministratorSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id','username','email','phone_number']

class TaskSerializer(serializers.ModelSerializer):
    administrator = AdministratorSerializer(many=False,read_only=True)
    class Meta:
        model = Task
        fields = '__all__'




