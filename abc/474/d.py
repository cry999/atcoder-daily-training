N = int(input())
(*A,) = map(int, input().split())
(*B,) = map(int, input().split())
C = [a - b for a, b in zip(A, B)]
neg_sum = sum(-c for c in C if c < 0)
pos_sum = sum(c for c in C if c > 0)

if neg_sum < pos_sum * 10**18:
    print("Yes")
    ans = []
    for c in C:
        if c < 0:
            ans.append(1)
        else:
            ans.append(10**18)
    print(*ans)
else:
    print("No")
