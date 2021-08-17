from functools import reduce


def get_longest_substring_dp(digit_string):
    n = len(digit_string)
    
    sum_ = {(i, j): None for i in range(n) for j in range(n) if i<=j}
    
    max_length = 0
    max_sub_string = None
    
    for i in range(n):
        sum_[(i, i)] = int(digit_string[i])
        
    for len_ in range(2, n+1):
        for start in range(n-len_+1):
            end = start + len_ -1
            mid = int(len_/2)
            
            sum_[(start, end)] = sum_[(start, end-mid)] + sum_[(end-mid+1,end)]
            if len_ %2 ==0 and (sum_[(start, end-mid)] == sum_[(end-mid+1,end)]):
                if max_length < len_:
                    max_sub_string = digit_string[start:end+1]
                    max_length = len_
    
    print(max_sub_string)
    return max_length
        
        
def get_longest_substring_old(digit_string):
    n = len(digit_string)
    
    sum_ = {(i, j): None for i in range(n) for j in range(n) if i<=j}
    
    max_length = 0
    max_sub_string = None
    
    for i in range(n):
        sum_[(i, i)] = int(digit_string[i])
    
    for i in range(n):
        for j in range(i+1, n, 2):
            mid = i + int((j-i)/2)
            left = digit_string[i:mid+1]
            right = digit_string[mid+1:j+1]
            lsum = reduce(lambda x, y: int(x)+int(y), left)
            rsum = reduce(lambda x, y: int(x)+int(y), right)
            
            if lsum == rsum:
                curr_len = len(left+right)
                if max_length < curr_len:
                    max_length = curr_len
                    max_sub_string = digit_string[i: j+1]
            
            
    print(max_sub_string)
    return curr_len
    

if __name__ == '__main__':
    print(get_longest_substring_dp('9430723'))
    print(get_longest_substring_dp('142124'))
