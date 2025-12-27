N = int(input())


cnt = 0
for a in range(1, N+1):
    # print(f'{a=}')
    if a**3 >= N:
        cnt += a**3 == N
        break
    # print(f'{a=}')
    for b in range(a, N+1):
        if a * (b**2) >= N:
            cnt += a * (b**2) == N
            break
        # print(f'  {b=}')
        # print(f'    c={b}~{N//(a*b)}({N//(a*b)-b+1=})')
        cnt += N // (a * b) - b + 1
print(cnt)
