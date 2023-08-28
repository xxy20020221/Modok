from django.http import Http404
from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .models import Task, Page, Component
from .serializers import TaskSerializer, PageSerializer, ComponentSerializer

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

class PageList(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, team_id, task_id):
        pages = Page.objects.filter(task_id=task_id)
        serializer = PageSerializer(pages, many=True)
        return Response(serializer.data)

    def post(self, request, team_id, task_id):
        # 将 url中的!!!task_id 添加到传入的数据中
        data = request.data.copy()
        data['task'] = task_id
        serializer = PageSerializer(data=data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class ComponentList(APIView):
    permission_classes = [IsAuthenticated]

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
        try:
            task = Task.objects.get(pk=task_id, team_id=team_id)
        except Task.DoesNotExist:
            print("Task not found")
            raise Http404

        try:
            page = Page.objects.get(pk=page_id, task=task)
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
        data = request.data.copy()
        data['page'] = page_id  # 添加 page_id 到数据中
        serializer = ComponentSerializer(component, data=data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, team_id, task_id, page_id, component_id):
        component = self.get_object(team_id, task_id, page_id, component_id)
        component.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

from rest_framework.exceptions import NotFound

class PageDetail(APIView):
    permission_classes = [IsAuthenticated]

    def get_object(self, team_id, task_id, page_id):
        try:
            task = Task.objects.get(pk=task_id, team_id=team_id)
            page = Page.objects.get(pk=page_id, task=task)
            return page
        except Page.DoesNotExist:
            raise NotFound("Page not found.")

    def put(self, request, team_id, task_id, page_id):
        page = self.get_object(team_id, task_id, page_id)
        data = request.data.copy()
        data['task'] = task_id  # 添加 task_id 到数据中
        serializer = PageSerializer(page, data=data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)