"""
The code smell modules provides the CodeSmell class
and the Location class, which is used by the CodeSmell.
"""
from multiprocessing.dummy import Array
from enum import Enum
from itertools import groupby
import json


class Location:
    """
    The Location class contains the location information of a CodeSmell.
    This includes the module, object, line and column numbers of the code smell
    in the file that the path points to.
    """

    def __init__(self, data):
        self.module = data['module']
        self.python_object = data['obj']
        self.line = data['line']
        self.column = data['column']
        self.end_line = data['endLine']
        self.path = data['path']

    def __repr__(self) -> str:
        return f'in {self.module} on line {self.line} at {self.column}'

    def __str__(self):
        return f'in {self.module} on line {self.line} at {self.column}'


class Priority(Enum):
    """
    The enum that represents the priorities/types of the code smells.
    """
    ERROR = ':red_circle:'
    WARNING = ':orange_circle:'
    REFACTOR = ':yellow_circle:'
    CONVENTION = ':blue_circle:'

    @staticmethod
    def get_priority(name):
        """
        Gets the Priority enum based on the lowercase string.
        :param: name the name of the priority to get
        :return: the corresponding priority
        """
        return {prio.name.lower(): prio for prio in Priority}[name]


class CodeSmell:
    """
    The CodeSmell class contains all the fields of the JSON objects that pylint generates.
    """

    def __init__(self, data):
        self.type = Priority.get_priority(data['type'])
        self.location = Location(data)
        self.symbol = data['symbol']
        self.message = data['message']
        self.message_id = data['message-id']

    def __repr__(self) -> str:
        return f'{self.type.name.lower()} {repr(self.location)} with reason: {self.message}'

    def __str__(self) -> str:
        return f'{self.type.name.lower()} {self.location} with reason: {self.message}'

    def severity(self) -> int:
        """
        Gives the severity depending on the type of the code smell.
        Unknown types are automatically -1 severity.
        From high to low the severities are:
        - Error
        - Warning
        - Refactor
        - Convention
        :return: the severity of the code smell
        """
        types = [Priority.CONVENTION, Priority.REFACTOR, Priority.WARNING, Priority.ERROR]
        return types.index(self.type) if self.type in types else -1

    def get_readable_symbol(self) -> str:
        """
        Gets the symbol as a readable string.
        :return: a readable string
        """
        return self.symbol.replace('-', ' ')

    def jsonify(self) -> str:
        """
        Creates a JSON object containing the CodeSmell.
        :return: a string with the JSON object
        """
        return json.dumps(self,
                          default=lambda o: {
                              **o.__dict__,
                              'severity': self.severity(),
                              'type': self.type.name.lower()
                          })


class Report:
    """
    The Report class contains a list of code smells and a grade.
    """

    def __init__(self, json_content, grade):
        self.code_smells = self.convert_dict(json_content)
        self.grade = grade

    def group_by_file(self):
        """
        Groups the code smells by their file.
        :param: code_smells the CodeSmells objects
        :return: a list with lists of CodeSmells.
        """

        def key_func(k):
            return k.location.path

        return [list(value) for _, value in groupby(self.code_smells, key_func)]

    @staticmethod
    def convert_dict(json_content) -> Array:
        """
        Converts JSON list of code smells to an Array of CodeSmell python objects.
        :param: json_content the content of the json file generated by pylint
        :return: Array of CodeSmells
        """
        ret = []
        for smell in json_content:
            ret.append(CodeSmell(smell))
        return sorted(ret, key=lambda s: s.severity(), reverse=True)
