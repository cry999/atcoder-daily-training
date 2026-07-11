class Dice:
    def __init__(self, *numbers: int):
        self.num = list(numbers[:])

    def roll(self, direction: str):
        rotate = {
            "N": (1, 5, 2, 3, 0, 4),
            "S": (4, 0, 2, 3, 5, 1),
            "E": (3, 1, 0, 5, 4, 2),
            "W": (2, 1, 5, 0, 4, 3),
        }
        self.num = [self.num[i] for i in rotate[direction]]

    def turn(self):
        self.num[1], self.num[2], self.num[4], self.num[3] = (
            self.num[2],
            self.num[4],
            self.num[3],
            self.num[1],
        )

    def copy(self):
        return Dice(*self.num)

    def is_same(self, other: "Dice") -> bool:
        dice = other.copy()

        for direction in "NNNNEEEE":
            for _ in range(4):
                if self.num == dice.num:
                    return True
                dice.turn()
            dice.roll(direction)

        return False


N = int(input())
dices = [Dice(*map(int, input().split())) for _ in range(N)]


def any_same(dices: list[Dice]):
    N = len(dices)
    for i in range(N):
        di = dices[i]
        for j in range(i + 1, N):
            dj = dices[j]
            if di.is_same(dj):
                return True
    return False


if any_same(dices):
    print("No")
else:
    print("Yes")
