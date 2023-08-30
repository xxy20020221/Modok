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
from .serializers import UserSerializer,TeamMembershipSerializer,TeamSerializer,DocumentSerializer,TaskSerializer,AvatarUploadSerializer
from .permissions import IsAdministrater,IsTeamAdministrator,IsTeamCreater,IsTeamMember
from .support import move_files,move_file,move_files_recursively,copy_contents
from Chatroom.serializers import ChatGroupSerializer

from rest_framework import generics,viewsets,permissions,status
from rest_framework.generics import CreateAPIView
from rest_framework.authtoken.models import Token
from rest_framework.views import APIView
from rest_framework.decorators import action,api_view
from rest_framework.response import Response
from rest_framework.exceptions import NotAuthenticated,AuthenticationFailed,PermissionDenied
from rest_framework.permissions import AllowAny,IsAuthenticated
from rest_framework.parsers import MultiPartParser, FormParser, JSONParser

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
        
class AvatarUploadView(APIView):
    parser_classes = (MultiPartParser,)
    permission_classes = [IsAuthenticated]
    def post(self, request, *args, **kwargs):
        serializer = AvatarUploadSerializer(data=request.data)

        if serializer.is_valid():
            user = request.user
            user.avatar = serializer.validated_data['avatar']
            user.save()
            return Response({"message": "Avatar uploaded successfully"}, status=status.HTTP_200_OK)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        
