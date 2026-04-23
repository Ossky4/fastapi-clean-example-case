from enum import Enum
from pathlib import Path
import enum
import sys


SRC_PATH = Path(__file__).resolve().parents[1] / "src"
if str(SRC_PATH) not in sys.path:
    sys.path.insert(0, str(SRC_PATH))

if not hasattr(enum, "StrEnum"):
    class StrEnum(str, Enum):
        pass

    enum.StrEnum = StrEnum
