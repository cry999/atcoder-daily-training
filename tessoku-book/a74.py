# 縦と横は別々に考えられる。
# それぞれの方向でバブルソートの回数を数えれば良い。
N = int(input())
P = [list(map(int, input().split())) for _ in range(N)]

vert, hori = [0]*N, [0]*N
for i in range(N):
    for j in range(N):
        if P[i][j] != 0:
            hori[j] = P[i][j]
            vert[i] = P[i][j]


def bubble_count(a: list[int]) -> int:
    c = 0
    n = len(a)
    for i in range(n):
        for j in range(n-1, 0, -1):
            if a[j-1] <= a[j]:
                continue
            c += 1
            a[j-1], a[j] = a[j], a[j-1]
    return c


# print('vert:', bubble_count(vert))
# print('hori:', bubble_count(hori))
print(bubble_count(vert) + bubble_count(hori))
