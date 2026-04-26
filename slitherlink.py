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

# ── SlitherlinkState ──────────────────────────────────────────────────────────

class SlitherlinkState:
    state_id = 0


    def __init__(self, board, h_edges, v_edges):
        self.board = board
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
            adjacents.append(self.board[row-1][column])
        if row < self.rows - 1:
            adjacents.append(self.board[row + 1][column])
        if column > 0:
            adjacents.append(self.board[row][column - 1])
        if column < self.columns - 1:
            adjacents.append(self.board[row][column + 1])
        return adjacents

    def get_cell_edges(self, row:int, column:int) -> list:
        """Devolve os arestas da célula enviada no argumento"""
        """perguntar dps aos stores como é a melhor forma de aplicar as edges"""
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
        


    @staticmethod
    def parse_instance():
        """Lê o test do standard input (stdin) que é passado como argumento
        e retorna uma instância da classe Board.

        Por exemplo:
            $ python3 pipe.py < test-01.txt

            > from sys import stdin
            > line = stdin.readline().split()
        """
        lines = stdin.readlines()
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
        # TODO
        pass


    def actions(self, state: SlitherlinkState):
        """Retorna uma lista de ações que podem ser executadas a
        partir do estado passado como argumento."""
        # TODO
        pass


    def result(self, state: SlitherlinkState, action):
        """Retorna o estado resultante de executar a 'action' sobre
        'state' passado como argumento. A ação a executar deve ser uma
        das presentes na lista obtida pela execução de
        self.actions(state)."""
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







