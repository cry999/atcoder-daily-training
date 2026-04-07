N = int(input())
S = input()

cnt_o = S.count("o")
cnt_x = S.count("x")

if cnt_o and not cnt_x:
    print("Yes")
else:
    print("No")
