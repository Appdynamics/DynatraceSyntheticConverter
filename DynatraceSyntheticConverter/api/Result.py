from dataclasses import dataclass
from typing import Generic, TypeVar, Optional

T = TypeVar('T')


@dataclass
class Result(Generic[T]):
    """Basic implementation of 'Go-like' error handling"""

    @dataclass
    class Error:
        msg: str

    data: T
    error: Optional[Error]
