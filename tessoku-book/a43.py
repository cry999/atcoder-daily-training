N, L = map(int, input().split())
min_east, max_west = L+1, -1

for _ in range(N):
    A, B = input().split()
    A = int(A)

    if B == 'E':
        min_east = min(min_east, A)
    else:
        max_west = max(max_west, A)

print(max(max_west, L-min_east))
