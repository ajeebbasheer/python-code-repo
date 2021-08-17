class Node:
    def __init__(self, data):
        self.data = data
        self.left = self.right = None
    
    def __str__(self):
        return self.data
    
class Bst:
    def __init__(self, root=None):
        self.root = root
    
    def preorder(self, root):
        if not root:
            return
            
        print(root.data, end='=> ')
        
        if root.left:
            self.preorder(root.left)
        if root.right:
            self.preorder(root.right)
            
    def insert(self, root, key):
        if not root:
            return Node(key)
        if root.data > key:
            root.left = self.insert(root.left, key)
        else:
            root.right = self.insert(root.right, key)
        return root
       
    def delete(self, root, key):
        # if tree is empty, return None
        if root is None:
            return
        
        # found node.
        if root.data == key:
            # Case #1: node to delete is a leaf.
            if root.left is None and root.right is None:
                return None
                
            # Case #2: node has one child
            if root.left:
                return root.right
            if root.right:
                return root.left
            
            # Case #3: root has both children.
            temp = root.left
            while temp and temp.right:
                temp = temp.right
            
            temp.data, root.data = root.data, temp.data
        
        root.left = self.delete(root.left, key)
        root.right = self.delete(root.right, key)
        return root
            
    def __str__(self):
        return self.preorder(self.root)
    
    
if __name__ == '__main__':
    bst = Bst()
    bst.preorder(bst.root)
    bst.preorder(bst.root)
    bst.root = bst.insert(bst.root, 10)
    bst.insert(bst.root, 5)
    bst.insert(bst.root, 25)
    bst.preorder(bst.root)
    bst.delete(bst.root, 5)
    bst.preorder(bst.root)
