from django.shortcuts import render
from django.http import HttpResponse,JsonResponse
from django.shortcuts import render, redirect
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.decorators import login_required
from django.views import View
from django.views.generic import ListView, DetailView, View
from django.utils.decorators import method_decorator
from django.utils.timezone import make_aware
from django_filters.rest_framework import DjangoFilterBackend
from django.db.models import F,Q,Subquery,OuterRef
import string
import os

from Chatroom.models import ChatGroup
from .models import User,Task,TeamMembership,Team,Document
from .serializers import UserSerializer,TeamMembershipSerializer,TeamSerializer,DocumentSerializer,TaskSerializer
from .permissions import IsAdministrater,IsTeamAdministrator,IsTeamCreater,IsTeamMember
from .support import move_files,move_file

from rest_framework import generics,viewsets,permissions,status
from rest_framework.generics import CreateAPIView
from rest_framework.authtoken.models import Token
from rest_framework.views import APIView
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.exceptions import NotAuthenticated,AuthenticationFailed,PermissionDenied
from rest_framework.permissions import AllowAny,IsAuthenticated

def extract_team_id_and_check_permission(type_param):
    def decorator(view_func):
        def _wrapped_view(view, request, *args, **kwargs):
            team_id = request.META.get('HTTP_TEAMID')
            if not team_id:
                return Response({"message":"team_id not found"}, status=status.HTTP_400_BAD_REQUEST)
            kwargs['team_id'] = team_id
            userid = request.user.id
            team_member = TeamMembership.objects.filter(user_id = userid,team_id=team_id).first()
            if not team_member:
                raise PermissionDenied()
            role = team_member.role
            if type_param == 'Administrator':
                allowed_roles = ['Creater','Administrator']
            elif type_param == 'Creater':
                allowed_roles = ['Creater']
            elif type_param == 'Member':
                allowed_roles = ['Creater','Administrator','Viewer']
            if role in allowed_roles:
                return view_func(view, request, *args, **kwargs)
        return _wrapped_view
    return decorator

# Create your views here.
class UserRegisterView(APIView):
    permission_classes = [AllowAny]
    def post(self, request):
        serializer = UserSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            if user:
                token = Token.objects.create(user=user)
                json=serializer.data
                json['token'] = token.key
                
                return Response(json, status=status.HTTP_201_CREATED)
        return Response(serializer.errors,status=status.HTTP_400_BAD_REQUEST)
    
class UserLoginView(APIView):
    permission_classes = [AllowAny]
    def post(self, request):
        username = request.data.get('username')
        password = request.data.get('password')
        user = authenticate(username=username,password=password)
        
        if user:
            token,created = Token.objects.get_or_create(user=user)
            # login(request, user)
            return Response({'token': token.key}, status=200)
        else:
            raise AuthenticationFailed("wrong username or password")
    
class UserLogoutView(APIView):
    def post(self, request):
        if request.user.is_authenticated:
            request.user.auth_token.delete()
            logout(request)
            return Response({'User logged out successfully'},status=200)
        else:
            raise NotAuthenticated("You are not logged in")
        
class UserChangeView(APIView):
    permission_classes = [IsAuthenticated]
    def post(self, request):
        password = request.data.get('password')
        email=request.data.get("email")
        phone_number = request.data.get("phone_number")
        user=request.user
        if(password!=None):
            user.set_password(password)
        if(email!=None):
            user.email=email
        if(phone_number!=None):
            user.phone_number=phone_number
        user.save()
        return Response({"message":"success"}, status=200)
    
class TeamManagerView(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticated]
    serializer_class = TeamSerializer
    queryset = Team.objects.all()
    def create(self,request):

        serializer = TeamSerializer(data = request.data)
        if serializer.is_valid():
            serializer.save()
            TeamMembership.objects.create(user=request.user,team=serializer.instance,role='Creater',permission='rw')
            # Create a ChatGroup for the new Team
            chatgroup_name = serializer.instance.title + " Chat Group"  # You can modify this naming convention
            ChatGroup.objects.create(team=serializer.instance, name=chatgroup_name)

            return Response({"message":"success"}, status=200)
        return Response(serializer.errors,status=status.HTTP_400_BAD_REQUEST)
    
    def list(self,request):
        user_teams = Team.objects.filter(users=request.user)
        return Response(TeamSerializer(user_teams,many=True).data,status=200)
        



    

class InviteView(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticated]
    queryset = TeamMembership.objects.all()
    serializer_class = TeamMembershipSerializer

    @extract_team_id_and_check_permission(type_param='Administrator')
    def create(self,request,team_id=None):
        try:
            user = User.objects.get(username=request.data.get('username'))
            team = Team.objects.get(id=team_id)
        except:
            return Response({"message":"user or team not found"}, status=status.HTTP_400_BAD_REQUEST)

        
        if TeamMembership.objects.filter(user=user,team=team).exists():
            return Response({"message":"user already exists"}, status=status.HTTP_400_BAD_REQUEST)
        else:
            temp = TeamMembership.objects.create(user=user,team=team,role='Viewer',permission='r')
            print(TeamMembershipSerializer(temp).data)
            return Response(TeamMembershipSerializer(temp).data, status=200)

    
    #找所有team_id对应的成员
    @extract_team_id_and_check_permission(type_param='Member')
    def list(self,request,team_id=None):
        teammembers = TeamMembership.objects.filter(team_id=team_id)
        return Response(TeamMembershipSerializer(teammembers, many=True).data, status=200)
            
    

    @extract_team_id_and_check_permission(type_param='Administrator')
    @action(detail=False, methods=['delete'])
    def delete(self,request,team_id=None):
        user_id = request.query_params.get('user_id')
        username = request.query_params.get('username')
        user = User.objects.filter(Q(id=user_id) | Q(username=username)).first()
        teamMembership = TeamMembership.objects.filter(user=user,team_id=team_id).first()
        if not teamMembership:
            return Response({"message":"user or team not found"}, status=status.HTTP_400_BAD_REQUEST)

        if teamMembership.role == "Viewer":
            teamMembership.delete()
            return Response({"message":"success"}, status=200)
        else:
            return Response({"message":"cannot delete creater or administrator"}, status=status.HTTP_400_BAD_REQUEST)

        
        
    
