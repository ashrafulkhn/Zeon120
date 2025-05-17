# Module which contains of all custom exceptions in the application

class ConfigException(Exception):
    def __init__(self, message):
        self.message = message
        super().__init__(self.message)
