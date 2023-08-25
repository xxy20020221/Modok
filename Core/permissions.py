from rest_framework import permissions
from .models import TeamMembership


class IsAdministrater(permissions.BasePermission):
    def has_permission(self, request, view):
        return bool(request.user and request.user.is_staff)


class IsTeamAdministrator(permissions.BasePermission):
    def has_permission(self, request, view):
        userid = request.user.id
        role = TeamMembership.objects.get(user_id=userid).role
        return role == 'Creater' or role == 'Administrator'


class IsTeamCreater(permissions.BasePermission):
    def has_permission(self, request, view):
        userid = request.user.id
        role = TeamMembership.objects.get(user_id=userid).role
        return role == 'Creater'
