N = int(input())
(*A,) = map(int, input().split())


ans = 0
for i in range(2):
    hist = [False] * (N + 1)
    j = i
    while i < N:
        # print(f"{i=}, {j=}, {hist=}")
        while j < i:
            j += 1
        # print(f"  1. {i=}, {j=}, {hist=}")

        while j + 1 < N and A[j] == A[j + 1] and not hist[A[j]]:
            hist[A[j]] = True
            j += 2
        # print(f"  2. {i=}, {j=}, {hist=}")

        ans = max(ans, j - i)
        hist[A[i]] = False
        if i + 1 < N:
            hist[A[i + 1]] = False
        i += 2
        # print(f"  3. {i=}, {j=}, {hist=}")

print(ans)
