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
from django.shortcuts import get_object_or_404
import time
from datetime import datetime
import string
import os
import shutil
from Chatroom.models import ChatGroup,ChatGroupMembership
from InterfaceDesign.models import Design
from .models import User,Task,TeamMembership,Team,Document,Directory
from .serializers import UserSerializer,TeamMembershipSerializer,TeamSerializer,DocumentSerializer,TaskSerializer,AvatarUploadSerializer,DirectorySerializer
from .permissions import IsAdministrater,IsTeamAdministrator,IsTeamCreater,IsTeamMember
from .support import move_files,move_file,move_files_recursively,copy_contents
from Chatroom.serializers import ChatGroupSerializer
from InterfaceDesign.serializers import DesignSerializer

from rest_framework import generics,viewsets,permissions,status
from rest_framework.generics import CreateAPIView
from rest_framework.authtoken.models import Token
from rest_framework.views import APIView
from rest_framework.decorators import action,api_view,permission_classes
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
            else:
                raise PermissionDenied()

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

    def post(self,request):
        avatar = request.FILES.get("avatar") if "avatar" in request.FILES else None
        user = request.user
        user.avatar = avatar
        user.save()
        return Response({"message":"success"}, status=status.HTTP_200_OK)


    def get(self, request):
        """
        获取当前认证用户的详细信息。
        """
        user = request.user
        data = {
            "userid":user.id,
            "username": user.username,
            "email": user.email,
            "phone_number": user.phone_number,
            "gender": user.gender,
            "description": user.description if user.description else "",
            "avatar": user.avatar.url if user.avatar else None,
            "register_date": user.register_date,
        }
        return Response(data, status=status.HTTP_200_OK)

    def patch(self, request):
        """
        更新当前认证用户的详细信息。
        """
        user = request.user
        password = request.data.get('password')
        email = request.data.get("email")
        phone_number = request.data.get("phone_number")
        gender = request.data.get("gender")
        avatar = request.FILES.get("avatar") if "avatar" in request.FILES else None
        description = request.data.get("description")

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
        if description:
            user.description = description

        user.save()
        return Response({"message": "success"}, status=status.HTTP_200_OK)
    
