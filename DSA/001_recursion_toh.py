def toh (n, startPeg=1, endPeg=3):
    if n:
        toh(n-1, startPeg, 6-startPeg-endPeg)
        print(f"Move Disk-{n} from {startPeg} to {endPeg}")
        toh(n-1, 6-startPeg-endPeg, endPeg)

def tower_of_hanoi(n, start='START', end='DEST', aux='AUX'):
    if n:
        tower_of_hanoi(n-1, start, aux, end)
        print(f"Move Disk-{n} from {start} to {end}")
        tower_of_hanoi(n-1, aux, end, start)

if __name__=='__main__':
    n = int(input("Number of disks: "))
    toh(n)
    tower_of_hanoi(n)
