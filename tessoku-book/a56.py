N, Q = map(int, input().split())
S = input()
M = 1_000_000_007

hash_lr = [0] * (N+1)
B = 26
b_pow = [1] * (N+1)
for i in range(N):
    b_pow[i+1] = (b_pow[i] * B) % M

for i in range(N):
    hash_lr[i+1] = (ord(S[i])-ord('a')) + B*hash_lr[i]
    hash_lr[i+1] %= M

for _ in range(Q):
    a, b, c, d = map(int, input().split())
    hash_ab = (hash_lr[b] - b_pow[b-a+1] * hash_lr[a-1]) % M
    hash_cd = (hash_lr[d] - b_pow[d-c+1] * hash_lr[c-1]) % M
    print('Yes' if hash_ab == hash_cd else 'No')
