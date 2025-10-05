N = int(input())
S = list(input() for _ in range(N))

for i in range(N):
    for j in range(N):
        if i == j:
            continue
        s = S[i] + S[j]
        for k in range(len(s)//2):
            if s[k] == s[-(k+1)]:
                continue
            break
        else:
            print('Yes')
            exit()
print('No')
