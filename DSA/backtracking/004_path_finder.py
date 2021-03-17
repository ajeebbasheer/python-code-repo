def path_finder(matrix, position, n):
    if position == (n-1, n-1):
        return [(n-1, n-1)]
    x, y = position
    print(f"position: {position}")

    if x+1 < n and matrix[x+1][y]==1:
        a = path_finder(matrix, (x+1,y), n)
        print(f"a: {a}")
        if a:
            return [(x,y)] + a

    if y+1 < n and matrix[x][y+1]==1:
        b = path_finder(matrix, (x,y+1), n)
        print(f"b: {b}")
        if b:
            return [(x,y)] + b

if __name__ == "__main__":
    matrix = [[1,1,1,1,0],
              [0,1,0,1,0],
              [0,1,0,1,0],
              [0,1,0,0,0],
              [1,1,1,1,1]]
    print(f"{path_finder(matrix, (0,0), 5)}")