class TeamManagerView(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticated]
    serializer_class = TeamSerializer
    queryset = Team.objects.all()
    def create(self,request):

        serializer = TeamSerializer(data = request.data)
        if serializer.is_valid():
            team=serializer.save()
            team_id = team.id
            TeamMembership.objects.create(user=request.user,team=serializer.instance,role='Creater',permission='rw')
            # Create a ChatGroup for the new Team
            chatgroup_name = serializer.instance.title + " Chat Group"  # You can modify this naming convention
            chatgroup = ChatGroup.objects.create(team=serializer.instance, name=chatgroup_name,group_manager=request.user,is_defalut_chatgroup=True)
            ChatGroupMembership.objects.create(user = request.user, chat_group = chatgroup)
            dir_path = os.path.join(os.path.abspath('.'),'data','documents',str(team_id))
            os.makedirs(dir_path,exist_ok=True)

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
        os.makedirs(dir_path,exist_ok=True)
        os.makedirs(recycle_path,exist_ok=True)
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
            default_chat_group = ChatGroup.objects.get(team=team, is_defalut_chatgroup=True)
            ChatGroupMembership.objects.create(user=user, chat_group=default_chat_group)
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
        print(task_data)
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
            directories = Directory.objects.filter(task_id=task_id)

            for document in documents:
                document_data = DocumentSerializer(document).data
                document_data.pop('id',None)
                dir_path = os.path.join(os.path.abspath('.'),'data','documents',str(team_id),str(task_id2))
                document_path = os.path.join(dir_path,''.join([document_data['document_name'],'.txt']))
                document_data['document_path'] = document_path
                document_data.pop('creater_name',None)
                document_data.pop('last_editor_name',None)
                document_data.pop('created_date',None)
                document_data['creater_id']=document_data['creater']
                document_data['directory_id']=document_data['directory']
                document_data['last_editor_id']=document_data['last_editor']
                document_data['task_id']=task_id2
                print("doc data is ",document_data)
                document2 = DocumentSerializer(data=document_data)
                if document2.is_valid():
                    print("doc data is valid!!!!!!!!!!!!!!!!!!!!")
                    document2.save()
            for directory in directories:
                directory_data = DirectorySerializer(directory).data
                dirid1 = directory_data.pop('id',None)
                dir_path = os.path.join(os.path.abspath('.'),'data','documents',str(team_id),str(task_id2))
                directory_data['dir_path'] = os.path.join(dir_path,directory_data['dir_name'])
                directory_data.pop('documents',None)
                directory_data.pop('created_date',None)
                directory_data['task_id']=task_id2
                directory_data['creater_id']=directory_data['creater']
                directory_data['last_editor_id']=directory_data['last_editor']
                print("dir data is ",directory_data)
                directory2 = DirectorySerializer(data=directory_data)
                if directory2.is_valid():
                    dir2 = directory2.save()
                    dirid2= dir2.id
                    documents2 = Document.objects.filter(task_id=task_id2,directory_id=dirid1)
                    for document in documents2:
                        document_data = DocumentSerializer(document).data
                        document_data.pop('id',None)
                        dir_path = os.path.join(os.path.abspath('.'),'data','documents',str(team_id),str(task_id2),directory_data['dir_name'])
                        document_path = os.path.join(dir_path,''.join([document_data['document_name'],'.txt']))
                        document_data['document_path'] = document_path
                        document_data.pop('creater_name',None)
                        document_data.pop('last_editor_name',None)
                        document_data.pop('created_date',None)
                        document_data['creater_id']=document_data['creater']
                        document_data['directory_id']=dirid2
                        document_data['last_editor_id']=document_data['last_editor']
                        document_data['task_id']=task_id2
                        print("doc data is ",document_data)
                        document2 = DocumentSerializer(data=document_data)
                        if document2.is_valid():
                            # print("doc data is valid!!!!!!!!!!!!!!!!!!!!")
                            document2.save()
                    
            
                    # return Response({"message":"success"}, status=200)
                # raise PermissionDenied()
            
            return Response({"message":"success"}, status=200)
                    # return Response({"message":"success"}, status=200)
                # raise PermissionDenied()
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
        print("serializer error is ",serializer.errors)
        return Response(serializer.errors,status=status.HTTP_400_BAD_REQUEST)

    @extract_team_id_and_check_permission(type_param='Member')
    def list(self,request,team_id=None):
        tasks = Task.objects.filter(team_id=team_id)
        final_data = TaskSerializer(tasks, many=True).data
        print("final_data is ",final_data)
        return Response(final_data, status=200)

    
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
    

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def list_directories_and_documents_for_task(request):
    task_id = request.META.get('HTTP_TASKID')
    # Fetch the task
    try:
        task = Task.objects.get(id=task_id)
    except Task.DoesNotExist:
        return Response({"error": "Task not found"}, status=404)
    
    # Fetch directories for the task
    directories = Directory.objects.filter(task=task)
    directory_serializer = DirectorySerializer(directories, many=True)
    for directory in directory_serializer.data:
        directory['document_count'] = len(directory['documents'])
        directory['is_dir']='1'
    
    # Fetch direct documents for the task (those not in any directory)
    documents = Document.objects.filter(task=task, directory__isnull=True)
    document_serializer = DocumentSerializer(documents, many=True)
    for document in document_serializer.data:
        document['is_dir']='0'

    designs = Design.objects.filter(task=task)
    design_serializer = DesignSerializer(designs, many=True)
    for design in design_serializer.data:
        design['is_dir']='2'

    final_data = directory_serializer.data + document_serializer.data + design_serializer.data
    
    return Response({"files":final_data}, status=200)
    

