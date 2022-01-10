from game import *
import random
import matplotlib.pyplot as plt
import time
import numpy as np
from sklearn.kernel_approximation import RBFSampler
from math import sqrt
import tkinter as tk
from functools import partial
import numpy as np
window = tk.Tk()
flip = {'X':'O','O':'X'}
curr = 'X'

Board = board(3)

def hash_board_r(board_matrix):
    total = 0
    k = 0
    r = len(board_matrix[0])
    for i in range(r):
        for j in range(r):
            total+= (r**k)*board_matrix[i][j]
            k+=1
    return total

class Player:
    def __init__(self,symbol,epsilon):
        self.epsilon = epsilon
        self.weighted_average = 0
        self.beta = 0.999
        self.Q = {}
        self.symbol = symbol
    
def epsilon_greedy(Q,s,epsilon):
    if np.random.random() < epsilon:
        
        return random.choice(ACTION_SPACE)

    else:
        keys = [k for k,v in Q[s].items() if v == max(Q[s].values()) and Board.board[k[0]][k[1]]==0]
        
        return random.choice(keys) if keys else random.choice(ACTION_SPACE)

player1 = Player('X',0.15)
player2 = Player('O',0.05)

gamma = 0.9
alpha = 0.1


flip_player = {player1:player2, player2:player1}
avg_winrate = {player1:[],player2:[]}
reward_other_player = {0:0,1:-1,-1:1,-0.5:-0.5} # gets the reward of other player given reward of curr player
rewards = {player1:[],player2:[]}
reward = {player1:0,player2:0}
seen_states = {}
steps = 50000
first_player1 = player2
def train(first_player,steps):
    for _ in range(steps):
       
        curr = player1
    
        s = Board.reset()
        
        
        
        print(_)
        
        rms = {player1:0,player2:0}
        states = {player1:[],player2:[]} # used to keep track of states
        steps = 0
        while Board.is_terminal(s) == False:
            steps +=1
          
            
            s_hash = hash_board_r(s)
            temp = seen_states.get(hash_board_r(s),None)
            if not temp:
                seen_states[hash_board_r(s)]=1
            else:
                seen_states[hash_board_r(s)]+=1
            if curr.Q.get(s_hash,None) is None:
                curr.Q[s_hash] = {(0,0):0,(0,1):0,(0,2):0,(1,0):0,(1,1):0,(1,2):0,(2,0):0,(2,1):0,(2,2):0}
            a = epsilon_greedy(curr.Q,s_hash,curr.epsilon)
            
            states[curr] = [hash_board_r(s),a]
           
            Board.place(curr.symbol,a) # reward curr player got
        
        
            s2 = Board.current_state()
            

            s = s2
            if curr == player1:
                
                curr = player2
            elif curr == player2:
                curr = player1
            if states[curr] != []:
                
                curr_r = Board.reward(curr.symbol)
            
                if Board.is_terminal(s2):
                    curr_target = curr_r
                    other_player = flip_player[curr] 
                    other_reward = reward_other_player[curr_r]
                    
                    if other_player.Q.get(s_hash,None) is not None:
                        other_player.Q[s_hash] = {(0,0):0,(0,1):0,(0,2):0,(1,0):0,(1,1):0,(1,2):0,(2,0):0,(2,1):0,(2,2):0}
                    
                    other_player.Q[s_hash][a]+= alpha*(other_reward - other_player.Q[s_hash][a])
                    
                    
                
                s_hash = states[curr][0]
                prev_a = states[curr][1]
                

                s2_hash = hash_board_r(s)
                if curr.Q.get(s2_hash,None) is None:
                    curr.Q[s2_hash] = {(0,0):0,(0,1):0,(0,2):0,(1,0):0,(1,1):0,(1,2):0,(2,0):0,(2,1):0,(2,2):0}
                a2 = random.choice([k for k,v in curr.Q[s2_hash].items() if v == max(curr.Q[s2_hash].values())])
                curr.Q[s_hash][prev_a] += alpha*(curr_r+gamma*curr.Q[s2_hash][a2]- curr.Q[s_hash][prev_a])
                

                states[curr] = []

train(player1,steps)


Board.reset()

