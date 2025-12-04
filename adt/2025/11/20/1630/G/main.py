N, M = map(int, input().split())


def rec(start: int, depth: int) -> list[list[int]]:
    if depth == 1:
        return [[i] for i in range(start, M+1)]

    ans = []
    for i in range(start, M+1):
        res = rec(i+10, depth-1)
        if not res:
            break
        for r in res:
            ans.append([i]+r)
    return ans


ans = rec(1, N)
print(len(ans))
for row in ans:
    print(*row)
