# 尺取り法でいけそう。
# 計算量は O(N) である。

N = int(input())
S = input()
*W, = map(int, input().split())

adult_cnt, child_cnt = sum(c == '1' for c in S), 0
max_score = adult_cnt
WS = sorted(zip(W, S))

i = 0
while i < N:
    w = WS[i][0]
    while i < N and WS[i][0] == w:
        w, s = WS[i]
        i += 1
        if s == '1':
            adult_cnt -= 1
        else:
            child_cnt += 1
    max_score = max(max_score, adult_cnt+child_cnt)
print(max_score)
