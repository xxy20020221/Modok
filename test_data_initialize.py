import requests

base_url = "http://127.0.0.1:8000/api/"

# Register users
users_to_register = [
    {"username": "peter", "password": "1111"},
    {"username": "charlie", "password": "1111"},
    {"username": "tom", "password": "1111"},
]

for user_data in users_to_register:
    response = requests.post(base_url + "register/", json=user_data)
    print("Register Response:", response.json())

# Login
login_data = {"username": "peter", "password": "1111"}
login_response = requests.post(base_url + "login/", json=login_data)
token = login_response.json().get("token")
headers = {"Authorization": f"Token {token}"}

# Create a team
team_data = {"title": "modok", "description": "testTeam"}
team_response = requests.post(base_url + "teammanage/", json=team_data, headers=headers)
print("Create Team Response:", team_response.json())

headers['teamid']='1'
# Invite users to the team
invitations = [
    {"username": "charlie"},
    {"username": "tom"},
]

for invite_data in invitations:
    invite_response = requests.post(base_url + "teaminvite/", json=invite_data, headers=headers)
    print("Team Invite Response:", invite_response.json())

# Grant user privileges
grant_data = {"username": "charlie", "team_id": "1", "type": "Administrator"}
grant_response = requests.post(base_url + "grant/", json=grant_data, headers=headers)
print("Grant Response:", grant_response.json())

# Get team invitations
get_invite_response = requests.get(base_url + "teaminvite/", headers=headers)
print("Get Team Invitations Response:", get_invite_response.json())

# Create tasks
tasks_to_create = [
    {"title": "task1", "description": "test description", "expiration_date": "2024-02-21"},
    {"title": "task2", "description": "test description2", "expiration_date": "2024-02-21"},
]

for task_data in tasks_to_create:
    task_response = requests.post(base_url + "taskmanage/", json=task_data, headers=headers)
    print("Create Task Response:", task_response.json())

# Get tasks
get_tasks_response = requests.get(base_url + "taskmanage/", headers=headers)
print("Get Tasks Response:", get_tasks_response.json())

headers['taskid']='1'
# Create documents
documents_to_create = [
    {"document_name": "document1", "priority": "1", "expiration_date": "2024-02-21"},
]

for document_data in documents_to_create:
    document_response = requests.post(base_url + "documentmanage/", json=document_data, headers=headers)
    print("Create Document Response:", document_response.json())
