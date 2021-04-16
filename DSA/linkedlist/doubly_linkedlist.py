import random

class DLLNode:
    def __init__(self, value, prev=None, next=None):
        self.value = value
        self.prev = None
        self.next = None
    
    def get_value(self):
        return self.value
    
    def set_value(self, value):
        self.value = value
    
    def get_next(self):
        return self.next
    
    def set_next(self, next):
        self.next = next
    
    def get_prev(self):
        return self.prev

    def set_prev(self, prev):
        self.prev = prev

    def has_next(self):
        return self.next != None
    
    def has_prev(self):
        return self.prev != None


class DoublyLinkedList:
    def __init__(self, items=[]):
        self.head = None
        self.tail = None
        self.length = 0
        for item in items:
            self.insert_at_head(item)

    def insert_at_head(self, item):
        new_node = DLLNode(item)
        self.length +=1
        if not self.head:
            self.head = new_node
            self.tail = new_node
            return
        
        new_node.set_next(self.head)
        self.head.set_prev(new_node)
        self.head = new_node

    def insert_at_tail(self, item):
        new_node = DLLNode(item)
        self.length +=1
        if not self.tail:
            self.head = new_node
            self.tail = new_node
            return
        
        new_node.set_prev(self.tail)
        self.tail.set_next(new_node)
        self.tail = new_node
        
    def insert_at_position(self, item, pos):
        error_msg = "Invalid position!"
        if pos < 1 or pos > self.length:
            print(f"{error_msg}")
            return
        
        if (not self.head) and pos != 1:
            print(f"{error_msg}")
            return
        
        if pos == 1:
            self.insert_at_head(item)
            return
        
        new_node = DLLNode(item)
        self.length +=1
        curr = self.head

        i = 0
        while(i < pos-2):
            curr = curr.get_next()
            i +=1
        
        # need to insert new node between 'curr' and 'curr.next'
        

        next = curr.get_next()

        new_node.set_next(next)
        new_node.set_prev(curr)

        curr.set_next(new_node)
        
        # beware that curr.next could be None for last node.
        if next:
            next.set_prev(new_node)
        

    def delete_head(self):
        if not self.head:
            print("List Empty!")
            return
        
        next = self.head.get_next()
        if next:
            next.set_prev(None)
        
        self.head.set_next(None)
        self.head = next
        self.length -=1
    
    def delete_tail(self):
        if not self.tail:
            print("List Empty!")
            return
        
        prev = self.tail.get_prev()
        self.tail.set_prev(None)
        prev.set_next(None)
        self.tail = prev
        self.length -=1

    def delete_node_at_pos(self, pos):
        error_msg = "Invalid Position"
        if pos < 1 or pos> self.length:
            print(f"{error_msg}")
            return
        
        if not self.head.get_next():
            if pos == 1:
                self.head = None
            else:
                print(f"{error_msg}")
            return
        
        i = 0
        curr = self.head
        prev = self.head

        while(i < pos-1):
            prev = curr
            curr = curr.get_next()
            i +=1
        
        next = curr.next
        prev.set_next(next)
        if next:
            next.set_prev(prev)
        self.length -= 1
        

        
    def traverse(self):
        curr = self.head
        print(f"HEAD: {ll.head.get_value()} TAIL: {ll.tail.get_value()} LEN: {ll.length}")
        while(curr):
            end = " <=> " if curr.has_next() else "\n"
            print(f"{curr.get_value()}", end=end)
            curr = curr.get_next()
    
    def traverse_reverse(self):
        curr = self.tail
        while(curr):
            end = " <=> " if curr.has_prev() else "\n"
            print(f"{curr.get_value()}", end=end)
            curr = curr.get_prev()
    
if __name__=='__main__':
    ll = DoublyLinkedList([random.randint(x, x+100) for x in range(10, 18)])
    ll.traverse()
    # ll.traverse_reverse()
    ll.insert_at_tail(111)
    ll.traverse()
    ll.insert_at_position(9090, 3)
    ll.traverse()
    ll.traverse_reverse()
    ll.delete_head()
    ll.traverse()
    ll.delete_tail()
    ll.traverse()
    ll.traverse_reverse()
    ll.delete_node_at_pos(3)
    ll.traverse()
    ll.traverse_reverse()
    ll.delete_node_at_pos(3)
    ll.traverse()
    ll.delete_node_at_pos(3)
    ll.traverse()
    ll.delete_node_at_pos(3)
    ll.traverse()
    ll.delete_node_at_pos(3)
    ll.traverse()
    ll.delete_node_at_pos(3)
    ll.traverse()
    ll.delete_node_at_pos(1)
    ll.traverse()
    ll.delete_node_at_pos(1)
    ll.traverse()
    ll.delete_node_at_pos(1)
    ll.traverse()


