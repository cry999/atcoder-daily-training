s1 = input()
s2 = input()

for s in [s1, s2, s1[0] + s2[0], s1[1] + s2[1]]:
    if s == "AD" or s == "DA":
        print("Yes")
        break
else:
    print("No")
