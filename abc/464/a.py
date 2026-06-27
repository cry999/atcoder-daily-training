S = input()
N = len(S)
E = S.count("E")
if 2 * E >= N:
    print("East")
else:
    print("West")
