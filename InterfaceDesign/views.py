from django.http import Http404
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import generics,viewsets,permissions,status

from .models import Task, Page, Component,Design
from .serializers import TaskSerializer, PageSerializer, ComponentSerializer,DesignSerializer
from django.shortcuts import get_object_or_404
from rest_framework.decorators import action,api_view,permission_classes
from Core.views import extract_team_id_and_check_permission

class DesignManage(viewsets.ModelViewSet):
    permission_classes = [AllowAny]
    queryset = Design.objects.all()
    serializer_class = DesignSerializer

    @extract_team_id_and_check_permission(type_param='Member')
    def create(self,request,team_id=None):
        task_id = request.META.get('HTTP_TASKID')
        request.data['task_id']=task_id
        request.data['creater_id']=request.user.id
        request.data['last_editor_id']=request.user.id
        dir_id = None
        serializer = DesignSerializer(data=request.data)
        if serializer.is_valid(): 
            serializer.save()
            return Response({"message":"success"}, status=200)
        return Response(serializer.errors,status=status.HTTP_400_BAD_REQUEST)

    @extract_team_id_and_check_permission(type_param='Member')
    def list(self,request,team_id=None):
        task_id = request.META.get('HTTP_TASKID')
        designs = Design.objects.filter(task_id=task_id)
        final_data = DesignSerializer(designs,many=True).data
        return Response(final_data,status=200)
    
    @extract_team_id_and_check_permission(type_param='Member')
    @action(detail=False, methods=['delete'])
    def delete(self,request,team_id=None):
        task_id = request.META.get('HTTP_TASKID')
        design_id = request.query_params.get('design_id')
        designs = Design.objects.filter(id=design_id).first()
        if not designs:
            return Response({"message":"design not found"}, status=status.HTTP_400_BAD_REQUEST)
        designs.delete()
        return Response({"message":"success"}, status=200)
    


class GetTaskSharedStatus(APIView):
    permission_classes = [IsAuthenticated]
    # 外部的参数不必改, 这样方便一点
    def get(self, request, task_id):
        design = get_object_or_404(Design, id=task_id)
        team = design.task.team

        if request.user not in team.users.all():
            return Response({"detail": "Not authorized to view this task."}, status=status.HTTP_403_FORBIDDEN)

        return Response({"is_shared": design.is_shared}, status=status.HTTP_200_OK)
class SetTaskShared(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, task_id):
        design = get_object_or_404(Design, id=task_id)
        team = design.task.team

        if request.user not in team.users.all():
            return Response({"detail": "Not authorized to modify this task."}, status=status.HTTP_403_FORBIDDEN)

        design.is_shared = True
        design.save()
        return Response({"detail": "Task is now shared."}, status=status.HTTP_200_OK)

class SetTaskPrivate(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, task_id):
        design = get_object_or_404(Design, id=task_id)
        team = design.task.team

        if request.user not in team.users.all():
            return Response({"detail": "Not authorized to modify this task."}, status=status.HTTP_403_FORBIDDEN)

        design.is_shared = False
        design.save()
        return Response({"detail": "Task is now private."}, status=status.HTTP_200_OK)

class TaskList(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, team_id):
        tasks = Task.objects.filter(team_id=team_id)
        serializer = TaskSerializer(tasks, many=True)
        return Response(serializer.data)

    def post(self, request, team_id):
        serializer = TaskSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save(team_id=team_id)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
class TaskDetail(APIView):
    permission_classes = [IsAuthenticated]

    def get_object(self, team_id, task_id):
        try:
            return Task.objects.get(pk=task_id, team_id=team_id)
        except Task.DoesNotExist:
            raise NotFound("Task not found.")

    def get(self, request, team_id, task_id):
        task = self.get_object(team_id, task_id)
        serializer = TaskSerializer(task)
        return Response(serializer.data)

    def put(self, request, team_id, task_id):
        task = self.get_object(team_id, task_id)
        serializer = TaskSerializer(task, data=request.data, partial=True)
        for field_name in serializer.fields:
            serializer.fields[field_name].required = False
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, team_id, task_id):
        task = self.get_object(team_id, task_id)
        task.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

class PageList(APIView):

    def get_permissions(self):
        design = get_object_or_404(Design, id=self.kwargs['task_id'])
        if design.is_shared:
            return []
        return [IsAuthenticated()]

    def get(self, request, team_id, task_id):
        pages = Page.objects.filter(design_id=task_id).order_by("last_modified")
        serializer = PageSerializer(pages, many=True)
        return Response(serializer.data)

    def post(self, request, team_id, task_id):
        # 将 url中的!!!task_id 添加到传入的数据中
        data = request.data.copy()
        data['design'] = task_id
        serializer = PageSerializer(data=data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
class PageDetail(APIView):

    def get_permissions(self):
        design = get_object_or_404(Design, id=self.kwargs['task_id'])
        if design.is_shared:
            return []
        return [IsAuthenticated()]

    def get_object(self, team_id, task_id, page_id):
        try:
            # design = Design.objects.get(pk=task_id)
            return Page.objects.get(pk=page_id)
        except Page.DoesNotExist:
            raise NotFound("Page not found.")

    def put(self, request, team_id, task_id, page_id):
        page = self.get_object(team_id, task_id, page_id)
        data = request.data.copy()
        data['design'] = task_id  # 添加 task_id 到数据中
        serializer = PageSerializer(page, data=data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, team_id, task_id, page_id):
        page = self.get_object(team_id, task_id, page_id)
        page.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

class ComponentList(APIView):


    def get_permissions(self):
        design = get_object_or_404(Design, id=self.kwargs['task_id'])
        if design.is_shared:
            return []
        return [IsAuthenticated()]

    def get(self, request, team_id, task_id, page_id):
        components = Component.objects.filter(page_id=page_id)
        serializer = ComponentSerializer(components, many=True)
        return Response(serializer.data)

    def post(self, request, team_id, task_id, page_id):
        data = request.data.copy()
        data['page'] = page_id
        serializer = ComponentSerializer(data=data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class ComponentDetail(APIView):
    permission_classes = [IsAuthenticated]

    def get_object(self, team_id, task_id, page_id, component_id):
        # try:
        #     task = Task.objects.get(pk=task_id, team_id=team_id)
        # except Task.DoesNotExist:
        #     print("Task not found")
        #     raise Http404

        try:
            page = Page.objects.get(pk=page_id)
        except Page.DoesNotExist:
            print("Page not found")
            raise Http404

        try:
            component = Component.objects.get(pk=component_id, page=page)
            return component
        except Component.DoesNotExist:
            print("Component not found")
            raise Http404

    def put(self, request, team_id, task_id, page_id, component_id):
        component = self.get_object(team_id, task_id, page_id, component_id)

        # 动态地设置序列化器字段为非必需
        serializer = ComponentSerializer(component, data=request.data, partial=True)
        for field_name in serializer.fields:
            serializer.fields[field_name].required = False

        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, team_id, task_id, page_id, component_id):
        component = self.get_object(team_id, task_id, page_id, component_id)
        component.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

from rest_framework.exceptions import NotFound