player1.epsilon=0
player2.epsilon=0
Human  = player2
Board.draw_board()
print('-------------------------')
print()
curr = player1
prev_states = []
print("NUM STATES , ",len(player1.Q))
def button_pressed(button_key):
    
   
    global prev_states
    button = buttons[button_key]
    
    button['text'] = Human.symbol
    s = Board.place(Human.symbol,button_key)
    
    player_won = Board.is_terminal(Board.board)
   
    
   
    if player_won == 'X':

        print("BOT WON")
        time.sleep(3)
        Board.reset()
        for b in buttons.keys():
            buttons[b]['text'] = ''
        hash_s = hash_board_r(Board.current_state())
        if player1.Q.get(hash_s,None) is None:

                player1.Q[hash_s] = {(0,0):0,(0,1):0,(0,2):0,(1,0):0,(1,1):0,(1,2):0,(2,0):0,(2,1):0,(2,2):0}
        a = epsilon_greedy(player1.Q,hash_s,player1.epsilon)
        prev_states = [Board.current_state(),a]
        Board.place(player1.symbol,a)
        buttons[a]['text'] = player1.symbol
        
    elif player_won == 'O':
       
        print("HUMAN WON")
        time.sleep(3)
        for b in buttons.keys():
            buttons[b]['text'] = ''
        Board.reset()
        s_hash = hash_board_r(Board.current_state())
        if player1.Q.get(s_hash,None) is None:
                player1.Q[s_hash] = {(0,0):0,(0,1):0,(0,2):0,(1,0):0,(1,1):0,(1,2):0,(2,0):0,(2,1):0,(2,2):0}
        a = epsilon_greedy(player1.Q,s_hash,player1.epsilon)
        prev_states = [Board.current_state(),a]
        Board.place(player1.symbol,a)
        buttons[a]['text'] = player1.symbol
        
    elif player_won == 'D':
        print("DRAW")
        time.sleep(3)
        Board.reset()
        for b in buttons.keys():
            buttons[b]['text'] = ''
        s_hash = hash_board_r(Board.current_state())
        if player1.Q.get(s_hash,None) is None:
                curr.Q[s_hash] = {(0,0):0,(0,1):0,(0,2):0,(1,0):0,(1,1):0,(1,2):0,(2,0):0,(2,1):0,(2,2):0}
        a = epsilon_greedy(player1.Q,s_hash,player1.epsilon)
        prev_states = [Board.current_state(),a]
        Board.place(player1.symbol,a)
        buttons[a]['text'] = player1.symbol
        

    else:
        flat = hash_board_r(Board.current_state())
        print("KKKKKK ",seen_states.get(flat,None))
        s_hash  = hash_board_r(Board.current_state())
        if player1.Q.get(s_hash,None) is None:
                player1.Q[s_hash] = {(0,0):0,(0,1):0,(0,2):0,(1,0):0,(1,1):0,(1,2):0,(2,0):0,(2,1):0,(2,2):0}
        a = epsilon_greedy(player1.Q,s_hash,player1.epsilon)
        
        buttons[a]['text'] = player1.symbol
        Board.place(player1.symbol,a)
        r = Board.reward(player1.symbol)
        player_won = Board.is_terminal(Board.current_state())
        
        if player_won:
            target = r  
           

        if player_won == 'X':
            
            time.sleep(3)
            Board.reset()
            for b in buttons.keys():
                buttons[b]['text'] = ''
            s_hash  = hash_board_r(Board.current_state())
            
            if player1.Q.get(s_hash,None) is None:
                
                player1.Q[s_hash] = {(0,0):0,(0,1):0,(0,2):0,(1,0):0,(1,1):0,(1,2):0,(2,0):0,(2,1):0,(2,2):0}
            a = epsilon_greedy(player1.Q,s_hash,player1.epsilon)
            prev_states = [Board.current_state(),a]
            Board.place(player1.symbol,a)
            buttons[a]['text'] = player1.symbol
            
        elif player_won == 'O':
            print("HUMAN WON")
            time.sleep(3)
            Board.reset()
            for b in buttons.keys():
                buttons[b]['text'] = ''
            s_hash  = hash_board_r(Board.current_state())
            if player1.Q.get(s_hash,None) is None:
                player1.Q[s_hash] = {(0,0):0,(0,1):0,(0,2):0,(1,0):0,(1,1):0,(1,2):0,(2,0):0,(2,1):0,(2,2):0}
            a = epsilon_greedy(player1.Q,s_hash,player1.epsilon)    
            prev_states = [Board.current_state(),a]    
            Board.place(player1.symbol,a)
            buttons[a]['text'] = player1.symbol
        
        elif player_won == 'D':
            print("DRAW")
            time.sleep(3)
            Board.reset()
            for b in buttons.keys():
                buttons[b]['text'] = ''
            
            s_hash  = hash_board_r(Board.current_state())
            if player1.Q.get(s_hash,None) is None:
                player1.Q[s_hash] = {(0,0):0,(0,1):0,(0,2):0,(1,0):0,(1,1):0,(1,2):0,(2,0):0,(2,1):0,(2,2):0}
            a = epsilon_greedy(player1.Q,s_hash,player1.epsilon) 
            prev_states = [Board.current_state(),a]
            Board.place(player1.symbol,a)
            buttons[a]['text'] = player1.symbol
        
        
    
one = tk.Button(text='',width=25,height=5,command=partial(button_pressed, (0,0)))
two = tk.Button(text='',width=25,height=5,command=partial(button_pressed, (0,1)))
three = tk.Button(text='',width=25,height=5,command=partial(button_pressed, (0,2)))
four = tk.Button(text='',width=25,height=5,command=partial(button_pressed, (1,0)))
five = tk.Button(text='',width=25,height=5,command=partial(button_pressed, (1,1)))
six = tk.Button(text='',width=25,height=5,command=partial(button_pressed, (1,2)))
seven = tk.Button(text='',width=25,height=5,command=partial(button_pressed, (2,0)))
eight = tk.Button(text='',width=25,height=5,command=partial(button_pressed, (2,1)))
nine = tk.Button(text='',width=25,height=5,command=partial(button_pressed, (2,2)))
buttons = {(0,0):one,(0,1):two,(0,2):three,(1,0):four,(1,1):five,(1,2):six,(2,0):seven,(2,1):eight,(2,2):nine}
# greeting.pack()
one.grid(row=0,column=0)
two.grid(row=0,column=1)
three.grid(row=0,column=2)
four.grid(row=1,column=0)
five.grid(row=1,column=1)
six.grid(row=1,column=2)
seven.grid(row=2,column=0)
eight.grid(row=2,column=1)
nine.grid(row=2,column=2)
s = hash_board(Board.current_state())
s_hash  = hash_board_r(Board.current_state())

a = epsilon_greedy(curr.Q,s_hash,curr.epsilon)
prev_states = [s,a]
Board.place(curr.symbol,a)
buttons[a]['text'] = curr.symbol




window.mainloop()
