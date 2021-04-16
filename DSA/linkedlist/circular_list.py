import random

class Node:
    def __init__(self, value, next = None):
        self.value = value
        self.next = next
    def get_value(self):
        return self.value
    def set_value(self, value):
        self.value = value
    def get_next(self):
        return self.next
    def set_next(self, next):
        self.next = next
    def has_next(self):
        return self.next != None

class CircularList:
    def __init__(self, values):
        self.head = None
        self.tail = None
        self.length = 0
        for value in values:
            self.insert_at_head(value)
    
    def insert_at_head(self, item):
        new_node = Node(item)
        self.length +=1
        if not self.head:
            self.head = new_node
            self.tail = self.head
            self.head.set_next(self.head)
            return
        
        new_node.set_next(self.head)
        self.tail.set_next(new_node)
        self.head = new_node
    
    def insert_at_tail(self, item):
        new_node = Node(item)
        self.length +=1

        if not self.head:
            self.head = new_node
            self.tail = self.head
            self.head.set_next(self.head)
            return
        
        self.tail.set_next(new_node)
        new_node.set_next(self.head)
        self.tail = new_node

    def insert_at_position(self, item, pos):
        error_msg = "Invalid position"
        if pos < 1 or pos > self.length +1:
            print(f"{error_msg}")
            return

        if not self.head and pos !=1:
            print(f"{error_msg}")
            return

        if pos == 1:
            self.insert_at_head(item)
            return

        new_node = Node(item)
        self.length +=1
        i = 0
        curr = self.head
        prev = self.head
        while(i < pos - 1):
            prev = curr
            curr = curr.get_next()
            i +=1

        prev.set_next(new_node)
        new_node.set_next(curr)

    def delete_head(self):
        if not self.head:
            print("List Empty!")
            return
        
        next = self.head.get_next()
        self.tail.set_next(next)
        self.head = next
        self.length -=1

    def delete_tail(self):
        if not self.head:
            print("List Empty!")
            return
        
        curr = self.head
        prev = self.head
        while(curr != self.tail):
            prev = curr
            curr = curr.get_next()
        
        prev.set_next(self.head)
        self.tail = prev
        self.length -=1
    
    def delete_node_at_position(self, pos):
        if pos <1 or pos > self.length:
            print ("invalid position")
            return
        
        self.length -=1
        if self.length ==1 and pos == 1:
            self.head = None
            self.tail = None
            return
        curr = self.head
        prev = self.head
        i = 0
        while(i< pos-1):
            prev = curr
            curr = curr.get_next()
            i +=1
        next = curr.get_next()
        prev.set_next(next)
        
    
    def traverse(self):
        if not self.head:
            print ("List Empty!")
            return

        node = self.head
        print (f"{node.get_value()} => ", end="")
        node = node.get_next()

        while(node != self.head):
            print (f"{node.get_value()} => ", end="")
            node = node.get_next()
        print("")

if __name__=='__main__':
    ll = CircularList([random.randint(x, x+100) for x in range(10, 20)])
    ll.traverse()
    ll.insert_at_tail(10010)
    ll.traverse()
    ll.insert_at_head(222)
    ll.traverse()
    ll.insert_at_position(111, 1)
    ll.traverse()
    ll.insert_at_position(333, 3)
    ll.traverse()
    ll.delete_head()
    ll.traverse()
    ll.delete_tail()
    ll.traverse()
    ll.delete_node_at_position(3)
    ll.traverse()
