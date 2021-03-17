def getVal(arr, i, j, L, H):
    if i<0 or i>=L or j<0 or j>=H:
        return 0
    else:
        return arr[i][j]

def findMaxBlock (arr, r, c, L, H, size):
    global maxsize
    global cntarr
    print(f"cntarr: {cntarr} size: {size} maxsize: {maxsize}")
    if (r>=L or c>=H):
        return
    cntarr[r][c] = 1
    size +=1
    if size > maxsize:
        maxsize = size

    direction = [[-1, 0], [-1, -1], [0, -1], [1, -1], [1, 0], [1, 1], [0, 1], [-1, 1]]

    for i in range(0, 7):
        newi = r + direction[i][0]
        newj = c + direction[i][1]
        val = getVal(arr, newi, newj, L, H)
        if val > 0 and cntarr[newi][newj] == 0:
            # print(f"Calling findMaxBlockfrom inside with newi:{newi}, newj:{newj}, L: {L}, H: {H}, size: {size}")
            findMaxBlock(arr, newj, newj, L, H, size)
    cntarr[r][c] = 0

def getMaxOnes(arr, max, colmax):
    global maxsize
    global size
    global cntarr
    for i in range(0, max):
        for j in range(0, colmax):
            if arr[i][j] == 1:
                # print(f"Calling findMaxBlock with i:{i}, j{j}, max: {max}, colmax: {colmax}, size: 0")
                findMaxBlock(arr, i, j, max, colmax, 0)

    return maxsize

if __name__ == "__main__":
    zarr = [[1,1,0,0,0], [0,1,1,0,1], [0,0,0,1,1], [1,0,0,1,1],[0,1,0,1,1]]
    rmax = 5
    colmax = 5
    maxsize = 0
    size = 0
    cntarr = rmax * [colmax * [0]]  # [[0, 0, 0, 0, 0], [0, 0, 0, 0, 0], [0, 0, 0, 0, 0], [0, 0, 0, 0, 0], [0, 0, 0, 0, 0]]
    print(f"{getMaxOnes(zarr, rmax, colmax)}")
