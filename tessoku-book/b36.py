N, K = map(int, input().split())
S = input()

off = sum(1 for c in S if c == '0')
on = N - off

if on % 2 == K % 2:
    print('Yes')
else:
    print('No')
