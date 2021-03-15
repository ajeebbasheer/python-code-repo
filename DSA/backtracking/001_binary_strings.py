def append_to_list(x, arr):
    return [x + item for item in arr]

def bit_strings(n):
    if not n:
        return []
    if n==1:
        return ['0', '1']

    return append_to_list('0', bit_strings(n-1)) + append_to_list('1', bit_strings(n-1))


if __name__ == '__main__':
    n = int(input("Enter length:"))
    print(f"{bit_strings(n)}")
