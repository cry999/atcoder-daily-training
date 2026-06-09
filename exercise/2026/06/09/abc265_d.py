N, P, Q, R = map(int, input().split())
(*A,) = map(int, input().split())

C = [0] * (N + 1)
for i in range(N):
    C[i + 1] = C[i] + A[i]

x, y, z, w = 0, 0, 0, 0
p, q, r = 0, 0, 0
while x < N:
    if y <= x:
        y = x
        p = 0

    while y < N and p < P:
        p += A[y]
        q -= A[y]
        y += 1

    if p == P:
        if z <= y:
            z = y
            q = 0

        while z < N and q < Q:
            q += A[z]
            r -= A[z]
            z += 1

        if q == Q:
            if w <= z:
                w = z
                r = 0

            while w < N and r < R:
                r += A[w]
                w += 1

            if r == R:
                print("Yes")
                # print("[DEBUG]", x, y, z, w)
                break

    p -= A[x]
    x += 1
else:
    print("No")
