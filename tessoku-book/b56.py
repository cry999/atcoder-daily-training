N, Q = map(int, input().split())
S = input()

h_forward = [0] * (N+1)
h_backward = [0] * (N+1)

B = 26
M = 1_000_000_007
b_pow = [1] * (N+1)
for i in range(N):
    b_pow[i+1] = (b_pow[i] * B) % M

for i, s in enumerate(S):
    h_forward[i+1] = (B * h_forward[i] + (ord(s) - ord('a'))) % M
for i, s in enumerate(reversed(S)):
    h_backward[i+1] = (B * h_backward[i] + (ord(s) - ord('a'))) % M

for _ in range(Q):
    L, R = map(int, input().split())
    mid = (L + R) // 2
    if (L + R) % 2:
        front_half = (h_forward[mid] - b_pow[mid-L+1] * h_forward[L-1]) % M
        rear_half = (h_backward[N-mid] - b_pow[R-mid] * h_backward[N-R]) % M
    else:
        front_half = (h_forward[mid-1] - b_pow[mid-L] * h_forward[L-1]) % M
        rear_half = (h_backward[N-mid] - b_pow[R-mid] * h_backward[N-R]) % M
    print('Yes' if front_half == rear_half else 'No')
