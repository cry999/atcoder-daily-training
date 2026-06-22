from math import lcm

N, M = map(int, input().split())
(*A,) = map(int, input().split())

# fact2[i] := A[i] が 2 で割り切れる回数
fact2 = [0] * N
for i in range(N):
    a = A[i]
    while a % 2 == 0:
        fact2[i] += 1
        a //= 2

    # A[i] が 2 で割り切れる回数が異なる場合は、
    # LCM / A{i] が奇数にならない i が存在する。
    # それは半公倍数にはならないためアウト。
    if i > 0 and fact2[i - 1] != fact2[i]:
        print(0)
        break
else:
    l = lcm(*A) // 2
    print((M + l) // (2 * l))
