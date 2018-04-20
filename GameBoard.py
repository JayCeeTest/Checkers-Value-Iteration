"""0 - white square, 1- blue square, 3- p1 (green player), 2-p2 (red player)
   5- p1 (green) queen, 4- p2 (red) queen
"""


class CheckersBoard(object):
    def __init__(self):
        self.n_rows = 8
        self.n_cols = 8
        self.board_config = self.initialize_board()  # format - list of ((i,j), val)
        self.place_red_pieces()
        self.place_green_pieces()
        self.occupied_states = {}
        self.next_configs = []
        self.queen_capture_flag = False  #

    def initialize_board(self):
        board_squares = []  # the effective squares in the board
        for i in range(self.n_rows):
            for j in range(self.n_cols):
                if ((i % 2 == 0) and (j % 2 == 0)) or ((i % 2 != 0)and(j % 2 != 0)):
                    continue
                board_squares.append([(i, j), 0])
        return board_squares

    def place_red_pieces(self):
        # the value 2 indicates the presence of red pieces on the square
        for i in range(12):
            self.board_config[i][1] = 3

    def place_green_pieces(self):
        total_pos = int((self.n_rows * self.n_cols)/2)
        for i in range(12):
            self.board_config[total_pos-i-1][1] = 2

    def apply_queen(self, configs):
        # given a list of next possible configurations, this function checks if a queen can be made
        total_pos = int((self.n_rows * self.n_cols) / 2)
        for i in range(len(configs)):
            conf = configs[i]
            for j in range(int(self.n_rows/2)):
                if conf[j][1] == 2:
                    conf[j][1] = 4
            for k in range(int(self.n_rows/2)):
                if conf[total_pos-k-1][1] == 3:
                    conf[total_pos-k-1][1] = 5

    def generate_next_board_configs(self, player):
        # given a board config and a player, this function generates all possible next configurations
        self.next_configs = []
        self.occupied_states = dict(self.board_config)
        for sq in self.board_config:
            if sq[1] != 0 and sq[1] != player +1 and sq[1] != player+3:
                if sq[1] > 3:
                    moves = list(self.check_valid_moves(sq[0], 1, sq[1])) + \
                            list(self.check_valid_moves(sq[0], 2, sq[1]))
                else:
                    moves = self.check_valid_moves(sq[0], player, 0)
                for mv in moves:
                    new_board = self.make_move(self.board_config, sq[0],sq[1],mv,sq[1])
                    self.next_configs.append(new_board)
        self.apply_queen(self.next_configs)
        return self.next_configs

    def check_valid_moves(self, c_state, player, q_val):
        # q_val = queen value (4 or 5)
        current_config_dict = dict(self.board_config)
        if player == 1:
            next_val = [(c_state[0]+1, c_state[1]-1), (c_state[0]+1, c_state[1]+1)]
            temp_val = list(filter(lambda x: 1 <= x[0] <= 6 and 1 <= x[1] <= 6, next_val))
            # temp_val filters out jump_states that are not possible
            for i in range(len(next_val)):
                try:
                    if (self.occupied_states[next_val[i]] == 2 or self.occupied_states[next_val[i]] == 4) \
                            and (next_val[i] in temp_val) and q_val != 4:
                        osv = self.occupied_states[next_val[i]]  # occupied state value (of the piece we wanna capture)
                        if i == 0:
                            jump_state = next_val[i][0]+1, next_val[i][1]-1
                        else:
                            jump_state = next_val[i][0] + 1, next_val[i][1] + 1

                        if self.occupied_states[jump_state] == 0:  # check if jump state is free or not
                            board = self.take_piece(self.board_config, c_state, current_config_dict[c_state],
                                                    jump_state,1+i,osv)
                            self.next_configs.append(board)  # board config added to existing list of configs
                    if (self.occupied_states[next_val[i]] == 3 or self.occupied_states[next_val[i]] == 5)\
                            and next_val[i] in temp_val and q_val == 4:
                        osv = self.occupied_states[next_val[i]]  # occupied state value (of the piece we wanna capture)
                        if i == 0:
                            jump_state = next_val[i][0] + 1, next_val[i][1] - 1
                        else:
                            jump_state = next_val[i][0] + 1, next_val[i][1] + 1

                        if self.occupied_states[jump_state] == 0:  # check if jump state is free or not
                            board = self.take_piece(self.board_config, c_state, current_config_dict[c_state],
                                                    jump_state, 1 + i, osv)
                            self.next_configs.append(board)  # board config added to existing list of configs
                except KeyError:
                    continue
        else:
            next_val = [(c_state[0]-1, c_state[1]-1), (c_state[0]-1, c_state[1]+1)]
            temp_val = list(filter(lambda x: 1 <= x[0] <= 6 and 1 <= x[1] <= 6, next_val))
            for i in range(len(next_val)):
                try:
                    if (self.occupied_states[next_val[i]] == 3 or self.occupied_states[next_val[i]] == 5)\
                            and next_val[i] in temp_val and q_val != 5:
                        osv = self.occupied_states[next_val[i]]
                        if i == 0:
                            jump_state = next_val[i][0] - 1, next_val[i][1] - 1
                        else:
                            jump_state = next_val[i][0] - 1, next_val[i][1] + 1
                        if self.occupied_states[jump_state] == 0:
                            board = self.take_piece(self.board_config, c_state, current_config_dict[c_state],
                                                    jump_state,3+i,osv)
                            self.next_configs.append(board)
                    if (self.occupied_states[next_val[i]] == 2 or self.occupied_states[next_val[i]] == 4) \
                            and (next_val[i] in temp_val) and q_val == 5:
                        osv = self.occupied_states[next_val[i]]
                        if i == 0:
                            jump_state = next_val[i][0] - 1, next_val[i][1] - 1
                        else:
                            jump_state = next_val[i][0] - 1, next_val[i][1] + 1
                        if self.occupied_states[jump_state] == 0:
                            board = self.take_piece(self.board_config, c_state, current_config_dict[c_state],
                                                    jump_state, 3 + i, osv)
                            self.next_configs.append(board)
                except KeyError:
                    continue
        next_val = filter(lambda x:0<=x[0]<=7 and 0<=x[1]<=7, next_val)
        next_val = filter(lambda x: current_config_dict[x] == 0, next_val)
        return next_val

    def make_move(self,i_board, old_state, o_val, new_state, n_val):
        # here _state should be a tuple and val should be the value for the square
        board = i_board[:]
        old_element_ind = board.index([old_state, o_val])
        new_element_ind = board.index([new_state, 0])
        board[old_element_ind]=[old_state,0]
        board[new_element_ind]=[new_state, n_val]
        return board

    def take_piece(self, i_board, old_state, o_val, new_state, dir, osv):
        board = i_board[:]
        old_element_ind = board.index([old_state, o_val])
        new_element_ind = board.index([new_state, 0])
        try:
            if dir == 1:
                taken_piece_state = (old_state[0]+1, old_state[1]-1)
                taken_piece_ind = board.index([taken_piece_state,osv])  # taking player 2's piece
            elif dir == 2:
                taken_piece_state = (old_state[0] + 1, old_state[1] + 1)
                taken_piece_ind = board.index([taken_piece_state, osv])
            elif dir == 3:
                taken_piece_state = (old_state[0] - 1, old_state[1] - 1)
                taken_piece_ind = board.index([taken_piece_state, osv])  # taking p1's piece
            else:
                taken_piece_state  = (old_state[0] - 1, old_state[1] + 1)
                taken_piece_ind = board.index([taken_piece_state, osv])
            board[old_element_ind] = [old_state, 0]
            board[new_element_ind] = [new_state, o_val]
            board[taken_piece_ind] = [taken_piece_state, 0]
        except KeyError:
            pass
        return board


if __name__ == "__main__":
    s = CheckersBoard()
    print(s.generate_next_board_configs(1))
    print(s.generate_next_board_configs(2))