class DirectoryManage(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticated]
    queryset = Directory.objects.all()
    serializer_class = DirectorySerializer

    @extract_team_id_and_check_permission(type_param='Member')
    def create(self, request, team_id=None):
        task_id = request.META.get('HTTP_TASKID')
        request.data['task_id'] = task_id
        dir_path = os.path.join(os.path.abspath('.'), 'data', 'documents', team_id, task_id, request.data.get('dir_name'))
        request.data['dir_path'] = dir_path
        request.data['creater_id'] = request.user.id
        request.data['last_editor_id'] = request.user.id
        if os.path.exists(dir_path):
            return Response({"message": "directory already exists"}, status=status.HTTP_400_BAD_REQUEST)
        # print(request.data)
        serializer = DirectorySerializer(data=request.data)

        if serializer.is_valid(): 
            serializer.save()
            os.makedirs(dir_path, exist_ok=True)
            return Response({"message": "success"}, status=200)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @extract_team_id_and_check_permission(type_param='Member')
    def list(self, request, team_id=None):
        task_id = request.META.get('HTTP_TASKID')
        directories = Directory.objects.filter(task_id=task_id)
        final_data = DirectorySerializer(directories, many=True).data
        return Response(final_data, status=200)
    
    @extract_team_id_and_check_permission(type_param='Member')
    @action(detail=False, methods=['delete'])
    def delete(self, request, team_id=None):
        task_id = request.META.get('HTTP_TASKID')
        directory_id = request.query_params.get('directory_id')
        directory = Directory.objects.filter(task_id=task_id, id=directory_id).first()
        if not directory:
            return Response({"message": "directory not found"}, status=status.HTTP_400_BAD_REQUEST)
        dir_path = os.path.join(os.path.abspath('.'), 'data', 'documents', team_id, task_id, directory.dir_name)
        recycle_path = os.path.join(os.path.abspath('.'), 'recycle',team_id,directory.dir_name)
        move_files_recursively(dir_path,recycle_path)

        directory.delete()
        return Response({"message": "success"}, status=200)

class DocumentManage(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticated]
    queryset = Document.objects.all()
    serializer_class = DocumentSerializer

    @extract_team_id_and_check_permission(type_param='Member')
    def create(self,request,team_id=None):
        task_id = request.META.get('HTTP_TASKID')
        request.data['task_id']=task_id
        dir_id = None
        if 'HTTP_DIRID' in request.META.keys():
            dir_id = request.META['HTTP_DIRID']
            request.data['directory_id'] = dir_id
            dir_name = Directory.objects.filter(id=dir_id).first().dir_name
            dir_path = os.path.join(os.path.abspath('.'),'data','documents',team_id,task_id,dir_name)
        else:
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
            with open(document_path,'w') as f:
                f.write('{"ops":[{"insert":"Hi!"}]}')
                pass
            return Response({"message":"success"}, status=200)
        return Response(serializer.errors,status=status.HTTP_400_BAD_REQUEST)

    @extract_team_id_and_check_permission(type_param='Member')
    def list(self,request,team_id=None):
        task_id = request.META.get('HTTP_TASKID')
        dir_id = request.META.get('HTTP_DIRID')
        if dir_id:
            documents = Document.objects.filter(task_id=task_id,directory_id = dir_id)
        else:
            documents = Document.objects.filter(task_id=task_id)
        final_data = DocumentSerializer(documents,many=True).data
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
    

@api_view(['GET'])
def list_all_chatrooms(request):
    team_id = request.META.get('HTTP_TEAMID')
    team = Team.objects.filter(id=team_id).first()
    teammember = TeamMembership.objects.filter(user = request.user,team=team)
    if teammember:
        chatgroups = ChatGroup.objects.filter(team_id = team_id)
        return Response([ChatGroupSerializer(chatgroup).data for chatgroup in chatgroups], status=200)
    raise PermissionDenied()

