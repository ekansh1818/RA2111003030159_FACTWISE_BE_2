import json
import os
import uuid
from datetime import datetime
class UserBase:
    """
    Base interface implementation for API's to manage users.
    """

    # create a user
    def create_user(self, request: str) -> str:
        """
        :param request: A json string with the user details
        {
          "name" : "<user_name>",
          "display_name" : "<display name>"
        }
        :return: A json string with the response {"id" : "<user_id>"}

        Constraint:
            * user name must be unique
            * name can be max 64 characters
            * display name can be max 64 characters
        """
        pass

    # list all users
    def list_users(self) -> str:
        """
        :return: A json list with the response
        [
          {
            "name" : "<user_name>",
            "display_name" : "<display name>",
            "creation_time" : "<some date:time format>"
          }
        ]
        """
        pass

    # describe user
    def describe_user(self, request: str) -> str:
        """
        :param request: A json string with the user details
        {
          "id" : "<user_id>"
        }

        :return: A json string with the response

        {
          "name" : "<user_name>",
          "description" : "<some description>",
          "creation_time" : "<some date:time format>"
        }

        """
        pass

    # update user
    def update_user(self, request: str) -> str:
        """
        :param request: A json string with the user details
        {
          "id" : "<user_id>",
          "user" : {
            "name" : "<user_name>",
            "display_name" : "<display name>"
          }
        }

        :return:

        Constraint:
            * user name cannot be updated
            * name can be max 64 characters
            * display name can be max 128 characters
        """
        pass

    def get_user_teams(self, request: str) -> str:
        """
        :param request:
        {
          "id" : "<user_id>"
        }

        :return: A json list with the response.
        [
          {
            "name" : "<team_name>",
            "description" : "<some description>",
            "creation_time" : "<some date:time format>"
          }
        ]
        """
        pass

class UserManager(UserBase):
    def __innit__(self,db_path='db/users.json'):
        self.db_path=db_path
        self.load_users()
    def _load_users(self):
        if os.path.exists(self.db_path):
            with open(self.db_path,'r') as file:
                self.users=json.load(file)
        else:
            self.users={}
    def _save_users(self):
        with open(self.db_path,'w') as file:
            json.dump(self.users,file)
    def create_user(self, request: str) -> str:
        user=json.loads(request)
        user_id=str(uuid.uuid4())
        user['id']=user_id
        user_name=user['name']
        if any(u['name']==user_name for u in self.users.values()):
            raise Exception("User name must be unique")
        if len(user_name)>64:
            raise Exception("User name can be max 64 characters")
        if len(user.get('display_name',''))>64:
            raise Exception("Display name can be max 64 characters")
        user['creation_time']=datetime.now().isoformat()
        self.users[user_id]=user
        self._save_users()
        return json.dumps({"id":user_id})
    def list_users(self) -> str:
        return json.dumps([{
            "name":user['name'],
            "display_name":user['display_name'],
            "creation_time":user['creation_time']
        } for user in self.users.values()])
    def describe_user(self, request: str) -> str:
        user_id=json.loads(request)['id']
        user=self.users.get(user_id)
        if not user:
            raise Exception("User not found")
        return json.dumps({
            "name":user['name'],
            "display_name":user['display_name'],
            "creation_time":user['creation_time']
        })
    def update_user(self, request: str) -> str:
        data=json.loads(request)
        user_id=data['id']
        user=self.users.get(user_id)
        if not user:
            raise Exception("User not found")
        if 'name' in data['user'] and data['user']['name'] != user['name']:
            raise Exception("User name cannot be updated")
        if len(data['user'].get('name',''))>64:
            raise Exception("User name can be max 64 characters")
        if len(data['user'].get('display_name',''))>128:
            raise Exception("Display name can be max 128 characters")
        self.users[user_id].update(data['user'])
        self._save_users
        return json.dumps({"status":"success"})
    def get_user_teams(self, request: str) -> str:
        user_id=json.loads(request)['id']
        return json.dumps([])
