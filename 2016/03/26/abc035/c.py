N, Q = map(int, input().split())

ocello = [0] * (N + 2)

for _ in range(Q):
    l, r = map(int, input().split())
    ocello[l] += 1
    ocello[r + 1] -= 1

for i in range(1, N + 2):
    ocello[i] += ocello[i - 1]

print(''.join(
    str(ocello[i] % 2)
    for i in range(1, N + 1)
))
