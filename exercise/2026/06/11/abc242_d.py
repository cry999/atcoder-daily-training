S = input()

ORD_A = ord("A")


def f(t: int, k: int):
    if t == 0:
        return ord(S[k]) - ORD_A

    if k == 0:
        n = (ord(S[0]) - ORD_A + t) % 3
        return n

    if k % 2 == 0:
        return (f(t - 1, k // 2) + 1) % 3
    return (f(t - 1, k // 2) + 2) % 3


Q = int(input())
for _ in range(Q):
    t, k = map(int, input().split())
    k -= 1  # 0-indexed

    print(chr(f(t, k) + ORD_A))
