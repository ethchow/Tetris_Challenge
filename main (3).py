'''
 ██████╗██╗██████╗             ██████╗  ██╗███████╗██████╗  █████╗ ██████╗ ██████╗ ██████╗ 
██╔════╝██║██╔══██╗    ██╗    ██╔═████╗███║██╔════╝╚════██╗██╔══██╗╚════██╗╚════██╗╚════██╗
██║     ██║██║  ██║    ╚═╝    ██║██╔██║╚██║███████╗ █████╔╝╚█████╔╝ █████╔╝ █████╔╝ █████╔╝
██║     ██║██║  ██║    ██╗    ████╔╝██║ ██║╚════██║ ╚═══██╗██╔══██╗██╔═══╝  ╚═══██╗██╔═══╝ 
╚██████╗██║██████╔╝    ╚═╝    ╚██████╔╝ ██║███████║██████╔╝╚█████╔╝███████╗██████╔╝███████╗
 ╚═════╝╚═╝╚═════╝             ╚═════╝  ╚═╝╚══════╝╚═════╝  ╚════╝ ╚══════╝╚═════╝ ╚══════╝                                                                                       
'''

import utils
import timeit
from copy import deepcopy
#target, perfect_solution = utils.generate_target(width=200, height=200, density=0.7, forbidden_pieces={1,2,3})

#Remaps the piece orientation of the pieces into a corner, basing its first placement being the top left most corner block

piece_orientation = {
                        4:([1,0],[2,0],[2,1]),
                        5:([1,0],[1,-1],[1,-2]),    #will be referenced as coords 
                        6:([0,1],[1,1],[2,1]),      #to add to existing ones
                        7:([0,1],[0,2],[1,0]),      #allows the scoring of matrixes
                        8:([1,0],[2,0],[2,-1]),
                        9:([0,1],[0,2],[1,2]),
                        10:([0,1],[1,0],[2,0]),
                        11:([1,0],[1,1],[1,2]),
                        12:([1,0],[1,1],[2,0]),
                        13:([1,-1],[1,0],[1,1]),
                        14:([1,-1],[1,0],[2,0]),
                        15:([0,1],[0,2],[1,1]),
                        16:([0,1],[1,-1],[1,0]),
                        17:([1,0],[1,1],[2,1]),
                        18:([0,1],[1,1],[1,2]),
                        19:([1,-1],[1,0],[2,-1])
                        
    }

'''
-------------------------------------------------------------------------

▒█░░▒█ █▀▀ ░▀░ █▀▀▀ █░░█ ▀▀█▀▀ 　 █▀▀ █░░█ █▀▀▄ █▀▀ ▀▀█▀▀ ░▀░ █▀▀█ █▀▀▄ 
▒█▒█▒█ █▀▀ ▀█▀ █░▀█ █▀▀█ ░░█░░ 　 █▀▀ █░░█ █░░█ █░░ ░░█░░ ▀█▀ █░░█ █░░█ 
▒█▄▀▄█ ▀▀▀ ▀▀▀ ▀▀▀▀ ▀░░▀ ░░▀░░ 　 ▀░░ ░▀▀▀ ▀░░▀ ▀▀▀ ░░▀░░ ▀▀▀ ▀▀▀▀ ▀░░▀

This weight function makes an empty set in order to create a weighted matrix, in which blocks are given a score based on how many
neighbours they contain. If the square to its left, right, above, or below contains a 1 it adds one to its score.

-------------------------------------------------------------------------
'''
def weight(target):
    weighted_matrix = []
    for s in target:
        b = []
        for c in s:
            b.append(0)             
        weighted_matrix.append(b)
    for row,rc in enumerate(target):                               #enumerate helps to assign an index to an iterable object
        for col,cc in enumerate(rc):                               #in which case is ideal
            if cc == 1:
                if row-1 >= 0:
                    if target[row-1][col] == 1:
                        weighted_matrix[row][col] += 1
                if col-1 >= 0:
                    if target[row][col-1] == 1:
                        weighted_matrix[row][col] += 1
                if row+1 < len(target):
                    if target[row+1][col] == 1:
                        weighted_matrix[row][col] += 1
                if col+1 < len(target[0]):
                    if target[row][col+1] == 1:
                        weighted_matrix[row][col] += 1
            else:
                continue
    return weighted_matrix

