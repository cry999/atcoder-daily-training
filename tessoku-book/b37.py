def f(x: int) -> int:
    return x * (x + 1) // 2


N = int(input())

ans = 0
for i in range(15):
    ten_i = 10**i
    ans += (N//(ten_i * 10))*f(9)*ten_i
    ans += f(((N//ten_i) % 10)-1)*ten_i
    ans += ((N//ten_i) % 10)*((N % ten_i)+1)

print(ans)
