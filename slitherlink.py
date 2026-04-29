#!/usr/bin/env python3
# slitherlink.py: Template para implementação do projeto de Inteligência Artificial 2025/2026.
# Devem alterar as classes e funções neste ficheiro de acordo com as instruções do enunciado.
# Além das funções e classes sugeridas, podem acrescentar outras que considerem pertinentes.

# Grupo 19:
# 113779 Leonor Machado
# 113931 David Vasques


import random, copy
from sys import stdin
from collections import defaultdict

import utils
from utils import *

from search import (
    Problem,
    Node,
    astar_search,
    breadth_first_tree_search,
    depth_first_tree_search,
    greedy_search,
    recursive_best_first_search,
)
# ── Coisas a Resolver ──────────────────────────────────────────────────────────

# criar o sistema de por cruzes
# ── SlitherlinkState ──────────────────────────────────────────────────────────

class SlitherlinkState:
    state_id = 0


    def __init__(self, h_edges, v_edges):
        self.id = SlitherlinkState.state_id
        SlitherlinkState.state_id += 1
        self.h_edges = h_edges
        self.v_edges = v_edges
    
    def __lt__(self, other):
        return self.id < other.id

    # TODO: outros metodos da classe


# ── Board ─────────────────────────────────────────────────────────────────────

class Board:
    """Representação interna de um tabuleiro de Slitherlink."""
    def __init__(self, board: tuple):
        self.board = board
        self.rows = len(board)
        self.columns = len(board[0])
        self.h_edges = tuple(tuple(0 for _ in range(self.columns)) for _ in range(self.rows + 1))
        self.v_edges = tuple(tuple(0 for _ in range(self.columns + 1)) for _ in range(self.rows))


    def adjacent_cell(self, cell:tuple) -> list:
        """Devolve uma lista das células que fazem
        fronteira com a célula enviada no argumento"""
        row, column =  cell
        adjacents = []
        if row > 0:
            adjacents.append((self.board[row-1][column], row - 1, column))
        if row < self.rows - 1:
            adjacents.append((self.board[row + 1][column], row + 1, column))
        if column > 0:
            adjacents.append((self.board[row][column - 1], row, column - 1))
        if column < self.columns - 1:
            adjacents.append((self.board[row][column + 1], row, column + 1))
        return adjacents

    def get_cell_edges(self, row:int, column:int) -> list:
        """Devolve os arestas da célula enviada no argumento"""
        if row < 0 or column < 0 or row >= self.rows or column >= self.columns:
            return None
        vertical_edges = [("V", row, column), ("V", row, column + 1)]
        
        horizontal_edges = [("H", row, column),("H", row + 1, column)]
        return vertical_edges + horizontal_edges
        
    def get_active_edges(self, state: SlitherlinkState, row:int, column:int) -> int:
        """Devolve o número de arestas ativas"""
        all_edges = self.get_cell_edges(row, column)
        num_active_edges = 0
        for type, r, c in all_edges:
            if type == 'V':
                if state.v_edges[r][c] == 1:
                    num_active_edges += 1
            else:
                if state.h_edges[r][c] == 1:
                    num_active_edges += 1

        return num_active_edges

    def get_unknown_edges(self, state: SlitherlinkState, row: int, column:int) -> int:
        """Devolve o número de arestas desconhecidas"""
        all_edges = self.get_cell_edges(row, column)
        num_unknown_edges = 0
        for type, r, c in all_edges:
            if type == 'V':
                if state.v_edges[r][c] == 0:
                    num_unknown_edges += 1
            else:
                if state.h_edges[r][c] == 0:
                    num_unknown_edges += 1

        return num_unknown_edges
        
    def is_limit_reached(self, state: SlitherlinkState, row: int, column: int) -> bool:
        '''Verifica se o limite de arestas ativas já foi alcançado'''
        cell = self.board[row][column]
        if cell != -1 and self.get_active_edges(state, row, column) >= cell:
            return True
        return False

        


    @staticmethod
    def parse_instance():
        """Lê o test do standard input (stdin) que é passado como argumento
        e retorna uma instância da classe Board.

        Por exemplo:
            $ python3 pipe.py < test-01.txt

            > from sys import stdin
            > line = stdin.readline().split()
        """
        if stdin.isatty():
            return None
        
        lines = stdin.readlines()

        if not lines:
            return None
        
        boardtemp = []

        for line in lines:
            cleanline = line.split()
            linelist = []

            if not cleanline:
                continue

            for char in cleanline:
                if char == '.':
                    linelist.append(-1)
                else:
                    linelist.append(int(char))
            boardtemp.append(tuple(linelist))
        
        boardtuple = tuple(boardtemp) 

        return Board(boardtuple)

    # TODO: outros metodos da classe


