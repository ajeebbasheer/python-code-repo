class Node:
    def __init__(self, data=None, next=None):
        self.data = data
        self.next = next
    
    def set_data(self, data):
        self.data = data
    
    def get_data(self):
        return self.data
    
    def set_next(self, next):
        self.next = next
    
    def get_next(self):
        return self.next

    def has_next(self):
        return self.next != None

class LinkedList:
    def __init__(self, head=None):
        self.head = head
        self.length = 0
    
    def traverse(self):
        node = self.head
        while (node):
            print(f"{node.get_data()} ==>")
            node = node.get_next()
    
    def insert(self, data):
        node = self.head
        while (node and node.get_next()):
            node = node.get_next()
        
        new_node = Node(data)
        if (not node):
            self.head = new_node
        else:
            node.set_next(new_node)



if __name__ == '__main__':
    ll = LinkedList()
    ll.insert(19)
    ll.insert(11)
    ll.insert(129)
    ll.traverse()
