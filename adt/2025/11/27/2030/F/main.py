from fractions import Fraction


n = int(input())
score = []
for i in range(n):
    a, b = map(int, input().split())
    score.append((-Fraction(a, a+b), i+1))

score.sort()
print(*map(lambda x: x[1], score))
