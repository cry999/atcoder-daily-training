from collections import deque

N = int(input())
S = input()
T = input()


def to_int(s: str):
    res = 0
    for c in s:
        res *= 3
        if c == "B":
            res += 1
        elif c == "W":
            res += 2
    return res


def to_str(u: int):
    res = ["."] * (N + 2)
    i = 0
    while u:
        res[i] = ".BW"[u % 3]
        u //= 3
        i += 1
    return "".join(reversed(res))


def move(u: int, i: int):
    if i < 1:
        return u
    a = u // (3 ** (i - 1))
    b = a % 9  # 動かす値
    if b % 3 == 0 or (b // 3) % 3 == 0:
        return u
    v = u - b * (3 ** (i - 1))
    j = 0
    while u:
        if u % 9 == 0:
            break
        u //= 3
        j += 1
    return v + b * (3**j)


s = to_int(S + "..")
t = to_int(T + "..")

dp = [-1] * (3 ** (N + 2))

q = deque()
q.append((s, 0))
dp[s] = 0

while q:
    u, op = q.popleft()
    if u == t:
        break

    for i in range(1, N + 2):
        v = move(u, i)
        if u == v:
            continue
        # print(v, to_str(u), i, to_str(v), 3 ** (N + 2))
        if 0 <= dp[v] <= op + 1:
            continue
        dp[v] = op + 1
        if v == t:
            break
        q.append((v, op + 1))

print(dp[t])
