class DBException(Exception):
    pass


class LessonsNotFound(DBException):
    def __init__(self, class_id: int, subgroup_id: int):
        super().__init__(f'Lessons with {class_id=}, {subgroup_id=} was not found')
