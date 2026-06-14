from math import gcd

N, A, B = map(int, input().split())


def s(n: int):
    return n * (n + 1) // 2


L = A * B // gcd(A, B)

print(s(N) - A * s(N // A) - B * s(N // B) + L * s(N // L))
# print(f"[DEBUG] {s(N)=}")
# print(f"[DEBUG] {s(N // A)=}")
# print(f"[DEBUG] {s(N // B)=}")
# print(f"[DEBUG] {s(N // L)=}")
