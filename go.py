class Go:

    HANDICAPS = { 9:[(2,6),(6,2),(6,6),(2,2),(4,4)],
                 13:[(3,9),(9,3),(9,9),(3,3),(6,6),(6,3),(6,9),(3,6),(9,6)],
                 19:[(3,15),(15,3),(15,15),(3,3),(9,9),(9,3),(9,15),(3,9),(15,9)]}

    SYMBOLS  = {'black':'x',
                'white':'o'}

    # Note that the letter I is omitted from possible coordinates.
    COL_LABELS = [chr(ord('A')+i) for i in range(26) if i!=8]

    MOVES = [(1,0), (-1,0), (0,1), (0,-1)]

    def __init__(self, *args):
        
        if len(args) == 1:
            self.width, self.height = args[0], args[0]
        elif len(args) == 2:
            self.height, self.width = args
        assert self.width < 25
        self.size = {"height": self.height, "width": self.width}
          
        self.board = [['.' for w in range(self.width)] for h in range(self.height)]
        self.turn = "black"
        
        self.turn_count = 0
        self.cache = []
        self.handicap = False
    
    def _get_row_col(self, pos):
        row = self.height - int(pos[:-1])
        col = self.COL_LABELS.index(pos[-1])
        return row, col
        
    
    def get_position(self, pos):
        row, col = self._get_row_col(pos)
        assert row < self.height and col < self.width
        return self.board[row][col]
    
    def move(self, *coordinates):
        print(coordinates)
        for coordinate in coordinates:
            row, col = self._get_row_col(coordinate)
            print(coordinate, self.SYMBOLS[self.turn])
            
            # Cannot play out of bounds.
            assert row < self.height and col < self.width
            # Cannot place a stone on another stone.
            assert self.board[row][col] == '.'

            self.play_turn(row, col)
            #self.display()
            #print()
                
    def play_turn(self, row, col):
        # make a save of the board
        save = [[self.board[ri][ci] for ci in range(self.width)] for ri in range(self.height)]
        save[row][col] = self.SYMBOLS[self.turn]
        
        # check for allies and enemies near the stone
        allies, enemies = [], []
        for dr, dc in self.MOVES:
            r, c = row + dr, col + dc
            if 0<=r<self.height and 0<=c<self.width:
                if self.board[r][c] == self.SYMBOLS[self.turn]:
                    allies.append((r, c))
                else:
                    enemies.append((r, c))
                    
        # all opponent stones without liberties should be 
        # captured and removed from the board
        opp = self.idle_player()
        opp_SYMBOLS =  self.SYMBOLS[opp]
        for (r, c) in enemies:
            # is the stone not already captured ?
            if save[r][c] == opp_SYMBOLS:
        
                # check liberties
                if self._get_liberties(r, c, opp, save) == 0:
                    self.capture(r, c, opp_SYMBOLS, save)
      
        ### Check to make sure a move is valid before proceeding
        # (Suicide)
        l = self._get_liberties(row, col, self.turn, save)
        assert l, "capturing moves are illegal"
            
        #assert save != self.board, "Illegal KO move" 
        # (KO Rule)
        if self.turn_count>1:
            assert save != self.cache[-2]
        self.update_cache(save)
        
        # commit
        self.board = [[save[ri][ci] for ci in range(self.width)] for ri in range(self.height)]
        self.change_turn()
        self.turn_count += 1
        
        return True
    
    def capture(self, row, col, symbol, board):
        board[row][col] = '.' # capture
        print('captured', row, col)
        for dr, dc in self.MOVES:
            r, c = row + dr, col + dc
            if 0<=r<self.height and 0<=c<self.width and board[r][c] == symbol:
                self.capture(r, c, symbol, board)
    
    def _get_liberties(self, row, col, turn, board):
        
        def get_liberties_rec(row, col, turn, board, visit_list):
            l = 0
            for dr, dc in self.MOVES:
                r, c = row + dr, col + dc
                # cheking boundaries and if we already tested the emplacement
                if 0<=r<self.height and 0<=c<self.width and not visit_list[r][c]:
                    visit_list[r][c] = 1
                    #if the neighbor is an ally, share the lib
                    if board[r][c] == self.SYMBOLS[turn]:
                        l += get_liberties_rec(r, c, turn, board, visit_list)     
                    elif board[r][c] == '.':
                        l += 1
            return l
              
        visit_list = [[0 for i in range(self.width)] for j in range(self.height)]
        return get_liberties_rec(row, col, turn, board, visit_list)
          
    
    def handicap_stones(self, n):
        # A player cannot place down handicap stones after the first move has been made 
        # or handicap stones have already been placed. 
        assert not self.turn_count and not self.handicap
        
        # Handicap stones can only be placed on 9x9, 13x13 and 19x19 boards
        assert self.width==self.height and self.width in [9, 13, 19]
        
        stones = self.HANDICAPS[self.width]

        # Placing too many handicap stones for a given board should throw an error.
        assert n<=len(stones)

        for i in range(n):
            r, c = stones[i][0], stones[i][1]
            self.board[r][c] = self.SYMBOLS[self.turn]
        
        self.handicap = True

    def update_cache(self, board):
        self.cache.append(board)
    
    def idle_player(self):
        if self.turn == 'black':
            return 'white'
        return 'black'
        
    def change_turn(self):
        self.turn = self.idle_player()
        
    def pass_turn(self):
        # User should be able to pass their turn.
        self.update_cache(self.board)
        self.turn_count += 1
        self.change_turn()
    
    def reset(self):
        # Resetting the board should clear all of the stones from 
        # it and set the turn to "black"
        self.__init__(self, self.height, self.width)
    
    def rollback(self, n):
        # User should be able to rollback a set amount of turns on the go board.
        assert self.turn_count, "Rollback after reset raises an error"
    
        assert n <= self.turn_count, "Rollback more than amount of moves raises an error"
        # update the cache
        self.cache = self.cache[:-n]
        if n == self.turn_count:
            self.board = [['.' for w in range(self.width)] for h in range(self.height)]
        else:
            self.board = self.cache[-1]
        
        self.turn_count -= n
        if n%2:
            self.turn = self.idle_player()

    def display(self):
        print(' ',  *self.COL_LABELS[:self.width])
        for r in range(self.height):
            print(self.height-r, *self.board[r], sep=' ')