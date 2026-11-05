from .imports import Fore


class ParsingError(Exception):
    def __init__(self, msg) -> None:
        super().__init__(Fore.RED + 'Parsing Error: ' + Fore.RESET + msg)


class ArgumentParseError(ParsingError):
    def __init__(self, msg):
        super().__init__(msg)
