N = int(input())
(*P,) = map(int, input().split())

i = 0
while i * 10 < N:
    min_n, max_n = 10**9, 0
    diff = min(N - i * 10, 10)
    for j in range(diff):
        min_n, max_n = min(min_n, P[i * 10 + j]), max(max_n, P[i * 10 + j])

    # print(f"[DEBUG] {i=}, {min_n=}, {max_n=}, {diff=}")
    if min_n == i * 10 + 1 and max_n == i * 10 + diff:
        i += 1
    else:
        print("No")
        break
else:
    print("Yes")
