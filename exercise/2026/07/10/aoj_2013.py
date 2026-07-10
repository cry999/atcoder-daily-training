T = 24 * 60 * 60
C = [0] * (T + 1)


def seconds(s: str):
    h = int(s[:2])
    m = int(s[3:5])
    s = int(s[6:8])
    return (h * 60 + m) * 60 + s


while True:
    N = int(input())
    if N == 0:
        break
    for t in range(T + 1):
        C[t] = 0

    for _ in range(N):
        s, t = map(seconds, input().split())
        C[s] += 1
        C[t] -= 1

    ans = 0
    for t in range(T):
        C[t + 1] += C[t]
        ans = max(ans, C[t])
    print(ans)