def restore_directory_files(directory,task, root_path, target_dir_path,expiration_date,creater,last_editor):
    """递归地恢复文件夹中的文件，并在数据库中为每一个文件创建/更新记录"""

    for item_name in os.listdir(root_path):
        current_path = os.path.join(root_path, item_name)
        current_target_path = os.path.join(target_dir_path, item_name)

        if os.path.isfile(current_path):
            # 如果是文件，更新或创建Document记录
            document, created = Document.objects.update_or_create(
                task=task,
                document_name=item_name,
                directory=directory,
                expiration_date=expiration_date,
                creater=creater,
                last_editor = last_editor,
                defaults={'document_path': current_target_path}
            )
        

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def restore_from_recycle_bin(request):
    # 获取从POST请求传递的数据
    task_id = request.META.get('HTTP_TASKID')
    team_id = request.META.get('HTTP_TEAMID')
    if TeamMembership.objects.filter(user=request.user,team_id=team_id):
        item_name = request.data.get('item_name')  # 此处为文件或目录名
        expiration_date = request.data.get('expiration_date')
        # 根据task_id查找任务，确保任务存在
        task = get_object_or_404(Task, pk=task_id)

        # 构建原始和目标路径
        recycle_path = os.path.join(os.path.abspath('.'), 'recycle',team_id, item_name)
        target_path = os.path.join(os.path.abspath('.'), 'data', 'documents', str(task.team.id), str(task_id), item_name)

        # 检查条目是否存在于回收站中
        if not os.path.exists(recycle_path):
            return JsonResponse({"message": "Item not found in recycle bin."}, status=404)


        if os.path.isfile(recycle_path):
            target_dir = os.path.dirname(target_path)
            os.makedirs(target_dir, exist_ok=True)

        # 检查是文件还是目录
        if os.path.isfile(recycle_path):
            
            # 更新或创建Document记录
            document, created = Document.objects.update_or_create(
                task=task,
                document_name=item_name,
                expiration_date=expiration_date,
                creater = request.user,
                last_editor = request.user,
                defaults={'document_path': target_path},
            )
            os.rename(recycle_path, target_path)
        elif os.path.isdir(recycle_path):
            # 移动整个目录
            
            directory = Directory.objects.create(task=task, dir_name=item_name,dir_path = target_path,expiration_date=expiration_date,creater=request.user,last_editor=request.user)
            restore_directory_files(directory,task, recycle_path, target_path,expiration_date,request.user,request.user)
            shutil.move(recycle_path, target_path)

        return JsonResponse({"message": "Item successfully restored."}, status=200)
    raise PermissionDenied()


class RecycleBinView(APIView):
    permission_classes=[IsAuthenticated]

    @extract_team_id_and_check_permission(type_param='Member')
    def get(self, request,team_id=None):
        # 设定recycle目录的路径
        recycle_path = os.path.join(os.path.abspath('.'), 'recycle',team_id)

        # 检查目录是否存在
        if not os.path.exists(recycle_path):
            return JsonResponse({"message": "Recycle bin does not exist."}, status=404)

        # 获取目录下所有文件的文件名（排除目录）
        files = []

        # 遍历recycle目录下的内容
        for item in os.listdir(recycle_path):
            item_path = os.path.join(recycle_path, item)
            item_time = datetime.fromtimestamp(os.path.getmtime(item_path)).strftime('%Y-%m-%d %H:%M')
            # 如果是文件，直接添加到filenames列表
            if os.path.isfile(item_path):

                files.append({"file_name":item,"last_modified":item_time,"is_dir":'0'})
            # 如果是目录，添加到directories字典，并列出目录中的文件
            elif os.path.isdir(item_path):
                dir_files = [{"file_name":f,"last_modified":datetime.fromtimestamp(os.path.getmtime(os.path.join(item_path, f))).strftime('%Y-%m-%d %H:%M'),"is_dir":'0'} for f in os.listdir(item_path) if os.path.isfile(os.path.join(item_path, f))]
                files.append({"file_name":item,"last_modified":item_time,"is_dir":'1',"files":dir_files})

        return JsonResponse({"files": files}, status=200)
    
    @extract_team_id_and_check_permission(type_param='Member')
    @action(detail=False, methods=['delete'])
    def delete(self, request,team_id = None):
        # 设定recycle目录的路径
        recycle_path = os.path.join(os.path.abspath('.'), 'recycle',team_id)

        # 检查目录是否存在
        if not os.path.exists(recycle_path):
            return JsonResponse({"message": "Recycle bin does not exist."}, status=404)

        # 删除目录
        shutil.rmtree(recycle_path)

        return JsonResponse({"message": "Recycle bin successfully emptied."}, status=200)

    


    
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def print_data(request):
    document = Document.objects.filter(id = request.data.get('document_id')).first()
    return JsonResponse({"allowed": True,"document_path":document.document_path}, status=200)



    

