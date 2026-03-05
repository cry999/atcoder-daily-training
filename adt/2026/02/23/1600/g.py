from collections import deque

N = int(input())
S = input()
T = input()


def s_to_n(s: str) -> int:
    n = 0
    for c in s:
        n *= 3
        if c == ".":
            n += 0
        elif c == "W":
            n += 1
        else:
            n += 2
    return n


def n_to_s(n: int) -> list[str]:
    s = [""] * (N + 2)
    i = N + 1
    while i >= 0:
        if n % 3 == 0:
            s[i] = "."
        elif n % 3 == 1:
            s[i] = "W"
        else:
            s[i] = "B"
        n //= 3
        i -= 1
    return s


def swap(n: int, i: int, j: int) -> int:
    s = n_to_s(n)
    s[i], s[j] = s[j], s[i]
    s[i + 1], s[j + 1] = s[j + 1], s[i + 1]
    return s_to_n("".join(s))


dp = [-1] * (3 ** (N + 2))

start = s_to_n(S + "..")
goal = s_to_n(T + "..")

q = deque([(start, N)])
dp[start] = 0

while q:
    # n: 状態 / k: どこが空いているか
    n, k = q.popleft()

    for i in range(N + 1):
        if k - 1 <= i <= k + 1:
            continue
        m = swap(n, i, k)
        if dp[m] != -1 and dp[n] + 1 >= dp[m]:
            continue
        dp[m] = dp[n] + 1
        if m == goal:
            break
        q.append((m, i))
    else:
        continue
    break

print(dp[goal])
