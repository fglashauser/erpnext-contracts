from enum import Enum

class BaseEnum(Enum):
    @classmethod
    def from_str(cls, text: str) -> "BaseEnum":
        """Returns the enumeration value for the given text.
        """
        for term in cls:
            if term.value == text:
                return term
        return None