class Node:
    def __init__(self, data, next=None):
        self.data = data
        self.next = next

class Stack:
    def __init__(self):
        self.top = None
        self.length = 0

    def push(self, data): #insert at head
        node = Node(data)
        self.length +=1
        
        if not self.top:
            self.top = node
            return
        
        node.next = self.top
        self.top = node
    
    def pop(self):  #delete head
        if not self.top:
            print("Stack Empty!")
            return
        top = self.top
        self.top = self.top.next
        top.next = None
        return top.data
    
    def insert_at_bottom(self, data):
        node = Node(data)
        self.length +=1

        if not self.top:
            self.top = node
            return

        curr = self.top
        while(curr.next):
            curr = curr.next

        curr.next = node

    def display(self):
        if not self.top:
            print("Stack Empty!")
            return
        curr = self.top
        while(curr):
            print(f"{curr.data} <=", end='')
            curr = curr.next
        print("\n")

    def display_from_end(self, top):
        if top:
            self.display_from_end(top.next)
            print(f"{top.data} <=", end='')

    def reverse(self):
        if self.top:
            item = self.pop()
            self.reverse()
            self.insert_at_bottom(item)

class Queue:
    def __init__(self):
        self.front = self.rear = None
        self.length = 0
    
    def is_empty(self):
        if self.front is None:
            return True
        return False

    def enqueue(self, data):
        node = Node(data)
        self.length += 1
        if self.is_empty():
            self.front = self.rear = node
            return
        self.rear.next = node
        self.rear = node
        return
    
    def dequeue(self):
        if self.is_empty():
            return
        temp = self.front
        self.front = temp.next
        if self.front == None:
            self.rear = None
        return temp.data

    def display(self):
        if self.front is None:
            print(f"Queue is empty")
            return
        curr = self.front
        while(curr):
            print(f"{curr.data} => ", end="")
            curr = curr.next
        print("\n")

if __name__=="__main__":
    q = Queue()
    item = q.dequeue()
    q.enqueue(10)
    q.enqueue(20)
    q.enqueue(30)
    q.enqueue(34)
    q.enqueue(33)
    q.enqueue(32)
    q.enqueue(31)
    q.display()
    item = q.dequeue()
    item = q.dequeue()
    item = q.dequeue()
    print(f"item: {item}")
    q.display()

