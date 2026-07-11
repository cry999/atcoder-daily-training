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


dice1 = Dice(*map(int, input().split()))
dice2 = Dice(*map(int, input().split()))
if dice1.is_same(dice2):
    print("Yes")
else:
    print("No")
