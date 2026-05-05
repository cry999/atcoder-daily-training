N = int(input())
S = input()

counter = [0] * (2 * N + 1)
cur = N
counter[cur] += 1

current_sum = 0
ans = 0

for s in S:
    if s == "A":
        current_sum += counter[cur]
        cur += 1
    elif s == "B":
        cur -= 1
        current_sum -= counter[cur]

    counter[cur] += 1

    ans += current_sum

print(ans)
