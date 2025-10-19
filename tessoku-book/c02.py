N = int(input())
print(sum(list(sorted(map(int, input().split()), reverse=True))[:2]))
