N = int(input())

loss = 0
for _ in range(N):
    raw_a, raw_b, s = input().split()
    a, b = map(int, [raw_a, raw_b])

    if s == "keep":
        loss += b - a
print(loss)
