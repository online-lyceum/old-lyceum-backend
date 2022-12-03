class DBException(Exception):
    pass


class LessonsNotFound(DBException):
    def __init__(self, subgroup_id: int):
        super().__init__(f'Lessons with {subgroup_id=} was not found')
