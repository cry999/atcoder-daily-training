N = int(input())
print(list(sorted(zip(map(int, input().split()), range(N))))[-2][1]+1)
