# node v と v-1,v+1 を結べば良い
N = int(input())
print(N)
print('\n'.join(f'{(i) % N or N} {i+1}' for i in range(N)))
