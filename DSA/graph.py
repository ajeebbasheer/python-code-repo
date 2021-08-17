from collections import defaultdict


class Graph:
    def __init__(self):
        self.graph = defaultdict(list)
        self.added = {}
        self.vertices = 0
        
    def add_edge(self, u, v):
        self.graph[u].append(v)
        if not self.added.get(u):
            self.vertices +=1
            self.added[u] = True
            
    def BFS(self, s):
        queue = []
        visited = [False] * self.vertices
        queue.append(s)
        visited[s] = True
        while queue:
            s = queue.pop(0)
            print(s, end=' ')
            for i in self.graph[s]:
                if not visited[i]:
                    queue.append(i)
                    visited[i] = True

    
if __name__ == '__main__':
    g = Graph()
    g.add_edge(0, 1)
    g.add_edge(0, 2)
    g.add_edge(1, 2)
    g.add_edge(2, 0)
    g.add_edge(2, 3)
    g.add_edge(3, 3)
    g.BFS(2)