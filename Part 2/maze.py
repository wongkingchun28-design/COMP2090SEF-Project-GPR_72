import random


class DisjointSetDataStructure:
    def __init__(self, n):
        self.parent = list(range(n))

    def find(self, a ):
        if self.parent[a] == a:
            return a
        self.parent[a] = self.find(self.parent[a])
        return self.parent[a]
    
    def union(self, a, b):
        root_a = self.find(a)
        root_b = self.find(b)
        if root_a != root_b:
            self.parent[root_a] = root_b
            return True
        else:
            return False

def CreateMaze(width,height):

    maze = {(x, y): 1 for y in range(height) for x in range(width)}
    rows, cols = height // 2, width // 2
    UnionFind = DisjointSetDataStructure(width * height)

    walls = []
    for c in range(cols):
            for r in range(rows):
                if c + 1 < cols:
                    walls.append(((c, r), (c + 1, r), (c * 2 + 2, r * 2 + 1)))
                if r + 1 < rows:
                    walls.append(((c, r), (c, r + 1), (c * 2 + 1, r * 2 + 2)))

    random.shuffle(walls)

    for cell1, cell2, wall_pos in walls:
        id1 = cell1[1] * cols + cell1[0]
        id2 = cell2[1] * cols + cell2[0]
        if UnionFind.union(id1, id2):
            maze[(cell1[0]*2+1, cell1[1]*2+1)] = 0
            maze[(cell2[0]*2+1, cell2[1]*2+1)] = 0
            maze[wall_pos] = 0
    for x in range(width):
        maze[(x, 0)] = 1
        maze[(x, height - 1)] = 1
        
    for y in range(height):
        maze[(0, y)] = 1
        maze[(width - 1, y)] = 1
    return maze






