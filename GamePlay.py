from GameBoard import CheckersBoard
import random
import math
from ast import literal_eval as make_tuple
# random.seed(1)


class Game(object):
    def __init__(self):
        self.p = 1  # Player 1's turn to play
        self.game_board = CheckersBoard()
        self.grid_states = [self.board_to_grid_converter(self.game_board.board_config)]
        self.explored_game_states = self.generate_possible_states()
        self.custom_states = {}  # we will use these for value iteration
        self.visited_states={}  # states in which actions were taken
        self.time_step_reward = -0.5
        self.draw_reward = 0
        self.win_reward = 100
        self.lose_reward = -100
        self.gamma = 0.9  # discount - arbitrary choice for gamma
        self.prob = 1  # p(s',r| s, a)

    def save_values_to_text_file(self):
        with open("value_ouputs.txt", "w") as f:
            for k in self.explored_game_states:
                f.write(str(k) + "-->" + str(self.explored_game_states[k]) + "\n")

    def load_values_from_text(self):
        with open("value_ouputs.txt", "r") as f:
            for line in f:
                k,v = line.split("-->")
                self.explored_game_states[make_tuple(k)] = float(v)
        # print(self.custom_states)

    def convert_to_board_state(self, stor_state):
        board_squares = []  # the effective squares in the board
        k=0
        for i in range(8):
            for j in range(8):
                if ((i % 2 == 0) and (j % 2 == 0)) or ((i % 2 != 0) and (j % 2 != 0)):
                    continue
                board_squares.append([(i, j), stor_state[k]])
                k+=1
        return board_squares

    def convert_to_storage_state(self, board_state):
        # this function converts a board config into an effient format storage
        return tuple(dict(board_state).values())

    def convert_to_game_state(self, store_state, p=1):
        # given a store state, convert to game state definition to deal with large state space
        """ returns n0- num of own uncrowned-pieces, n1- num of opponent uncrowned pieces
                    n2- num of own queens, n3- num of opponent queens
        """
        n0 = store_state.count(3)
        n1 = store_state.count(2)
        n2 = store_state.count(5)
        n3 = store_state.count(4)

        return n0, n1, n2, n3

    #  --> method did not work, too many states... look at later
    # def generate_all_possible_states(self):
    #     """This method generates all possible states that could be encountered in the full game of checkers.
    #        Since iterating over the whole state space would be insane, just have to find states that are more likely
    #        to be encountered
    #     """
    #     raw_init_state = self.game_board.board_config  # init state before conversion
    #     current_state = self.convert_to_storage_state(raw_init_state)
    #     if current_state not in self.explored_game_states:
    #         self.explored_game_states[current_state] = 0
    #     opponent_states = self.game_board.generate_next_board_configs(1)  # possible states after we play
    #     if len(opponent_states) == 0: return  # base case
    #     for os in opponent_states:
    #         self.game_board.board_config = os  # set the board config to the current one for the opponent
    #         next_states = self.game_board.generate_next_board_configs(2)  # possible states after opponent plays
    #         next_states = list(filter(lambda x: self.convert_to_storage_state(x) not in self.explored_game_states,
    #                              next_states))  # only keep those states we want
    #         for s in next_states:
    #             state_store = self.convert_to_storage_state(s)  # convert state to storage format
    #             self.explored_game_states[state_store] = 0
    #             self.game_board.board_config = s
    #             self.generate_all_possible_states()
    #     return

    def generate_possible_states(self):
        # a - number of own pieces, b - number of opponent's pieces
        # c - number of own queens, d - number of opponent's queens
        # e - number of own corner pieces
        possible_states = [((a, b, c, d), 0) for a in range(13) for b in range(13)
                           for c in range(13) for d in range(13)]
        return dict(list(filter(lambda x: sum(x[0]) <= 24, possible_states)))

    def generate_next_states(self, s, a):
        # 0 - my own pieces, 1 - opponent's pieces, 2 - my own queens, 3 - opponent queens
        # a is the action, 0 - move, 1 - capture, 2 - crown, 3 - capture and crown
        opponent_states = [(s[0], s[1], s[2], s[3]), (s[0], s[1]-1, s[2], s[3]),
                           (s[0]-1, s[1], s[2]+1, s[3]), (s[0]-1, s[1]-1, s[2]+1, s[3])]
        nos = opponent_states[a]  # The opponent's state after action a was taken
        for v in nos:
            if not 0 <= v <= 12:
                return []  # taking an action in that state is not possible
        my_next_states = [(nos[0], nos[1], nos[2], nos[3]), (nos[0]-1, nos[1], nos[2], nos[3]),
                          (nos[0], nos[1]-1, nos[2], nos[3]+1), (nos[0]-1, nos[1]-1, nos[2], nos[3]+1)]
        return list(filter(lambda x: 0 <= x[0] <= 12 and 0 <= x[1] <= 12 and
                                     0 <= x[2] <= 12 and 0 <= x[3] <= 12, my_next_states))

    def action_taken(self, s1, s2):
        # given 2 state transitions, find out which action was taken from that state
        if s1 == s2:  # action was a move
            a = 0
        elif s2 == (s1[0], s1[1]-1, s1[2], s1[3]):  # action was a capture
            a = 1
        elif s2 == (s1[0]-1, s1[1], s1[2]+1, s1[3]):  # action was crowning
            a = 2
        else:  # action was capture and crown
            a = 3
        return a

    def value_iteration(self):
        # state_ = self.convert_to_game_state(self.convert_to_storage_state(self.game_board.board_config))
        # init_state = (0, 1, 2, 2)
        eps = 0.0001  # This is our convergence criteria
        while True:
            converged = True  # First set converged to True, make it false when epsilon does not converge
            for state_ in self.explored_game_states:  # iterate over all the state
                v = self.explored_game_states[state_]  # current value for the state
                actions = (0, 1, 2, 3)  # possible actions, see action_taken function for more details
                q_values = []
                for a in actions:
                    next_states = self.generate_next_states(state_, a)
                    if len(next_states) == 0:
                        continue
                    else:
                        q = self.compute_q_values(a, next_states)
                    q_values.append(q)
                new_v = max(q_values)
                self.explored_game_states[state_] = new_v
                if abs(v-new_v) > eps:
                    converged = False
            if converged:
                break
        self.save_values_to_text_file()

    def compute_q_values(self, a, s_primes):
        # assume an equiprobable p(s',r|s,a) val -- random agent
        prob = 1.0/len(s_primes)
        q_val = 0
        for s in s_primes:
            if self.is_terminal(s):  # s is a terminal state
                q_val = self.reward_function(s)
            else:
                q_val += prob*(self.reward_function(s) + self.gamma*self.explored_game_states[s])
        return q_val

    def is_terminal(self, state):
        if (state[0] == 0 and state[2] == 0) or (state[1] == 0 and state[3] == 0):
            return True
        return False

    def reward_function(self, state):
        if state[0] == 0 and state[2] == 0:
            # p1 lost the game
            return self.lose_reward
        elif state[1] == 0 and state[3] == 0:
            # p1 won the game
            return self.win_reward
        else:
            return self.time_step_reward

    def enlightened_agent(self):
        # RL Agent that plays based on the value iteration algorithm
        moves = self.game_board.generate_next_board_configs(self.p)
        move_values = []
        if len(moves) == 0:
            return None
        for m in moves:
            m_stored = self.convert_to_storage_state(m)
            m_stored_c = self.convert_to_game_state(m_stored)
            #  if m_stored_c in self.explored_game_states:
            move_values.append(self.explored_game_states[m_stored_c])
            #  else:
            #    move_values.append(0)
        return moves[move_values.index(max(move_values))]

    def random_agent(self):
        moves =self.game_board.generate_next_board_configs(self.p)
        if len(moves) == 0:
            return None
        move = random.choice(moves)
        return move

    def play_game(self):
        # simulates the game playing process
        # right now we are playing a random vs an RL agent
        self.game_board = CheckersBoard()
        current_config = self.enlightened_agent()
        count = 0
        while True:
            count+=1
            if current_config is None:
                break
            self.game_board.board_config = current_config
            self.grid_states.append(self.board_to_grid_converter(current_config))
            if self.p == 1:
                self.p = 2
                current_config = self.random_agent()
            else:
                self.p = 1
                current_config = self.enlightened_agent()
            if count>5000:
                break

    def board_to_grid_converter(self, board):
        # given an input board, converts it into a format suitable for the visualisation module
        board_map = dict(board)
        result_grid = [[1 for m in range(8)] for n in range(8)]
        for i in range(self.game_board.n_rows):
            for j in range(self.game_board.n_cols):
                if ((i % 2 == 0) and (j % 2 == 0)) or ((i % 2 != 0) and (j % 2 != 0)):
                    result_grid[i][j] = 0
                if (i, j) in board_map:
                    if board_map[(i,j)] != 0:
                        result_grid[i][j] = board_map[(i,j)]
        return result_grid

if __name__ == "__main__":
    g = Game()
    g.value_iteration()
    # g.load_values_from_text()
    # g.play_game()
    # print(g.convert_to_custom_state(g.convert_to_storage_state(g.game_board.board_config)))

