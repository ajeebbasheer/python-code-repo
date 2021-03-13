def is_array_sorted(arr, n):
    if n < 1:
        return True
    if arr[n] < arr[n-1]:
        return False
    return is_array_sorted(arr, n-1)
    
if __name__=='__main__':
    arr = [227, 220, 246, 277, 321, 454, 534, 565, 1933]
    ret = is_array_sorted(arr, len(arr)-1)
    print(f"Sorted: {ret}")
