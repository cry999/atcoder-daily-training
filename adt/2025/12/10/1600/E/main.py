K = int(input())

d = []
while K:
    d.append(2 if K % 2 else 0)
    K //= 2
print(''.join(map(str, d[::-1])))
