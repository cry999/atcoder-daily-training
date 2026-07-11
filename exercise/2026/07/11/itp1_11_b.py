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

    def turn(self):
        self.num[1], self.num[2], self.num[4], self.num[3] = (
            self.num[2],
            self.num[4],
            self.num[3],
            self.num[1],
        )

    def top(self):
        return self.num[0]

    def front(self):
        return self.num[1]

    def right(self):
        return self.num[2]


dice = Dice(*map(int, input().split()))

Q = int(input())
for _ in range(Q):
    top, front = map(int, input().split())
    for _ in range(4):
        if dice.top() == top:
            break
        dice.roll("N")
    for _ in range(3):
        if dice.top() == top:
            break
        dice.roll("E")
    for _ in range(4):
        if dice.front() == front:
            break
        dice.turn()
    print(dice.right())
