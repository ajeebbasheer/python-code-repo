class Node:
    def __init__(self, data):
        self.data = data
        self.left = None
        self.right = None
    

class BST:
    def __init__(self):
        self.root = None

    def inorder(self, root):
        if root is None:
            return
        self.inorder(root.left)
        print(f"{root.data} => ", end="")
        self.inorder(root.right)
    
    def preorder(self, root):
        if root is None:
            return
        
        print(f"{root.data} => ", end="")
        self.preorder(root.left)
        self.preorder(root.right)

    def insert(self, root, data):
        if root is None:
            node = Node(data)
            # we need to save root of the tree.
            # otherwise, we need to save it on the first insert() call like
            # t.root = t.insert(t.root, 6).
            if self.root is None:
                self.root = node
            return node
    
        if root.data == data:
            return root
        elif root.data > data:
            root.left = self.insert(root.left, data)
        else:
            root.right = self.insert(root.right, data)
        
        return root

    def delete_node(self, root, data):
        if root is None:
            return
        if root.data == data:
            # CASE #1: if node to delete is a leaf, just return None.
            if root.left is None and root.right is None:
                return None

            # CASE #2: if has a single child, return that one.
            if root.left is None:
                return root.right
            if root.right is None:
                return root.left
            
            # CASE #3: if has both children, then 
            #   - either find largest element in left subtree (which won't have a right child)
            #   - or find smallest element in right subtree (which won't have a left child)
            #   - swap root.data with this node.data.
            #   - case #2 will take care of rest.
            else:
                curr = root.left
                while(curr and curr.right):
                    curr = curr.right
                root.data, curr.data = curr.data, root.data
        root.left = self.delete_node(root.left, data)
        root.right = self.delete_node(root.right, data)
        return root
        

if __name__ == "__main__":
    t = BST()
    t.insert(t.root, 10)
    t.insert(t.root, 5)
    t.insert(t.root, 3)
    t.insert(t.root, 8)
    t.insert(t.root, 7)
    t.insert(t.root, 6)
    t.insert(t.root, 9)
    t.insert(t.root, 15)
    t.inorder(t.root)
    print("")
    t.delete_node(t.root, 10)
    t.inorder(t.root)
    print("")
