N = int(input())
S = input()
MAX = int("".join(sorted(S, reverse=True)))

goal_hist = [0] * 10
for s in S:
    goal_hist[int(s)] += 1


ans = 0
hist = [0] * 10
for i in range(10**7):
    n = i * i
    if n > MAX:
        continue
    for j in range(10):
        hist[j] = 0

    j = 0
    while j < N or n > 0:
        hist[n % 10] += 1
        j += 1
        n //= 10

    for k in range(10):
        if hist[k] == goal_hist[k]:
            continue
        break
    else:
        # print(i * i)
        ans += 1
print(ans)
