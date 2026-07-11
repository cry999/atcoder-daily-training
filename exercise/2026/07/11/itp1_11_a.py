class Dice:
    def __init__(self, *numbers: int):
        self.num = list(numbers[:])

    def roll(self, direction: str):
        if direction == "E":
            self.num[0], self.num[2], self.num[5], self.num[3] = (
                self.num[3],
                self.num[0],
                self.num[2],
                self.num[5],
            )
        elif direction == "W":
            self.num[0], self.num[2], self.num[5], self.num[3] = (
                self.num[2],
                self.num[5],
                self.num[3],
                self.num[0],
            )
        elif direction == "S":
            self.num[0], self.num[1], self.num[5], self.num[4] = (
                self.num[4],
                self.num[0],
                self.num[1],
                self.num[5],
            )
        else:
            self.num[0], self.num[1], self.num[5], self.num[4] = (
                self.num[1],
                self.num[5],
                self.num[4],
                self.num[0],
            )

    def top(self):
        return self.num[0]


dice = Dice(*map(int, input().split()))
for d in input():
    dice.roll(d)
print(dice.top())
