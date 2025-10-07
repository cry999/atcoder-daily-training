N = int(input())

numbers = {}
for a in map(int, input().split()):
    numbers[a] = numbers.get(a, 0) + 1

ans = 0
for v in numbers.values():
    if v < 3:
        continue
    ans += v * (v - 1) * (v - 2) // 6

print(ans)
