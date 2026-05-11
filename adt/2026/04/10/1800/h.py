N, X, Y = map(int, input().split())
(*A,) = map(int, input().split())


def solve(B: list[int], max_v: int, min_v: int):
    if not B:
        return 0
    l, r = 0, 0
    num_max, num_min = 0, 0
    ret = 0
    while l < len(B):
        while r < len(B) and not (num_max and num_min):
            num_max += B[r] == max_v
            num_min += B[r] == min_v
            r += 1

        if num_max and num_min:
            ret += len(B) - r + 1

        num_max -= B[l] == max_v
        num_min -= B[l] == min_v
        l += 1
    return ret


i, ans = 0, 0
while i < N:
    B = []
    while i < N and not Y <= A[i] <= X:
        i += 1
    while i < N and Y <= A[i] <= X:
        B.append(A[i])
        i += 1

    ans += solve(B, X, Y)

print(ans)
