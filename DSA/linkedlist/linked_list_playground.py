import random
from linked_list import LinkedList, Node

class PlayGround(LinkedList):
    def __init__(self, items = []):
        super().__init__(items)

    def nth_node_from_end(self, n):
        ptr1 = self.head
        ptr2 = self.head
        i = 0
        while(i < n-1):
            if not ptr1:  # we already reached end, n is invalid.
                print("n it greater than list length")
                return
            ptr1 = ptr1.get_next()
            i +=1
        
        # now ptr1 is at nth node.
        print(f"Ptr1 is at: {ptr1.get_value()}. Start Ptr2 to move..")
        while(ptr1):
            ptr1 = ptr1.get_next()
            if (ptr1): # we should stop immediatly when ptr1 reaches None.
                ptr2 = ptr2.get_next()

        print(f"Nth node from end: {ptr2.get_value()}")

    def insert_in_a_sorted_list(self, data):
        node = Node(data)
        self.length +=1
        if not self.head:
            self.head = node
            return
        prev = None
        curr = self.head
        while(curr and curr.get_value() < data):
            prev = curr
            curr = curr.get_next()
        
        if prev:
            prev.set_next(node)
        else:
            self.head = node
        node.set_next(curr)

    def reverse_list(self):
        prev = None
        curr = self.head
        while(curr):
            next = curr.get_next()
            curr.set_next(prev)
            prev = curr
            curr = next
        self.head = prev

    def reverse_list_recursive(self, curr, prev):
        if not curr:
            return None

        if not curr.next:
            self.head = curr
        
        next = curr.get_next()
        curr.set_next(prev)
        prev = curr
        curr = next 
        self.reverse_list_recursive(curr, prev)
    
    def reverse_recursive(self, node):
        if not node:  # Reverse of None is None
            return None
        
        if not node.next:  # Reverse of a single node is the node itself.
            self.head = node  # you are at the last node. make this head.
            return node

        # reverse of rest of the list
        rest = self.reverse_recursive(node.next)

        # now we are at second last node.
        node.next.next = node   #make last node points to secondlast node.
        node.next = None  # this will be updated to it's previous node.
        return rest 
    
    def reverse_each_k_items(self, curr, lastBlockEnd, k):
        if not curr:
            return None

        i = 0 
        end = curr
        prev = None
        # reverse k nodes starting from curr.
        while(i < k):
            if not curr:
                break
            next = curr.get_next()
            curr.set_next(prev)
            prev = curr
            curr = next
            i +=1

        if lastBlockEnd:
            lastBlockEnd.set_next(prev)
        else:
            # first K sets.Head is no more the first one, head is the kth one.
            self.head = prev
        self.reverse_each_k_items(curr, end, k)


if __name__=="__main__":
    pg = PlayGround([random.randint(x, x+100) for x in range(10, 20)])
    pg.traverse()
    pg.nth_node_from_end(3)
    # pg.reverse_list()
    
    ll = PlayGround([1,2,3,4,5,6,7,8,9,10])
    ll.traverse()
    ll.reverse_each_k_items(ll.head, None, 2)
    ll.traverse()

    # sorted_list = PlayGround()
    # sorted_list.insert_in_a_sorted_list(10)
    # sorted_list.insert_in_a_sorted_list(1)
    # sorted_list.insert_in_a_sorted_list(3)
    # sorted_list.insert_in_a_sorted_list(21)
    # sorted_list.insert_in_a_sorted_list(15)
    # sorted_list.traverse()
