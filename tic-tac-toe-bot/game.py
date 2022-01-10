import numpy as np
from staticfg import CFGBuilder

ACTION_SPACE = [(0,0),(0,1),(0,2),(1,0),(1,1),(1,2),(2,0),(2,1),(2,2)] # place symbol in that cell
class board:
    def __init__(self,rows):
        self.rows = rows
        self.cols = rows
        self.board = np.zeros((rows,self.cols)) # 0 if its empty 1 if its X -1 if its O
        self.num_places = 0 # num of times a symbol was placed (used to check for draws efficiently)
    def reward(self,symbol):
        player_won = self.is_terminal(self.board)
        if player_won == symbol:
            reward = 1
        elif (player_won=='X' and symbol=='O') or (symbol=='X' and player_won=='O'):
            reward = -1
            
        elif player_won == 'D':
            reward = 0
        else:
            reward = 0
        return reward
    def place(self,symbol,place):
        
        encode_string = {'X':1,'O':-1}
        if self.board[place[0]][place[1]] == 0:
            self.num_places+=1
            self.board[place[0]][place[1]] = encode_string[symbol]
            player_won = self.is_terminal(self.board)
            
            
            if player_won == symbol:
                reward = 1
            elif (player_won=='X' and symbol=='O') or (symbol=='X' and player_won=='O'):
                reward = -1
                
            elif player_won == 'D':
                reward = 0
            else:
                reward = 0
            return reward
        return 0
    def is_terminal(self,board):
        deconde_int = {1:'X',-1:'O',0:''}

        if self.num_places <self.rows: # no point in checking the first N times 
            return False
        # check the for rows and cols
        for row in range(self.rows):
            total_row = sum(board[row])
            
            total_col = sum(board[:,row])
            if total_row==self.rows or total_col==self.rows: # player X won
                return 'X'
            elif total_row==-self.rows or total_col==-self.rows:
                return 'O'
        # check diagonal
        total = sum(board.diagonal())
        if total==self.rows:
            return 'X'
        elif total==-self.rows:
            return 'O'
        
        total = sum(np.flipud(board).diagonal()) # right diagonal
        if total==self.rows:
            return 'X'
        elif total==-self.rows:
            return 'O'
        # check for draw
        if  self.num_places == self.rows**2:
            return 'D'
        else:
            return False
    def game_over(self):
        return self.is_terminal(self.board)==False
    def draw_board(self):
        deconde_int = {1:'X',-1:'O',0:''}
        temp = [[] for _ in range(self.rows)]
        for i in range(self.rows):
            for j in range(self.cols):
                temp[i].append(deconde_int[self.board[i][j]])

            print(temp[i])
            print()
    def all_states(self):
        states = []
        
    def reset(self):
        self.board = np.zeros((self.rows,self.cols))
        self.num_places = 0
        return self.board
    def current_state(self):
        return self.board


# Board = board(3)
# Board.board = np.array([
#                         [-1,1,-1],
#                         [1,-1,-1],
#                         [-1,0,1]])
# print(Board.is_terminal(Board.board))
# Board.draw_board()