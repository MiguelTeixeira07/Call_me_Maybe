from colorama import Fore


class ParsingError(Exception):
    """Base exception for all parsing errors.

    Prefixes the message with a red "Parsing Error:" label.

    Args:
        msg: Description of the error.
    """
    def __init__(self, msg: str) -> None:
        """Initializes the exception with a colored error message.

        Args:
            msg: Description of the error.
        """
        super().__init__(Fore.RED + 'Parsing Error: ' + Fore.RESET + msg)


class ArgumentParseError(ParsingError):
    """Raised when the command-line arguments are invalid.

    Args:
        msg: Description of the error.
    """
    def __init__(self, msg: str):
        """Initializes the exception.

        Args:
            msg: Description of the error.
        """
        super().__init__(msg)


class SchemaError(ParsingError):
    """Raised when a JSON file does not match its JSON schema.

    Args:
        msg: Description of the error.
    """
    def __init__(self, msg: str):
        """Initializes the exception.

        Args:
            msg: Description of the error.
        """
        super().__init__(msg)
