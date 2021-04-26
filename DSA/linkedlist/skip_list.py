from random import randint

class Node:
    def __init__(self, data, levels):
        self.data = data
        self.next = [None] * levels
        self.levels = levels

class SkipList:
    def __init__(self, maxLevels=4):
        self.max_levels = maxLevels
        self.head = Node("HEAD", maxLevels)
    
    def display(self):
        level = self.max_levels-1
        while(level >= 0):
            print("HEAD => ", end='')
            curr = self.head.next[level]
            while(curr):
                print(f"{curr.data} => ", end='')
                curr = curr.next[level]
            print("None")
            level -=1
    
    def num_of_tails(self):
        count = 1
        flip = randint(0,1)
        while(not flip):
            count +=1
            flip = randint(0,1)
            if count == self.max_levels:
                break
        return count

    def insert(self, data):
        curr = self.head
        level = self.max_levels - 1
        # initialize array to store last traversed node in each level.
        last_nodes = [None] * self.max_levels
        while(level >=0):
            # if next node is null, come down.
            if not curr.next[level]:
                last_nodes[level] = curr
                level -= 1
                continue

            next_node = curr.next[level]

            # if next node is bigger, come down.
            if next_node.data > data:
                last_nodes[level] = curr
                level -= 1
                continue
            else:
                curr = curr.next[level]
        
        # we are at the previous node of the node to be installed.
        level = 0
        next_array_size = self.num_of_tails()
        new_node = Node(data, next_array_size)
        while(level < next_array_size):
            curr = last_nodes[level]
            next_node = curr.next[level]
            curr.next[level] = new_node
            new_node.next[level] = next_node
            level +=1
        
        print(f"Added {data} with {next_array_size} levels..")

    def delete(self, data):
        curr = self.head
        level = self.max_levels - 1
        # initialize array to store last traversed node in each level.
        last_nodes = [None] * self.max_levels
        while(level >=0):
            # if next node is null, come down.
            if not curr.next[level]:
                last_nodes[level] = curr
                level -= 1
                continue

            next_node = curr.next[level]

            # if next node is bigger, come down.
            if next_node.data >= data:
                last_nodes[level] = curr
                level -= 1
                continue
            else:
                curr = curr.next[level]
        
        # we are at the previous node of the node to be deleted.
        # make sure next node is the node to be deleted.

        delete_node = curr.next[0]
        if delete_node.data != data:
            print (f"No element with data {data} found!")
            return
        
        level = 0
        levels = delete_node.levels
        while(level < levels):
            curr = last_nodes[level]
            next_node = delete_node.next[level]
            curr.next[level] = next_node
            level +=1
        
        print(f"Deleted {data}..")

    def find(self, data):
        curr = self.head
        level = self.max_levels - 1
        # initialize array to store last traversed node in each level.
        last_nodes = [None] * self.max_levels
        while(level >=0):
            # if next node is null, come down.
            if not curr.next[level]:
                last_nodes[level] = curr
                level -= 1
                continue

            next_node = curr.next[level]

            if next_node.data == data:
                print(f"Search success!!. Element Found")
                return

            # if next node is bigger, come down.
            if next_node.data > data:
                last_nodes[level] = curr
                level -= 1
                continue
            else:
                curr = curr.next[level]

        print(f"Search failed!!. No Element Found")                
        
if __name__ == '__main__':
    sl = SkipList()
    # sl.display()
    for item in range(10):
        data = randint(5, 55)
        sl.insert(data)
    sl.insert(23)
    sl.display()
    sl.find(23)
    sl.delete(23)
    sl.display()
    sl.find(23)
    
    
    
        
    
            
