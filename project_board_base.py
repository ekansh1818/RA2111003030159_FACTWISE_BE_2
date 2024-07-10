import json
import os
import uuid
from datetime import datetime
class ProjectBoardBase:
    """
    A project board is a unit of delivery for a project. Each board will have a set of tasks assigned to a user.
    """

    # create a board
    def create_board(self, request: str):
        """
        :param request: A json string with the board details.
        {
            "name" : "<board_name>",
            "description" : "<description>",
            "team_id" : "<team id>"
            "creation_time" : "<date:time when board was created>"
        }
        :return: A json string with the response {"id" : "<board_id>"}

        Constraint:
         * board name must be unique for a team
         * board name can be max 64 characters
         * description can be max 128 characters
        """
        pass

    # close a board
    def close_board(self, request: str) -> str:
        """
        :param request: A json string with the user details
        {
          "id" : "<board_id>"
        }

        :return:

        Constraint:
          * Set the board status to CLOSED and record the end_time date:time
          * You can only close boards with all tasks marked as COMPLETE
        """
        pass

    # add task to board
    def add_task(self, request: str) -> str:
        """
        :param request: A json string with the task details. Task is assigned to a user_id who works on the task
        {
            "title" : "<board_name>",
            "description" : "<description>",
            "user_id" : "<team id>"
            "creation_time" : "<date:time when task was created>"
        }
        :return: A json string with the response {"id" : "<task_id>"}

        Constraint:
         * task title must be unique for a board
         * title name can be max 64 characters
         * description can be max 128 characters

        Constraints:
        * Can only add task to an OPEN board
        """
        pass

    # update the status of a task
    def update_task_status(self, request: str):
        """
        :param request: A json string with the user details
        {
            "id" : "<task_id>",
            "status" : "OPEN | IN_PROGRESS | COMPLETE"
        }
        """
        pass

    # list all open boards for a team
    def list_boards(self, request: str) -> str:
        """
        :param request: A json string with the team identifier
        {
          "id" : "<team_id>"
        }

        :return:
        [
          {
            "id" : "<board_id>",
            "name" : "<board_name>"
          }
        ]
        """
        pass

    def export_board(self, request: str) -> str:
        """
        Export a board in the out folder. The output will be a txt file.
        We want you to be creative. Output a presentable view of the board and its tasks with the available data.
        :param request:
        {
          "id" : "<board_id>"
        }
        :return:
        {
          "out_file" : "<name of the file created>"
        }
        """
        pass
class ProjectBoardManager(ProjectBoardBase):
    def __init__(self, db_path='db/boards.json'):
        self.db_path = db_path
        self._load_boards()

    def _load_boards(self):
        if os.path.exists(self.db_path):
            with open(self.db_path, 'r') as file:
                self.boards = json.load(file)
        else:
            self.boards = {}

    def _save_boards(self):
        with open(self.db_path, 'w') as file:
            json.dump(self.boards, file)

    def create_board(self, request: str) -> str:
        board = json.loads(request)
        board_id = str(uuid.uuid4())
        board['id'] = board_id
        board_name = board['name']
        if any(b['name'] == board_name and b['team_id'] == board['team_id'] for b in self.boards.values()):
            raise Exception("Board name must be unique for a team")
        if len(board_name) > 64:
            raise Exception("Board name can be max 64 characters")
        if len(board.get('description', '')) > 128:
            raise Exception("Description can be max 128 characters")
        board['creation_time'] = datetime.now().isoformat()
        self.boards[board_id] = board
        self._save_boards()
        return json.dumps({"id": board_id})

    def close_board(self, request: str) -> str:
        board_id = json.loads(request)['id']
        board = self.boards.get(board_id)
        if not board:
            raise Exception("Board not found")
        if any(task['status'] != 'COMPLETE' for task in board.get('tasks', [])):
            raise Exception("All tasks must be marked as COMPLETE to close the board")
        board['status'] = 'CLOSED'
        board['end_time'] = datetime.now().isoformat()
        self._save_boards()
        return json.dumps({"status": "success"})

    def add_task(self, request: str) -> str:
        task = json.loads(request)
        board_id = task['board_id']
        board = self.boards.get(board_id)
        if not board:
            raise Exception("Board not found")
        if board.get('status') == 'CLOSED':
            raise Exception("Cannot add task to a CLOSED board")
        task_id = str(uuid.uuid4())
        task['id'] = task_id
        task_title = task['title']
        if any(t['title'] == task_title for t in board.get('tasks', [])):
            raise Exception("Task title must be unique for a board")
        if len(task_title) > 64:
            raise Exception("Task title can be max 64 characters")
        if len(task.get('description', '')) > 128:
            raise Exception("Description can be max 128 characters")
        task['creation_time'] = datetime.now().isoformat()
        if 'tasks' not in board:
            board['tasks'] = []
        board['tasks'].append(task)
        self._save_boards()
        return json.dumps({"id": task_id})

    def update_task_status(self, request: str) -> str:
        data = json.loads(request)
        task_id = data['id']
        status = data['status']
        if status not in ['OPEN', 'IN_PROGRESS', 'COMPLETE']:
            raise Exception("Invalid status")
        for board in self.boards.values():
            for task in board.get('tasks', []):
                if task['id'] == task_id:
                    task['status'] = status
                    self._save_boards()
                    return json.dumps({"status": "success"})
        raise Exception("Task not found")

    def list_boards(self, request: str) -> str:
        team_id = json.loads(request)['id']
        return json.dumps([{
            "id": board_id,
            "name": board['name']
        } for board_id, board in self.boards.items() if board['team_id'] == team_id and board.get('status') != 'CLOSED'])

    def export_board(self, request: str) -> str:
        board_id = json.loads(request)['id']
        board = self.boards.get(board_id)
        if not board:
            raise Exception("Board not found")
        out_file = f"out/board_{board_id}.txt"
        with open(out_file, 'w') as file:
            file.write(f"Board: {board['name']}\n")
            file.write(f"Description: {board['description']}\n")
            file.write(f"Creation Time: {board['creation_time']}\n")
            file.write(f"Team ID: {board['team_id']}\n")
            file.write("\nTasks:\n")
            for task in board.get('tasks', []):
                file.write(f"- {task['title']} ({task['status']})\n")
                file.write(f"  Description: {task['description']}\n")
                file.write(f"  Assigned to: {task['user_id']}\n")
                file.write(f"  Creation Time: {task['creation_time']}\n")
        return json.dumps({"out_file": out_file})