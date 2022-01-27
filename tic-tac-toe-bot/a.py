from turtle import update
from game import *
import random
import matplotlib.pyplot as plt
import time
import numpy as np
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
        self.Q[0] = {(0,0):0,(0,1):0,(0,2):0,(1,0):0,(1,1):0,(1,2):0,(2,0):0,(2,1):0,(2,2):0} 
        
        self.returns = {}
        self.returns[0.0] = {(0,0):[1],(0,1):[1],(0,2):[1],(1,0):[1],(1,1):[1],(1,2):[1],(2,0):[1],(2,1):[1],(2,2):[1]}
def epsilon_greedy(player,s,epsilon):
    Q = player.Q
    if Q.get(s,None) is None:

        Q[s] = {(0,0):0,(0,1):0,(0,2):0,(1,0):0,(1,1):0,(1,2):0,(2,0):0,(2,1):0,(2,2):0} 
        # player.returns[s] = {(0,0):[1],(0,1):[1],(0,2):[1],(1,0):[1],(1,1):[1],(1,2):[1],(2,0):[1],(2,1):[1],(2,2):[1]}
   
    if np.random.random() < epsilon:
        
        return random.choice(ACTION_SPACE)

    else:
       
        keys = [k for k,v in Q[s].items() if v == max(Q[s].values()) and Board.board[k[0]][k[1]]==0]
            
        return keys[0] if keys else random.choice([x for x in ACTION_SPACE if Board.board[x[0]][x[1]] == 0])

player1 = Player('X',0.1)
player2 = Player('O',0.1)

gamma = 0.9
alpha = 0.001


flip_player = {player1:player2, player2:player1}
avg_winrate = {player1:[],player2:[]}
reward_other_player = {0:0,1:-1,-1:1} # gets the reward of other player given reward of curr player
rewards = {player1:[],player2:[]}
reward = {player1:0,player2:0}
seen_states = {}
steps = 1 
first_player1 = player2
def max_dict(d):
  max_val = max(d.values())
  max_keys = [key for key,val in d.items() if val == max_val]

  return random.choice(max_keys),max_val
i = 0
def play_game(player1,player2):
    global i
    # print(i)
    i+=1
    s = Board.reset()
    
    s_hash = hash_board_r(s)
    
    a = epsilon_greedy(player1,s_hash,player1.epsilon)
    p1_states = [s_hash]
    p1_rewards = []
    p1_a = [a]
    Board.place(player1.symbol,a)
    curr = player1


    
    
    a = epsilon_greedy(player2,hash_board_r(s),player2.epsilon)
    p2_states = [hash_board_r(Board.current_state())]
    p2_rewards = []
    p2_a = [a]
    Board.place(player2.symbol,a)
    while not Board.game_over():
       
        if curr == player1:
            reward = Board.reward(player1.symbol)
            p1_rewards.append(reward)

            if seen_states.get(hash_board_r(Board.current_state()),None) is None:
                seen_states[hash_board_r(Board.current_state())] = 1
            else:
                seen_states[hash_board_r(Board.current_state())] +=1
            a = epsilon_greedy(player1,hash_board_r(Board.current_state()),player1.epsilon)
            p1_states.append(hash_board_r(Board.current_state()))
            
            p1_a.append(a)
            Board.place(player1.symbol,a)
            
            
            curr = flip_player[curr]
            player_won = Board.is_terminal(Board.current_state())
       
            if player_won:
                r = Board.reward(player1.symbol)
                # print('P1 ',r)
                p2_rewards.append(reward_other_player[r])
                p1_rewards.append(r)
        else:
            
            reward = Board.reward(player2.symbol)
            p2_rewards.append(reward)

            a = epsilon_greedy(player2,hash_board_r(Board.current_state()),player2.epsilon)
            p2_states.append(hash_board_r(Board.current_state()))
            p2_a.append(a)
            Board.place(player2.symbol,a)
            player_won = Board.is_terminal(Board.current_state())
            
           
            if player_won:
                r = Board.reward(player2.symbol)
                
              
                p1_rewards.append(reward_other_player[r])
                p2_rewards.append(r)
                
            curr= flip_player[curr]
    return (p1_states,p1_a,p1_rewards,p2_states,p2_a,p2_rewards)


def update_model(player,states,actions,r,s_a):
    T = len(r)
    
    G = 0
    # print(T,len(states),r[T-1])
    reward = r[-1]
    for t in range(T-2,-1,-1):
        # G = r[t+1] + gamma*G
        # if t==T-2:
        #     print(G,r[t+1])
            
        s = states[t]
        a  = actions[t]
       
        old_q = player.Q[s][a]
        
        # player.returns[s][a].append(G)

        # player.Q[s][a] = np.mean(player.returns[s][a]) 
        player.Q[s][a]+= alpha*(gamma*reward-old_q)
        reward = player.Q[s][a]
        best_key,biggest_val = max_dict(player.Q[s])

