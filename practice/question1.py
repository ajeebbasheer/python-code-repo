lst = [ x for x in range(1999, 3201) if x%7 ==0 and x%5 != 0]


"""list = [a, b, c, ..]
str(list) = '[a, b, c, ..]'
str(list).strip('[]') = a, b, c .. strip out '[' and ']'
"""

print(str(lst).strip('[]'))

print('\n')
#map applies a function to all items to a list

print(', '.join(map(str,lst)))
