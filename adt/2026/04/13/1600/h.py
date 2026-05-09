N = int(input())
(*H,) = map(int, input().split())
A = [0] * N

prev_hights = []

for j in range(N):
    while prev_hights:
        h, i = prev_hights[-1]
        if H[j] < h:
            A[j] = A[i] + H[j] * (j - i)
            prev_hights.append([H[j], j])
            break
        prev_hights.pop()
    else:
        A[j] = H[j] * (j + 1) + 1
        prev_hights.append([H[j], j])


print(*A)
