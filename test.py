import enum
class State(enum.Enum):
    WAIT_SCAN = 0
    ING_SCAN = 1
    FINISH_SCAN = 2

print(State.WAIT_SCAN.value)