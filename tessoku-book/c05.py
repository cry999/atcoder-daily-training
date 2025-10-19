# 10 桁の 2 進数表現において、 0->4 / 1->7 と変換すれば良い
print((
    lambda N: sum((7 if (N-1) & (1 << i) else 4)*(10**i) for i in range(10))
)(int(input())))
