from sys import stdin

input = stdin.readline


def main():
    N, K = map(int, input().split())

    ans = dist = [list(map(int, input().split())) for _ in range(N)]

    def prod(l, r):
        ret = [[float("inf")] * N for _ in range(N)]
        for i in range(N):
            for j in range(N):
                for k in range(N):
                    ret[i][j] = min(ret[i][j], l[i][k] + r[k][j])
        return ret

    K -= 1
    while K:
        if K & 1:
            ans = prod(ans, dist)
        dist = prod(dist, dist)
        K //= 2

    for i in range(N):
        print(ans[i][i])


main()
