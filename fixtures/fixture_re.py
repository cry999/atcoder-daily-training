# fixture: 常に RE (Runtime Error) で異常終了
n = int(input())
raise RuntimeError(f"intentional crash with n={n}")