class UserDetailView(APIView):
    permission_classes = [IsAuthenticated]
    parser_classes = [MultiPartParser, FormParser, JSONParser]

    def get(self, request):
        """
        获取当前认证用户的详细信息。
        """
        user = request.user
        data = {
            "username": user.username,
            "email": user.email,
            "phone_number": user.phone_number,
            "gender": user.gender,
            "avatar": user.avatar.url if user.avatar else None
        }
        return Response(data, status=status.HTTP_200_OK)

    def put(self, request):
        """
        更新当前认证用户的详细信息。
        """
        user = request.user
        password = request.data.get('password')
        email = request.data.get("email")
        phone_number = request.data.get("phone_number")
        gender = request.data.get("gender")
        avatar = request.FILES.get("avatar") if "avatar" in request.FILES else None

        if password:
            user.set_password(password)
        if email:
            user.email = email
        if phone_number:
            user.phone_number = phone_number
        if gender:
            user.gender = gender
        if avatar:
            user.avatar = avatar

        user.save()
        return Response({"message": "success"}, status=status.HTTP_200_OK)
    
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
    
    @action(detail=False, methods=['delete'])
    def delete(self,request):
        team_id = request.query_params.get('team_id')
        team = Team.objects.filter(id=team_id).first()
        userid = request.user.id
        team_member = TeamMembership.objects.filter(user_id = userid,team_id=team_id).first()
        if not team_member:
            raise PermissionDenied()
        if team_member.role != 'Creater':
            raise PermissionDenied()

        #删除团队
        team.delete()
        dir_path = os.path.join(os.path.abspath('.'),'data','documents',team_id)
        recycle_path = os.path.join(os.path.abspath('.'),'recycle',team_id)
        move_files_recursively(dir_path,recycle_path)
        #改，缺少原型设计的储存路径
        return Response({"message":"success"}, status=200)

        



    

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
class DuplicateTask(APIView):
    permission_classes = [IsAuthenticated]

    @extract_team_id_and_check_permission(type_param='Member')
    def post(self,request,team_id=None):
        team_id = request.META.get('HTTP_TEAMID')
        task_id = request.data.get('task_id')
        task = Task.objects.filter(team_id=team_id,id=task_id).first()
        task_data = TaskSerializer(task).data
        task_data['title'] = task_data['title'] + "_副本"
        task_data.pop('id',None)
        task_data.pop('created_date',None)
        task_data.pop('task_permission',None)
        task_data['team_id']=team_id
        serializer = TaskSerializer(data=task_data)
        
        if serializer.is_valid():
            #创建新task
            tmp = serializer.save()
            task_id2 = tmp.id
            #复制文件
            dir_path = os.path.join(os.path.abspath('.'),'data','documents',str(team_id),str(task_id))
            dest_path = os.path.join(os.path.abspath('.'),'data','documents',str(team_id),str(serializer.data.get('id')))
            copy_contents(dir_path,dest_path)
            #复制到数据库
            documents = Document.objects.filter(task_id=task_id)
            for document in documents:
                document_data = DocumentSerializer(document).data
                document_data.pop('id',None)
                dir_path = os.path.join(os.path.abspath('.'),'data','documents',team_id,task_id2)
                document_path = os.path.join(dir_path,''.join([document_data['document_name'],'.txt']))
                document_data['document_path'] = document_path
                document2 = DocumentSerializer(data=document_data)
                if document2.is_valid():
                    document2.save()
                    return Response({"message":"success"}, status=200)
                raise PermissionDenied()
        raise PermissionDenied()






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
            task_id = serializer.data.get('id')
            dir_path = os.path.join(os.path.abspath('.'),'data','documents',team_id,str(task_id))
            os.makedirs(dir_path,exist_ok=True)
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
        request.data['task_id']=task_id
        dir_path = os.path.join(os.path.abspath('.'),'data','documents',team_id,task_id)
        document_path = os.path.join(dir_path,''.join([request.data.get('document_name'),'.txt']))
        request.data['document_path']=document_path
        request.data['creater_id'] = request.user.id
        request.data['last_editor_id'] = request.user.id
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
        final_data = DocumentSerializer(documents,many=True).data
        for x in final_data:
            x['creater_username']=User.objects.filter(id=x['creater']).first().username
            x['last_editor_username']=User.objects.filter(id=x['last_editor']).first().username
        return Response(final_data,status=200)
    
    #缺少正在编辑时的项目保护，即有人编辑时应该无法删除
    @extract_team_id_and_check_permission(type_param='Member')
    @action(detail=False, methods=['delete'])
    def delete(self,request,team_id=None):
        task_id = request.META.get('HTTP_TASKID')
        document_id = request.query_params.get('document_id')
        documents = Document.objects.filter(task_id=task_id,id=document_id).first()
        if not documents:
            return Response({"message":"document not found"}, status=status.HTTP_400_BAD_REQUEST)
        document_name = documents.document_name
        #移入垃圾桶
        dir_path = os.path.join(os.path.abspath('.'),'data','documents',team_id,task_id)
        document_path = os.path.join(dir_path,''.join([document_name,'.txt']))
        recycle_path = os.path.join(os.path.abspath('.'),'recycle',team_id)
        os.makedirs(recycle_path,exist_ok=True)
        move_file(document_path,recycle_path)

        documents.delete()
        return Response({"message":"success"}, status=200)
    
    @extract_team_id_and_check_permission(type_param='Member')
    def partial_update(self,request,pk=None,team_id=None):
        task_id = request.META.get('HTTP_TASKID')
        request.data['task_id']=task_id
        documents = Document.objects.filter(task_id=task_id,id=pk).first()
        
        document_original_name = documents.document_name
        
        if 'document_name' in request.data.keys():
            if request.data['document_name'] != document_original_name:
                dir_path = os.path.join(os.path.abspath('.'),'data','documents',team_id,task_id)
                document_original_path = os.path.join(dir_path,''.join([document_original_name,'.txt']))
                print("!!!!!!!!",request.data['document_name'])
                document_path = os.path.join(dir_path,''.join([request.data['document_name'],'.txt']))
                os.rename(document_original_path,document_path)
        
        return super().partial_update(request,pk)
    

@extract_team_id_and_check_permission(type_param='Member')
@api_view(['GET'])
def list_all_chatrooms(request,team_id=None):
    chatgroups = ChatGroup.objects.filter(team_id = team_id)
    return Response([ChatGroupSerializer(chatgroup).data for chatgroup in chatgroups], status=200)
    


    

