N, X, Y = map(int, input().split())
*A, = sorted(map(int, input().split()), reverse=True)
*B, = sorted(map(int, input().split()), reverse=True)

amasa = 0
num_amasa = 0
for a in A:
    num_amasa += 1
    amasa += a
    if amasa > X:
        break

shoppasa = 0
num_shoppasa = 0
for b in B:
    num_shoppasa += 1
    shoppasa += b
    if shoppasa > Y:
        break

print(min(num_amasa, num_shoppasa))
