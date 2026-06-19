from collections import Counter

N = int(input())
(*A,) = map(int, input().split())

counter = Counter(A)
s = sum(A)

Q = int(input())
for _ in range(Q):
    b, c = map(int, input().split())

    cnt = counter[b]

    s -= b * cnt
    s += c * cnt

    counter[b] = 0
    counter[c] += cnt

    print(s)
