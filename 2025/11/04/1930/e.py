N = int(input())

s = ''
for i in range(N):
    s = ' '.join(filter(lambda x: x, [s, f'{i+1}', s]))
print(s)
