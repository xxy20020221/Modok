from rest_framework import permissions
from .models import TeamMembership
class IsAdministrater(permissions.BasePermission):
    def has_permission(self, request, view):
        return bool(request.user and request.user.is_staff)
    
def IsTeamAdministrator(request):
    userid = request.user.id
    team_id = request.data.get('team_id')
    team_member = TeamMembership.objects.filter(user_id = userid,team_id=team_id).first()
    if not team_member:
        return False
    role = team_member.role
    return role=='Creater' or role=='Administrator'

def IsTeamCreater(request):
    userid = request.user.id
    team_id = request.data.get('team_id')
    team_member = TeamMembership.objects.filter(user_id = userid,team_id=team_id).first()
    if not team_member:
        return False
    role = team_member.role
    return role=='Creater'

def IsTeamMember(request):
    userid = request.user.id
    team_id = request.data.get('team_id')
    team_member = TeamMembership.objects.filter(user_id = userid,team_id=team_id).first()
    if not team_member:
        return False
    
    role = team_member.role
    return role=='Creater' or role=='Administrator' or role=='Viewer'



