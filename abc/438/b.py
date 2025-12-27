N, M = map(int, input().split())
S = input()
T = input()

ans = float('inf')
for i in range(N-M+1):
    cnt = 0
    for k in range(M):
        s, t = ord(S[i+k])-ord('0'), ord(T[k])-ord('0')
        if s >= t:
            cnt += s-t
        else:
            cnt += 10-t+s
    ans = min(ans, cnt)
print(ans)
