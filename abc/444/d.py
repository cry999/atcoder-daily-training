N = int(input())
(*A,) = map(int, input().split())

M = max(A)
digit = [0] * (M + 10)

for a in A:
    digit[0] += 1
    digit[a] -= 1

for i in range(M):
    digit[i + 1] += digit[i]

for i in range(M + 9):
    if digit[i] >= 10:
        digit[i + 1] += digit[i] // 10
        digit[i] %= 10

digit.reverse()
i = 0
while i < len(digit) and digit[i] == 0:
    i += 1

s = "".join(map(str, digit[i:]))
print(s)