# 只有创建者和管理员可以授予权限  改
class GrantAccess(APIView):     
    permission_classes = [IsAuthenticated]
    @extract_team_id_and_check_permission(type_param='Administrator')
    def post(self, request,team_id=None):

        type = request.data.get('type')
        if(type=='Creater'):
            return Response({"message":"cannot grant creater access"} , status=status.HTTP_400_BAD_REQUEST)
        user_id = request.data.get('id')
        team = Team.objects.get(id=team_id)
        username = request.data.get('username')
        user = User.objects.filter(Q(id=user_id) | Q(username=username)).first()
        TeamMembership.objects.filter(user=user,team=team).update(role=type)
        return Response({"message":"success"}, status=200)


#只有创建者可以撤销权限

class RevokeAccess(APIView):     
    permission_classes = [IsAuthenticated]
    @extract_team_id_and_check_permission(type_param='Creater')
    def post(self, request,team_id=None):

        type = request.data.get('type')
        user_id = request.data.get('id')
        team = Team.objects.get(id=team_id)
        username = request.data.get('username')
        user = User.objects.filter(Q(id=user_id) | Q(username=username)).first()
        TeamMembership.objects.filter(user=user,team=team).update(role=type)
        return Response({"message":"success"}, status=200)

    
# class TaskManagerView(viewsets.ModelViewSet):


class TaskManage(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticated]
    queryset = Task.objects.all()
    serializer_class = TaskSerializer

    @extract_team_id_and_check_permission(type_param='Member')
    def create(self,request,team_id=None):

        request.data['team_id']=team_id
        serializer = TaskSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response({"message":"success"}, status=200)
        return Response(serializer.errors,status=status.HTTP_400_BAD_REQUEST)

    
    #缺少正在编辑时的项目保护，即有人编辑时应该无法删除
    @extract_team_id_and_check_permission(type_param='Member')
    @action(detail=False, methods=['delete'])
    def delete(self,request,team_id=None):
            task_id = request.query_params.get('task_id')
            tasks = Task.objects.filter(team_id=team_id,id=task_id).first()
            if not tasks:
                return Response({"message":"task not found"}, status=status.HTTP_400_BAD_REQUEST)
            #移入垃圾桶
            dir_path = os.path.join(os.path.abspath('.'),'data','documents',team_id,task_id)
            recycle_path = os.path.join(os.path.abspath('.'),'recycle',team_id)
            os.makedirs(recycle_path,exist_ok=True)
            move_files(dir_path,recycle_path)

            tasks.delete()
            return Response({"message":"success"}, status=200)
    

    
    

class DocumentManage(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticated]
    queryset = Document.objects.all()
    serializer_class = DocumentSerializer

    @extract_team_id_and_check_permission(type_param='Member')
    def create(self,request,team_id=None):
        task_id = request.META.get('HTTP_TASKID')
        dir_path = os.path.join(os.path.abspath('.'),'data','documents',team_id,task_id)
        document_path = os.path.join(dir_path,''.join([request.data.get('document_name'),'.txt']))
        request.data['document_path']=document_path
        request.data['creater_id'] = request.user.id
        if(os.path.exists(document_path)):
                return Response({"message":"document already exists"}, status=status.HTTP_400_BAD_REQUEST)
        serializer = DocumentSerializer(data=request.data)
        if serializer.is_valid(): 
            serializer.save()
            os.makedirs(dir_path,exist_ok=True)
            with open(document_path,'w'):
                pass
            return Response({"message":"success"}, status=200)
        return Response(serializer.errors,status=status.HTTP_400_BAD_REQUEST)

    @extract_team_id_and_check_permission(type_param='Member')
    def list(self,request,team_id=None):
        task_id = request.META.get('HTTP_TASKID')
        documents = Document.objects.filter(task_id=task_id)
        return Response(DocumentSerializer(documents,many=True).data,status=200)
    
    #缺少正在编辑时的项目保护，即有人编辑时应该无法删除
    @extract_team_id_and_check_permission(type_param='Member')
    @action(detail=False, methods=['delete'])
    def delete(self,request,team_id=None):
        task_id = request.META.get('HTTP_TASKID')
        document_id = request.query_params.get('document_id')
        documents = Document.objects.filter(task_id=task_id,id=document_id).first()
        if not documents:
            return Response({"message":"document not found"}, status=status.HTTP_400_BAD_REQUEST)
        #移入垃圾桶
        dir_path = os.path.join(os.path.abspath('.'),'data','documents',team_id,task_id)
        document_path = os.path.join(dir_path,''.join([request.data.get('document_name'),'.txt']))
        recycle_path = os.path.join(os.path.abspath('.'),'recycle',team_id)
        os.makedirs(recycle_path,exist_ok=True)
        move_file(document_path,recycle_path)

        documents.delete()
        return Response({"message":"success"}, status=200)
    


    

