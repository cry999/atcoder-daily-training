S = input()

ans = 0
for s in S:
    ans = ans*26 + (ord(s)-ord('A')+1)

print(ans)
