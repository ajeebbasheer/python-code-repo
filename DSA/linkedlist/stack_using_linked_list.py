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

if __name__=="__main__":
    stack = Stack()
    stack.push(10)
    stack.push(20)
    stack.push(30)
    stack.push(40)
    stack.push(50)
    stack.display()
    stack.reverse()
    stack.display()
    stack.display_from_end(stack.top)
    print("\n")
