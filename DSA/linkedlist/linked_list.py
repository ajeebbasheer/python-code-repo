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

class LinkedList:
    def __init__(self, items=[]):
        self.head = None
        self.length = 0
        for item in items[::-1]:
            self.insert_at_head(item)
    
    def insert_at_head(self, item):
        new_node = Node(item)
        self.length +=1
        if not self.head:
            self.head = new_node
            return
        new_node.set_next(self.head)
        self.head = new_node
        self.traverse()
    
    def insert_at_end(self, item):
        new_node = Node(item)
        self.length += 1
        if not self.head:
            self.head = new_node
            return
        curr = self.head
        while(curr.has_next()):
            curr = curr.get_next()
        curr.set_next(new_node)
        self.traverse()
    
    def insert_at_position(self, item, pos):
        error_msg = "Invalid Position"
        if not self.head:
            if pos == 1:
                self.insert_at_head(item)
            else:
                print(f"\n{error_msg}")
            return
        
        if pos < 1 or pos > self.length:
            print(f"\n{error_msg}")
            return
                
        new_node = Node(item)
        self.length +=1

        prev = self.head
        curr = self.head
        i = 0
        while (i < pos-1):
            prev = curr
            curr = curr.get_next()
            i +=1
        new_node.set_next(curr)
        prev.set_next(new_node)
        self.traverse()
    
    def delete_head_node(self):
        if not self.head:
            print(f"\nList Empty!!")
            return
        
        self.head = self.head.get_next()
        self.length -= 1
        self.traverse()
    
    def delete_tail_node(self):
        if not self.head:
            print(f"\nList Empty!!")
            return
        if not self.head.has_next():
            self.head = None
            return
        
        i = 0
        curr = self.head
        while(i < self.length-2):
            curr = curr.get_next()
            i +=1

        curr.set_next(None)
        self.length -= 1
        self.traverse()     

    def delete_node_at_pos(self, pos):
        if not self.head:
            print("\nList Empty!")
            return

        if pos < 1 or pos > self.length:
            print("\nInvalid Position!")
            return
        
        self.length -= 1
        
        if not self.head.has_next():
            self.head = None
            return
        
        i = 0
        curr = self.head
        prev = self.head

        while(i < pos-1):
            prev = curr
            curr = curr.get_next()
            i +=1
        
        prev.set_next(curr.get_next())
        self.traverse()

        
    def traverse(self):
        node = self.head
        print(f"List Length: {self.length}")
        while(node):
            end = " => " if node.has_next() else "\n\n"
            print(f"{node.get_value()}", end=end)
            node = node.get_next()

if __name__=='__main__':
    ll = LinkedList([random.randint(x, x+100) for x in range(10, 20)])
    ll.traverse()
    # ll.delete_tail_node()
    # ll.delete_node_at_pos(3)
    
    while True:
        ch = int(input(f"\n--LINKED LIST--\n\n1. Insert at head\n2. Insert at tail\n3. Insert at position\n4. Delete head\n5. Delete tail\n6. Delete node at position\n7. Traverse\n8. Quit\n\nEnter your choice: "))

        if ch == 8 or ch < 1 or ch > 8:
            break
        
        if ch <= 3:
            x = int(input("\nEnter value:"))
            if ch == 1:
                ll.insert_at_head(x)
            elif ch == 2:
                ll.insert_at_end(x)
            else:
                pos = int(input("\nEnter Position: "))
                ll.insert_at_position(x, pos)
        else:
            if ch == 4:
                ll.delete_head_node()
            elif ch == 5:
                ll.delete_tail_node()
            elif ch == 6:
                pos = int(input("Enter Position: "))
                ll.delete_node_at_pos(pos)
            elif ch == 7:
                ll.traverse()