def train(first_player,steps):
    for _ in range(steps):
        print(_)
        if _ == 10000:
            player1.epsilon = 0.15
            player2.epsilon  = 0.05
        # if (_%10 ==0):
        # player1.epsilon,player2.epsilon = player2.epsilon,player1.epsilon
        p1_s,p1_a,p1_r, p2_s,p2_a,p2_r = play_game(player1,player2)
        p1_s_a,p2_s_a = list(zip(p1_s,p1_a)), list(zip(p2_s,p2_a))
        update_model(player1,p1_s,p1_a,p1_r,p1_s_a)
        update_model(player2,p2_s,p2_a,p2_r,p2_s_a)
        # print("--------")


train(player1,20000)

print('fffffffffFFFFFFFFFFFFFFFF, ',player1.Q[0])
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
   
    r = Board.reward(player1.symbol)
    s_prev,a_prev = prev_states[0],prev_states[1]
    s2_hash = hash_board_r(Board.current_state())
    print(player1.Q.get(s2_hash,None))
    if s2_hash not in player1.Q:
        player1.Q[s2_hash] ={(0,0):0,(0,1):0,(0,2):0,(1,0):0,(1,1):0,(1,2):0,(2,0):0,(2,1):0,(2,2):0} 
    
    a2 = random.choice([k for k,v in player1.Q[s2_hash].items() if v == max(player1.Q[s2_hash].values())])
    # player1.Q[s_prev][a_prev]+= alpha*(r+gamma*curr.Q[s2_hash][a2]- curr.Q[s_prev][a_prev])
    if player_won == 'X':

        print("BOT WON")
        time.sleep(3)
        Board.reset()
        for b in buttons.keys():
            buttons[b]['text'] = ''
        hash_s = hash_board_r(Board.current_state())
        if player1.Q.get(hash_s,None) is None:

                player1.Q[hash_s] = {(0,0):0,(0,1):0,(0,2):0,(1,0):0,(1,1):0,(1,2):0,(2,0):0,(2,1):0,(2,2):0} 
        a = epsilon_greedy(player1,hash_s,player1.epsilon)
        prev_states = [hash_board_r(Board.current_state()),a]
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
                player1.Q[s_hash] ={(0,0):0,(0,1):0,(0,2):0,(1,0):0,(1,1):0,(1,2):0,(2,0):0,(2,1):0,(2,2):0} 
        a = epsilon_greedy(player1,s_hash,player1.epsilon)
        prev_states = [hash_board_r(Board.current_state()),a]
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
                curr.Q[s_hash] ={(0,0):0,(0,1):0,(0,2):0,(1,0):0,(1,1):0,(1,2):0,(2,0):0,(2,1):0,(2,2):0} 
        a = epsilon_greedy(player1,s_hash,player1.epsilon)
        prev_states = [hash_board_r(Board.current_state()),a]
        Board.place(player1.symbol,a)
        buttons[a]['text'] = player1.symbol
        

    else:
        flat = hash_board_r(Board.current_state())
        print("KKKKKK ",seen_states.get(flat,None))
        s_hash  = hash_board_r(Board.current_state())
        if player1.Q.get(s_hash,None) is None:
                player1.Q[s_hash] ={(0,0):0,(0,1):0,(0,2):0,(1,0):0,(1,1):0,(1,2):0,(2,0):0,(2,1):0,(2,2):0} 
        a = epsilon_greedy(player1,s_hash,player1.epsilon)
        prev_states = [hash_board_r(Board.current_state()),a]
        buttons[a]['text'] = player1.symbol
        Board.place(player1.symbol,a)
        r = Board.reward(player1.symbol)
        player_won = Board.is_terminal(Board.current_state())
        if player_won:
            s2_hash = hash_board_r(Board.current_state())
            if s2_hash not in player1.Q:
                player1.Q[s2_hash] = {(0,0):0,(0,1):0,(0,2):0,(1,0):0,(1,1):0,(1,2):0,(2,0):0,(2,1):0,(2,2):0} 
            a2 = random.choice([k for k,v in curr.Q[s2_hash].items() if v == max(curr.Q[s2_hash].values())])
            # player1.Q[s_prev][a_prev] += alpha*(r+gamma*curr.Q[s2_hash][a2]- curr.Q[s_prev][a_prev])
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
            a = epsilon_greedy(player1,s_hash,player1.epsilon)
            prev_states = [hash_board_r(Board.current_state()),a]
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
            a = epsilon_greedy(player1,s_hash,player1.epsilon)    
            prev_states = [hash_board_r(Board.current_state()),a]    
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
                player1.Q[s_hash] ={(0,0):0,(0,1):0,(0,2):0,(1,0):0,(1,1):0,(1,2):0,(2,0):0,(2,1):0,(2,2):0} 
            a = epsilon_greedy(player1,s_hash,player1.epsilon) 
            prev_states = [hash_board_r(Board.current_state()),a]
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

s_hash  = hash_board_r(Board.current_state())

a = epsilon_greedy(curr,s_hash,curr.epsilon)
prev_states = [s_hash,a]
Board.place(curr.symbol,a)
buttons[a]['text'] = curr.symbol




window.mainloop()
