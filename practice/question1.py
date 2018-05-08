"""
Question 1
Level 1

Question:
Write a program which will find all such numbers which are divisible by 7 but are not a multiple of 5,
between 2000 and 3200 (both included).
The numbers obtained should be printed in a comma-separated sequence on a single line.
-----------------------------------------------------------------------------------------------------
"""

lst = [ x for x in range(1999, 3201) if x%7 ==0 and x%5 != 0]


"""list = [a, b, c, ..]
str(list) = '[a, b, c, ..]'
str(list).strip('[]') = a, b, c .. strip out '[' and ']'
"""

print(str(lst).strip('[]'))

print('\n')
#map applies a function to all items to a list

print(', '.join(map(str,lst)))
