from enum import Enum


class ShipConditionEventComponent(str, Enum):
    ENGINE = "ENGINE"
    FRAME = "FRAME"
    REACTOR = "REACTOR"

    def __str__(self) -> str:
        return str(self.value)
