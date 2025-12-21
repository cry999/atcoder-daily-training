N = int(input())
AB = [tuple(map(int, input().split())) for _ in range(N)]

sum_a = sum(map(lambda x: x[0], AB))
ans = 0

for i in range(N):
    # 巨人 i をてっぺんにした時の値を全探索
    a, b = AB[i]
    ans = max(b+sum_a-a, ans)
print(ans)
