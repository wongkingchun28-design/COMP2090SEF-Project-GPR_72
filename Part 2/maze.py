import random


class DisjointSetDataStructure:     #Disjoint Set Data Structure for Maze Generation
    def __init__(self, n):          #n is the number of cells in the maze
        self.parent = list(range(n))    #each cell is initially its own parent

    def find(self, a ):         #Find the root of the set that a belongs to, with path compression
        if self.parent[a] == a:
            return a
        self.parent[a] = self.find(self.parent[a])
        return self.parent[a]
    
    def union(self, a, b):      #Union the sets that a and b belong to, return True if they were in different sets, False if they were already in the same set
        root_a = self.find(a)
        root_b = self.find(b)
        if root_a != root_b:
            self.parent[root_a] = root_b
            return True
        else:
            return False

def CreateMaze(width,height):       #Create a maze using randomized Kruskal's algorithm, return a dictionary with (x,y) as keys and 0 for paths and 1 for walls

    maze = {(x, y): 1 for y in range(height) for x in range(width)}     #Initialize all cells as walls, carve out paths by setting some cells to 0
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

    for cell1, cell2, wall_pos in walls:    #For each wall, if the cells it separates are in different sets, union them and remove the wall
        id1 = cell1[1] * cols + cell1[0]
        id2 = cell2[1] * cols + cell2[0]
        if UnionFind.union(id1, id2):
            maze[(cell1[0]*2+1, cell1[1]*2+1)] = 0
            maze[(cell2[0]*2+1, cell2[1]*2+1)] = 0
            maze[wall_pos] = 0
    for x in range(width):          #Add outer walls
        maze[(x, 0)] = 1
        maze[(x, height - 1)] = 1
        
    for y in range(height):         #Add outer walls
        maze[(0, y)] = 1
        maze[(width - 1, y)] = 1
    return maze