# ── Slitherlink ───────────────────────────────────────────────────────────────

class Slitherlink(Problem):
    def __init__(self, board: Board, gui=None):
        """O construtor especifica o estado inicial."""
        self.board = board
        self.gui = gui
        self.h_edges = board.h_edges
        self.v_edges = board.v_edges
        SlitherlinkState(self.h_edges, self.v_edges)
        # TODO
        pass 


    def actions(self, state: SlitherlinkState):
        """Retorna uma lista de ações que podem ser executadas a
        partir do estado passado como argumento."""
        #cada ação vai ser composta pela informação de onde está a arresta e o que fazer com ela
        
        for r in range(self.board.rows):
            for c in range(self.board.columns):
                
                cell_edges = self.board.get_cell_edges(r, c)
                

                for type, r_edge, c_edge in cell_edges:

                    actions = []
                    cell = self.board.get_unknown_edges(state, r_edge, c_edge)
                    
                    if type == 'H' and state.h_edges[r_edge][c_edge] == 0:

                        is_down = True
                        if r_edge < self.board.rows:
                            is_down = not self.board.is_limit_reached(state, r_edge, c_edge)

                        is_up = True
                        if r_edge > 0:
                            is_up = not self.board.is_limit_reached(state, r_edge - 1, c_edge)

                        if cell == self.board[r_edge][c_edge]:
                            actions.append(('H', r_edge, c_edge, 2))

                        if cell == self.board[r_edge - 1][c_edge]:
                            actions.append(('H', r_edge - 1, c_edge, 2))

                        if is_down and is_up:
                            actions.append(('H', r_edge, c_edge, 1))
                            return actions

                    elif type == 'V' and state.v_edges[r_edge][c_edge] == 0:

                        is_right = True
                        if c_edge < self.board.columns:
                            is_right = not self.board.is_limit_reached(state, r_edge, c_edge)

                        is_left = True
                        if c_edge > 0:
                            is_left = not self.board.is_limit_reached(state, r_edge, c_edge - 1)

                        if cell == self.board[r_edge][c_edge]:
                            actions.append(('V', r_edge, c_edge, 2))

                        if cell == self.board[r_edge][c_edge - 1]:
                            actions.append(('V', r_edge, c_edge - 1, 2))

                        if is_left and is_right:
                            actions.append(('V', r_edge, c_edge, 1))
                            return actions


        return []
    


    def result(self, state: SlitherlinkState, action):
        """Retorna o estado resultante de executar a 'action' sobre
        'state' passado como argumento. A ação a executar deve ser uma
        das presentes na lista obtida pela execução de
        self.actions(state)."""
        #if action in self.actions(state):

            # SlitherlinkState(action, action)

        # TODO
        pass

    def goal_test(self, state: SlitherlinkState):
        """Retorna True se e só se o estado passado como argumento é
        um estado objetivo. Deve verificar se todas as posições do tabuleiro
        estão preenchidas de acordo com as regras do problema."""
        # TODO
        pass

    def h(self, node: Node):
        """Função heuristica utilizada para a procura A*."""
        # TODO
        pass


# ── __main__ ───────────────────────────────────────────────────────────────———

if __name__ == "__main__":
    # TODO:
    # Ler o ficheiro do standard input,
    # Usar uma técnica de procura para resolver a instância,
    # Retirar a solução a partir do nó resultante,
    # Imprimir para o standard output no formato indicado.
    #pass
    
    board = Board.parse_instance()

    if board is None:
        print("deu merda")
    else:
        adj_cells = board.adjacent_cell((1,1))
        cell_edges = board.get_cell_edges(1,1)
        num_active_edges = board.get_active_edges(SlitherlinkState(board.board, board.h_edges, board.v_edges), 1, 1)

        print("\nBOARD:")
        print(board.board)

        print("\nADJACENT CELLS:")
        print(adj_cells)

        print("\nCELL EDGES:")
        print(cell_edges)

        print("\nNUM ACTIVE EDGES: ", num_active_edges, "\n")







