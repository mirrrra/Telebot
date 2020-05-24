import shelve


def get_data(id: int, type: str):
    data = {}
    with shelve.open('database' + str(id) + '.txt') as db:
        if type == 'plan':
            data = db['plan']
        if type == 'timetable':
            data = db['timetable']
    return data


def add_data(id: int, type: str, action: str):
    with shelve.open('database' + str(id) + '.txt') as db:
        if type == 'plan':
            db['plan'].add(action)
        if type == 'timetable':
            db['timetable'].add(action.split(' '))


def register(id: int):
    with shelve.open('database' + str(id) + '.txt') as db:
        db['plan'] = set()
        db['timetable'] = set()


class Database:
    def __init__(self):
        self.users = []

    def add_user(self, id: int):
        self.users.append(id)
        register(id)

    def get_users(self):
        return self.users




