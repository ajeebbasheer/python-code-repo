def k_ary_strings(k, n):
    if not n:
        return []
    if n == 1:
        return [str(x) for x in range(k)]
         
    return [x + y for x in k_ary_strings(k, 1) for y in k_ary_strings(k, n-1)]

if __name__ == '__main__':
    n = int(input("Enter n:"))
    k = int(input("Enter k:"))
    print(f"{k_ary_strings(k, n)}")