'''
-----------------------------------------------------------------------------------------

▀█░█▀ █▀▀█ █░░ ░▀░ █▀▀▄ ░▀░ ▀▀█▀▀ █░░█ 　 █▀▀ █░░█ █▀▀▄ █▀▀ ▀▀█▀▀ ░▀░ █▀▀█ █▀▀▄ 
░█▄█░ █▄▄█ █░░ ▀█▀ █░░█ ▀█▀ ░░█░░ █▄▄█ 　 █▀▀ █░░█ █░░█ █░░ ░░█░░ ▀█▀ █░░█ █░░█ 
░░▀░░ ▀░░▀ ▀▀▀ ▀▀▀ ▀▀▀░ ▀▀▀ ░░▀░░ ▄▄▄█ 　 ▀░░ ░▀▀▀ ▀░░▀ ▀▀▀ ░░▀░░ ▀▀▀ ▀▀▀▀ ▀░░▀

The validity function bases its choice on a greedy alogirthm. It uses a scoring system, in which the valid pieces are accepted and then compared to one another.
The piece with the lowest score is chosen as the desired piece and it is changed into the desired tuple. 

-----------------------------------------------------------------------------------------
'''

def validity(weighted_matrix, target, row, col, count):    
    order = []
    best_piece_coord = []    
    best_piece = [100,0]
    for piece in piece_orientation:
        weight = 0
        order.clear()
        order = [(row, col)]
        for coord in piece_orientation[piece]:
            y1,x1 = coord
            y1 += row
            x1 += col           
            if y1 >= len(target) or x1 >= len(target[0]) or x1 <= 0 or y1 <= 0:               #boundary check of the piece
                break
            if type(weighted_matrix[y1][x1]) is not tuple:                    
                if weighted_matrix[y1][x1] >= 1:
                    weight += weighted_matrix[y1][x1]
                    order.append((y1,x1))
            if len(order) == 4:                     
                if weight > best_piece[0]:
                    order.clear()
                if weight < best_piece[0]:
                    best_piece_coord.clear()
                    best_piece_coord = order[:]                                              #takes the list in order and changes it         
                    best_piece = (weight, piece)                  
            else:
                continue
    return (best_piece[1], count), best_piece_coord                                          #returns the shapeID of the piece

'''
------------------------------------------------------------------------------------------

█░░█ █▀▀█ █▀▀▄ █▀▀█ ▀▀█▀▀ █▀▀ 　 █▀▀ █░░█ █▀▀▄ █▀▀ ▀▀█▀▀ ░▀░ █▀▀█ █▀▀▄ 
█░░█ █░░█ █░░█ █▄▄█ ░░█░░ █▀▀ 　 █▀▀ █░░█ █░░█ █░░ ░░█░░ ▀█▀ █░░█ █░░█ 
░▀▀▀ █▀▀▀ ▀▀▀░ ▀░░▀ ░░▀░░ ▀▀▀ 　 ▀░░ ░▀▀▀ ▀░░▀ ▀▀▀ ░░▀░░ ▀▀▀ ▀▀▀▀ ▀░░▀

The update function takes the co-ordinates found in the previous best solution and assigns the tuple to the co-ordinates within the weighted
matrix. It then proceeds to take 1 away from neighbouring squares based on certain conditions in order to change and edit the matrix again.'

------------------------------------------------------------------------------------------
'''
def update_func(weighted_matrix, temp_coord, temp_tup, count):   
    best_piece, count = temp_tup
    for coords in temp_coord:
        x = coords[1]  # 0 = 1st value in list 
        y = coords[0]  # 1 = 2nd value in list
        weighted_matrix[y][x] = (best_piece, count)                                       #acts as a piece placing for loop
        if x+1<len(weighted_matrix[0]):
            if type(weighted_matrix[y][x+1]) != tuple:
                if weighted_matrix[y][x+1] >= 1:
                    weighted_matrix[y][x+1] -= 1
        if x-1>=0:
            if type(weighted_matrix[y][x-1]) != tuple:                                      #basic check of pieces around the given coordinates
                if weighted_matrix[y][x-1] >= 1:                                            #so that it takes 1 away from nearest neighbouring pieces
                    weighted_matrix[y][x-1] -= 1
        if y+1<len(weighted_matrix):    
            if type(weighted_matrix[y+1][x]) != tuple:
                if weighted_matrix[y+1][x] >= 1:
                    weighted_matrix[y+1][x] -= 1
        if y-1>=0:
            if type(weighted_matrix[y-1][x]) != tuple:
                if weighted_matrix[y-1][x] >= 1:
                    weighted_matrix[y-1][x] -= 1
    return weighted_matrix

