import json
import os
import uuid
from datetime import datetime
class TeamBase:
    """
    Base interface implementation for API's to manage teams.
    For simplicity a single team manages a single project. And there is a separate team per project.
    Users can be
    """

    # create a team
    def create_team(self, request: str) -> str:
        """
        :param request: A json string with the team details
        {
          "name" : "<team_name>",
          "description" : "<some description>",
          "admin": "<id of a user>"
        }
        :return: A json string with the response {"id" : "<team_id>"}

        Constraint:
            * Team name must be unique
            * Name can be max 64 characters
            * Description can be max 128 characters
        """
        pass

    # list all teams
    def list_teams(self) -> str:
        """
        :return: A json list with the response.
        [
          {
            "name" : "<team_name>",
            "description" : "<some description>",
            "creation_time" : "<some date:time format>",
            "admin": "<id of a user>"
          }
        ]
        """
        pass

    # describe team
    def describe_team(self, request: str) -> str:
        """
        :param request: A json string with the team details
        {
          "id" : "<team_id>"
        }

        :return: A json string with the response

        {
          "name" : "<team_name>",
          "description" : "<some description>",
          "creation_time" : "<some date:time format>",
          "admin": "<id of a user>"
        }

        """
        pass

    # update team
    def update_team(self, request: str) -> str:
        """
        :param request: A json string with the team details
        {
          "id" : "<team_id>",
          "team" : {
            "name" : "<team_name>",
            "description" : "<team_description>",
            "admin": "<id of a user>"
          }
        }

        :return:

        Constraint:
            * Team name must be unique
            * Name can be max 64 characters
            * Description can be max 128 characters
        """
        pass

    # add users to team
    def add_users_to_team(self, request: str):
        """
        :param request: A json string with the team details
        {
          "id" : "<team_id>",
          "users" : ["user_id 1", "user_id2"]
        }

        :return:

        Constraint:
        * Cap the max users that can be added to 50
        """
        pass

    # add users to team
    def remove_users_from_team(self, request: str):
        """
        :param request: A json string with the team details
        {
          "id" : "<team_id>",
          "users" : ["user_id 1", "user_id2"]
        }

        :return:

        Constraint:
        * Cap the max users that can be added to 50
        """
        pass

    # list users of a team
    def list_team_users(self, request: str):
        """
        :param request: A json string with the team identifier
        {
          "id" : "<team_id>"
        }

        :return:
        [
          {
            "id" : "<user_id>",
            "name" : "<user_name>",
            "display_name" : "<display name>"
          }
        ]
        """
        pass
class TeamManager(TeamBase):
    def __init__(self, db_path='db/teams.json'):
        self.db_path = db_path
        self._load_teams()

    def _load_teams(self):
        if os.path.exists(self.db_path):
            with open(self.db_path, 'r') as file:
                self.teams = json.load(file)
        else:
            self.teams = {}

    def _save_teams(self):
        with open(self.db_path, 'w') as file:
            json.dump(self.teams, file)

    def create_team(self, request: str) -> str:
        team = json.loads(request)
        team_id = str(uuid.uuid4())
        team['id'] = team_id
        team_name = team['name']
        if any(t['name'] == team_name for t in self.teams.values()):
            raise Exception("Team name must be unique")
        if len(team_name) > 64:
            raise Exception("Team name can be max 64 characters")
        if len(team.get('description', '')) > 128:
            raise Exception("Description can be max 128 characters")
        team['creation_time'] = datetime.now().isoformat()
        self.teams[team_id] = team
        self._save_teams()
        return json.dumps({"id": team_id})

    def list_teams(self) -> str:
        return json.dumps([{
            "name": team['name'],
            "description": team['description'],
            "creation_time": team['creation_time'],
            "admin": team['admin']
        } for team in self.teams.values()])

    def describe_team(self, request: str) -> str:
        team_id = json.loads(request)['id']
        team = self.teams.get(team_id)
        if not team:
            raise Exception("Team not found")
        return json.dumps({
            "name": team['name'],
            "description": team['description'],
            "creation_time": team['creation_time'],
            "admin": team['admin']
        })

    def update_team(self, request: str) -> str:
        data = json.loads(request)
        team_id = data['id']
        team = self.teams.get(team_id)
        if not team:
            raise Exception("Team not found")
        if 'name' in data['team'] and data['team']['name'] != team['name']:
            raise Exception("Team name must be unique")
        if len(data['team'].get('name', '')) > 64:
            raise Exception("Team name can be max 64 characters")
        if len(data['team'].get('description', '')) > 128:
            raise Exception("Description can be max 128 characters")
        self.teams[team_id].update(data['team'])
        self._save_teams()
        return json.dumps({"status": "success"})

    def add_users_to_team(self, request: str) -> str:
        data = json.loads(request)
        team_id = data['id']
        team = self.teams.get(team_id)
        if not team:
            raise Exception("Team not found")
        if 'users' not in team:
            team['users'] = []
        new_users = data['users']
        if len(team['users']) + len(new_users) > 50:
            raise Exception("Cannot add more than 50 users to a team")
        team['users'].extend(new_users)
        self._save_teams()
        return json.dumps({"status": "success"})

    def remove_users_from_team(self, request: str) -> str:
        data = json.loads(request)
        team_id = data['id']
        team = self.teams.get(team_id)
        if not team:
            raise Exception("Team not found")
        users_to_remove = data['users']
        team['users'] = [u for u in team['users'] if u not in users_to_remove]
        self._save_teams()
        return json.dumps({"status": "success"})

    def list_team_users(self, request: str) -> str:
        team_id = json.loads(request)['id']
        team = self.teams.get(team_id)
        if not team:
            raise Exception("Team not found")
        users = team.get('users', [])
        return json.dumps(users)