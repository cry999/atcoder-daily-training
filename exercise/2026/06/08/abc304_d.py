from bisect import bisect_left

W, H = map(int, input().split())
N = int(input())
strawberries = [tuple(map(int, input().split())) for _ in range(N)]

A = int(input())
(*a,) = map(int, input().split())
a.append(W)

B = int(input())
(*b,) = map(int, input().split())
b.append(H)

# pieces := いちごを含むケーキのピース
pieces = {}

for p, q in strawberries:
    i = bisect_left(a, p)
    j = bisect_left(b, q)

    pieces.setdefault(i, {})
    pieces[i].setdefault(j, 0)
    pieces[i][j] += 1

m, M = N, 0
n = 0
for k, d in pieces.items():
    m = min(m, min(d.values()))
    M = max(M, max(d.values()))
    n += len(d)

if n < (A + 1) * (B + 1):
    # 空いているピースがある。
    m = 0

print(m, M)