'''
------------------------------------------------------------------------------------------

█▀▄▀█ █▀▀█ ▀█░█▀ ░▀░ █▀▀▄ █▀▀▀ 　 █▀▀ █░░█ █▀▀▄ █▀▀ ▀▀█▀▀ ░▀░ █▀▀█ █▀▀▄ 
█░▀░█ █░░█ ░█▄█░ ▀█▀ █░░█ █░▀█ 　 █▀▀ █░░█ █░░█ █░░ ░░█░░ ▀█▀ █░░█ █░░█ 
▀░░░▀ ▀▀▀▀ ░░▀░░ ▀▀▀ ▀░░▀ ▀▀▀▀ 　 ▀░░ ░▀▀▀ ▀░░▀ ▀▀▀ ░░▀░░ ▀▀▀ ▀▀▀▀ ▀░░▀

The moving function allows progression to be made within the matrix. It uses a count as the position in which the block is placed and its shape ID
as a tuple. it acts as the main calling function, ensuring that squares that contain integers are used and those containing tuples are not.

------------------------------------------------------------------------------------------
'''

def moving(weighted_matrix, target):
    count = 1
    for row,rc in enumerate(weighted_matrix):
        for col,cc in enumerate(rc):                                                          
            if type(weighted_matrix[row][col]) is not tuple:                                  
                if weighted_matrix[row][col] > 0:                                            
                    temp_tup,temp_coord = validity(weighted_matrix, target, row, col, count)
                    best_piece,count = temp_tup
                    update_func(weighted_matrix, temp_coord, temp_tup, count)
                    if len(temp_coord) == 4:                                                  #providing that the temporary coordinates of the placed block are 
                        count += 1                                                            #of length 4, it adds one to the count as the blocks placement
            continue  
    return weighted_matrix

'''
-------------------------------------------------------------------------------------------

█░░ █▀▀█ █▀▀ ▀▀█▀▀ 　 █▀▀ █░░█ █▀▀ █▀▀ █░█ 　 █▀▀ █░░█ █▀▀▄ █▀▀ ▀▀█▀▀ ░▀░ █▀▀█ █▀▀▄ 
█░░ █▄▄█ ▀▀█ ░░█░░ 　 █░░ █▀▀█ █▀▀ █░░ █▀▄ 　 █▀▀ █░░█ █░░█ █░░ ░░█░░ ▀█▀ █░░█ █░░█ 
▀▀▀ ▀░░▀ ▀▀▀ ░░▀░░ 　 ▀▀▀ ▀░░▀ ▀▀▀ ▀▀▀ ▀░▀ 　 ▀░░ ░▀▀▀ ▀░░▀ ▀▀▀ ░░▀░░ ▀▀▀ ▀▀▀▀ ▀░░▀

The last check function, does a last sweep of the weighted matrix, in case any numbers slip through the processing, changing them into tuples of (0,0)
otherwise the performance file will not accept any of the numbers.

-------------------------------------------------------------------------------------------
'''
def lastcheck(M):
    for row,rc in enumerate(M):
        for col,cc in enumerate(rc):                                                        
            if type(cc) != tuple:
                M[row][col] = (0,0)
            else:
                continue
    return M

'''
-------------------------------------------------------------------------------------------
▀▀█▀▀ █▀▀ ▀▀█▀▀ █▀▀█ ░▀░ █▀▀ 　 █▀▀ █░░█ █▀▀▄ █▀▀ ▀▀█▀▀ ░▀░ █▀▀█ █▀▀▄ 
░▒█░░ █▀▀ ░░█░░ █▄▄▀ ▀█▀ ▀▀█ 　 █▀▀ █░░█ █░░█ █░░ ░░█░░ ▀█▀ █░░█ █░░█ 
░▒█░░ ▀▀▀ ░░▀░░ ▀░▀▀ ▀▀▀ ▀▀▀ 　 ▀░░ ░▀▀▀ ▀░░▀ ▀▀▀ ░░▀░░ ▀▀▀ ▀▀▀▀ ▀░░▀

The Tetris function calls the other elements within the function, returning a value M which is to be used as the solution matrix.

-------------------------------------------------------------------------------------------
'''

def Tetris(target):    
    weighted = weight(target)
    M = moving(weighted, target)
    lastcheck(M)
    return M

#M = Tetris(target)