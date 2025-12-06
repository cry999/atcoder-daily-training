# 累積和でとく
# c[n] = n 文字目を S を使うか T を使うかを 0/1 で表現する
import os


def debug(*args, **kwargs):
    if os.getenv('DEBUG', '0') == '1':
        print(*args, **kwargs)


N, M = map(int, input().split())
S, T = input(), input()

is_t = [0] * (N+1)

for _ in range(M):
    L, R = map(int, input().split())
    is_t[L-1] += 1
    is_t[R] -= 1

is_t[0] %= 2
for i in range(N):
    is_t[i+1] = (is_t[i] + is_t[i+1]) % 2

debug(is_t)

ans = ''.join(T[i] if is_t[i] else S[i] for i in range(N))
print(ans)
