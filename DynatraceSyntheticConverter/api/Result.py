from dataclasses import dataclass
from typing import Any


@dataclass
class Result:
    """Basic implementation of  'Go-like' error handling"""

    @dataclass
    class Error:
        msg: str

    data: Any
    error: Error
