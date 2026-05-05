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


    def __init__(self, h_edges, v_edges, h_value = None):
        self.id = SlitherlinkState.state_id
        SlitherlinkState.state_id += 1
        self.h_edges = h_edges
        self.v_edges = v_edges
        self.h_value = h_value

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



    def in_bounds(self, kind: str, r: int, c: int) -> bool:
        """Verifica se as coordenadas (r, c) estão dentro dos limites do tabuleiro, dependendo do tipo."""
        if kind == 'cell':
            r_valid = 0 <= r < self.rows
            c_valid = 0 <= c < self.columns
            return r_valid and c_valid
        elif kind == 'h_edge':
            r_valid = 0 <= r <= self.rows
            c_valid = 0 <= c < self.columns
            return r_valid and c_valid
        elif kind == 'v_edge':
            r_valid = 0 <= r < self.rows
            c_valid = 0 <= c <= self.columns
            return r_valid and c_valid
        elif kind == 'vertex':
            r_valid = 0 <= r <= self.rows
            c_valid = 0 <= c <= self.columns
            return r_valid and c_valid
        else:
            raise ValueError


    def adjacent_cell(self, cell:tuple) -> list:
        """Devolve uma lista das células que fazem
        fronteira com a célula enviada no argumento"""
        row, column =  cell
        adjacents = []
        if self.in_bounds('cell', row - 1, column):
            adjacents.append((self.board[row-1][column], row - 1, column))
        if self.in_bounds('cell', row + 1, column):
            adjacents.append((self.board[row + 1][column], row + 1, column))
        if self.in_bounds('cell', row, column - 1):
            adjacents.append((self.board[row][column - 1], row, column - 1))
        if self.in_bounds('cell', row, column + 1):
            adjacents.append((self.board[row][column + 1], row, column + 1))
        return adjacents

    def get_cell_edges(self, row:int, column:int) -> list:
        """Devolve os arestas da célula enviada no argumento"""
        if not self.in_bounds('cell', row, column):
            raise ValueError
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

    def get_vertex_status(self, state: SlitherlinkState, r_v: int, c_v: int):
        """Recebe as coordenadas de um vértice (r_v, c_v) e devolve (ativas, livres)."""
        active = 0
        free = 0

        if self.in_bounds('v_edge', r_v - 1, c_v):
            val = state.v_edges[r_v - 1][c_v]
            if val == 1: active += 1
            elif val == 0: free += 1

        if self.in_bounds('v_edge', r_v, c_v):
            val = state.v_edges[r_v][c_v]
            if val == 1: active += 1
            elif val == 0: free += 1

        if self.in_bounds('h_edge', r_v, c_v - 1):
            val = state.h_edges[r_v][c_v - 1]
            if val == 1: active += 1
            elif val == 0: free += 1

        if self.in_bounds('h_edge', r_v, c_v):
            val = state.h_edges[r_v][c_v]
            if val == 1: active += 1
            elif val == 0: free += 1

        return active, free

    def is_ok_active(self, state: SlitherlinkState, edge: tuple):
        """Verifica se é seguro ativar esta aresta."""
        type, r_edge, c_edge = edge

        if type == 'V' and state.v_edges[r_edge][c_edge] != 0:
            return False
        if type == 'H' and state.h_edges[r_edge][c_edge] != 0:
            return False
        
        if type == 'V':
            r_v1, c_v1 = r_edge, c_edge
            r_v2, c_v2 = r_edge + 1, c_edge
        else:
            r_v1, c_v1 = r_edge, c_edge
            r_v2, c_v2 = r_edge, c_edge + 1

        active_v1, free_v1 = self.get_vertex_status(state, r_v1, c_v1)
        active_v2, free_v2 = self.get_vertex_status(state, r_v2, c_v2)


        if active_v1 == 2 or active_v2 == 2:
            return False

        if (active_v1 == 0 and free_v1 == 1) or (active_v2 == 0 and free_v2 == 1):
            return False

        
        if type == 'V':
            # Existe esquerda? Se sim verfica se o limite dessa celula ja foi alcançado
            is_left = True
            if self.in_bounds('cell', r_edge, c_edge - 1):
                is_left = not self.is_limit_reached(state, r_edge, c_edge - 1)
            # Existe direita? Se sim verfica se o limite dessa celula ja foi alcançado
            is_right = True
            if self.in_bounds('cell', r_edge, c_edge):
                is_right = not self.is_limit_reached(state, r_edge, c_edge)
            # Caso um deles não esteja ok, retorna False
            if not is_left or not is_right:
                return False
        elif type == 'H':
            #Existe cima? Se sim verfica se o limite dessa celula ja foi alcançado
            is_up = True
            if self.in_bounds('cell', r_edge - 1, c_edge):
                is_up = not self.is_limit_reached(state, r_edge - 1, c_edge)
            #Existe baixo? Se sim verfica se o limite dessa celula ja foi alcançado
            is_down = True
            if self.in_bounds('cell', r_edge, c_edge):
                is_down = not self.is_limit_reached(state, r_edge, c_edge)
            #Caso um deles não esteja ok, retorna False
            if not is_up or not is_down:
                return False

        return True
    
    def is_ok_blocked(self, state: SlitherlinkState, edge: tuple):
        """Verifica se é seguro ativar esta aresta."""
        type, r_edge, c_edge = edge

        if type == 'V' and state.v_edges[r_edge][c_edge] != 0:
            return False
        if type == 'H' and state.h_edges[r_edge][c_edge] != 0:
            return False
        
        if type == 'V':
            r_v1, c_v1 = r_edge, c_edge
            r_v2, c_v2 = r_edge + 1, c_edge
        else:
            r_v1, c_v1 = r_edge, c_edge
            r_v2, c_v2 = r_edge, c_edge + 1

        active_v1, free_v1 = self.get_vertex_status(state, r_v1, c_v1)
        active_v2, free_v2 = self.get_vertex_status(state, r_v2, c_v2)


        if (active_v1 == 1 and free_v1 == 1) or (active_v2 == 1 and free_v2 == 1):
            return False
    
        if type == 'V':
            # Existe esquerda? Se sim verifica se colocar um X a celula ainda é possivel de completar
            is_left = True
            if self.in_bounds('cell', r_edge, c_edge - 1):
                cell = self.board[r_edge][c_edge - 1]
                if cell != -1 and (self.get_unknown_edges(state, r_edge, c_edge - 1) - 1) + (self.get_active_edges(state, r_edge, c_edge - 1)) < cell:
                    is_left = False
            # Existe direita? Se sim verifica se colocar um X a celula ainda é possivel de completar
            is_right = True
            if self.in_bounds('cell', r_edge, c_edge):
                cell = self.board[r_edge][c_edge]
                if cell != -1 and (self.get_unknown_edges(state, r_edge, c_edge) - 1) + (self.get_active_edges(state, r_edge, c_edge)) < cell:
                    is_right = False
            # Caso um deles não esteja ok, retorna False
            if not is_left or not is_right:
                return False
        elif type == 'H':
            #Existe cima? Se sim verifica se colocar um X a celula ainda é possivel de completar
            is_up = True
            if self.in_bounds('cell', r_edge - 1, c_edge):
                cell = self.board[r_edge - 1][c_edge]
                if cell != -1 and (self.get_unknown_edges(state, r_edge - 1, c_edge) - 1) + (self.get_active_edges(state, r_edge - 1, c_edge)) < cell:
                    is_up = False
            #Existe baixo? Se sim verifica se colocar um X a celula ainda é possivel de completar
            is_down = True
            if self.in_bounds('cell', r_edge, c_edge):
                cell = self.board[r_edge][c_edge]
                if cell != -1 and (self.get_unknown_edges(state, r_edge, c_edge) - 1) + (self.get_active_edges(state, r_edge, c_edge)) < cell:
                    is_down = False
            # Caso um deles não esteja ok, retorna False
            if not is_up or not is_down:
                return False

        return True
    
    def total_h_value(self) -> int:
        '''Devolve a soma do valor de todas as células numeradas'''
        counter = 0
        for r in range(self.rows):
            for c in range(self.columns):
                cell = self.board[r][c]
                if cell != -1:
                    counter += cell

        return counter 
    
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
        initial = SlitherlinkState(self.h_edges, self.v_edges, h_value = self.board.total_h_value())
        super().__init__(initial)


    def actions(self, state: SlitherlinkState):
        """Retorna uma lista de ações que podem ser executadas a
        partir do estado passado como argumento."""    

        best_free_count = 5
        best_edge = None

        for r in range(self.board.rows):
            for c in range(self.board.columns):
                
                cell_value = self.board.board[r][c]
                cell_edges = self.board.get_cell_edges(r, c)

                if cell_value != -1:
                    unknown_count = self.board.get_unknown_edges(state, r, c)

                    if 0 < unknown_count < best_free_count:
                        best_free_count = unknown_count

                        for type, r_edge, c_edge in cell_edges:
                            if type == 'H' and state.h_edges[r_edge][c_edge] == 0:
                                best_edge = ['H', r_edge, c_edge]
                                break
                            elif type == 'V' and state.v_edges[r_edge][c_edge] == 0:
                                best_edge = ['V', r_edge, c_edge]
                                break
        
        if best_edge is None:
            for r in range(self.board.rows + 1):
                for c in range(self.board.columns + 1):
                    if c < self.board.columns and state.h_edges[r][c] == 0:
                        best_edge = ['H', r, c]
                        break
                    elif r < self.board.rows and state.v_edges[r][c] == 0:   
                        best_edge = ['V', r, c]
                        break 
                if best_edge:
                    break
        
        if best_edge is None:
            return []

        actions = []

        type, r_edge, c_edge = best_edge[0], best_edge[1], best_edge[2]

        adjacent_cells = []
        if type == 'H':
            if self.board.in_bounds('cell', r_edge - 1, c_edge):
                adjacent_cells.append((r_edge - 1, c_edge))
            if self.board.in_bounds('cell', r_edge, c_edge):
                adjacent_cells.append((r_edge, c_edge))
        else:
            if self.board.in_bounds('cell', r_edge, c_edge - 1):
                adjacent_cells.append((r_edge, c_edge - 1))
            if self.board.in_bounds('cell', r_edge, c_edge):
                adjacent_cells.append((r_edge, c_edge))

        best_edge_tuple = tuple(best_edge)

        if self.board.is_ok_active(state, best_edge_tuple):
            actions.append(tuple(best_edge + [1]))
                    
        if self.board.is_ok_blocked(state, best_edge_tuple):
            actions.append(tuple(best_edge + [2]))

        return actions


    def result(self, state: SlitherlinkState, action):
        """Retorna o estado resultante de executar a 'action' sobre
        'state' passado como argumento. A ação a executar deve ser uma
        das presentes na lista obtida pela execução de
        self.actions(state)."""
        h_edges = [list(line) for line in state.h_edges]
        v_edges = [list(line) for line in state.v_edges]

        type, r_edge, c_edge, do = action
        subtract = 0

        up_cell    = self.board.board[r_edge - 1][c_edge] if self.board.in_bounds('cell', r_edge - 1, c_edge) else -1
        down_left_cell = self.board.board[r_edge][c_edge] if self.board.in_bounds('cell', r_edge, c_edge)     else -1
        right_cell = self.board.board[r_edge][c_edge - 1] if self.board.in_bounds('cell', r_edge, c_edge - 1) else -1
        
        if type == 'H':
            if do == 1:
                if (up_cell != -1 and down_left_cell == -1) or (up_cell == -1 and down_left_cell != -1):
                    subtract += 1

                elif(up_cell != -1 and down_left_cell != -1):
                    subtract += 2

            h_edges[r_edge][c_edge] = do

        if type == 'V':
            if do == 1:
                if (right_cell != -1 and down_left_cell == -1) or (right_cell == -1 and down_left_cell != -1):
                    subtract += 1
                    
                elif(right_cell != -1 and down_left_cell != -1):
                    subtract += 2

            v_edges[r_edge][c_edge] = do
            
        h_edges_state = tuple(tuple(line) for line in h_edges)
        v_edges_state = tuple(tuple(line) for line in v_edges)

        new_h_value = (state.h_value if state.h_value is not None else 0) - subtract

        print(f"Action: {action}, h_value: {new_h_value}")
        return SlitherlinkState(h_edges_state, v_edges_state, new_h_value)


    def goal_test(self, state: SlitherlinkState):
        """Retorna True se e só se o estado passado como argumento é
        um estado objetivo. Deve verificar se todas as posições do tabuleiro
        estão preenchidas de acordo com as regras do problema."""
        #verifica se cada celula tem o numero correto de arrestas ativas
        for r in range(self.board.rows):
            for c in range(self.board.columns):
                cell_value = self.board.board[r][c]
                if cell_value != -1 and cell_value != self.board.get_active_edges(state, r, c):
                    return False

        #verifica se cada vertice tem 0 ou 2 arrestas ativas, loop fechado
        act_edges_count = 0
        for r in range(self.board.rows + 1):
            for c in range(self.board.columns + 1):

                active_edges, _ = self.board.get_vertex_status(state, r, c)
                if active_edges not in (0, 2):
                    return False
                act_edges_count += active_edges

        total_active_edges = act_edges_count // 2

        #verifica se o tabuleiro não está vazio
        if total_active_edges == 0:
            return False

        #verifica se o loop para além de fechado é contínuo
        for r in range(self.board.rows + 1):
            for c in range(self.board.columns + 1):

                active_edges, _ = self.board.get_vertex_status(state, r, c)
                if active_edges == 2:
                    traveled_edges = set()
                    current_v = (r, c)

                    while True:
                        r_v, c_v = current_v
                        new_edge = None
                        next_v = None

                        if self.board.in_bounds('v_edge', r_v - 1, c_v) and state.v_edges[r_v - 1][c_v] == 1:
                            aresta = ('V', r_v - 1, c_v)
                            if aresta not in traveled_edges:
                                new_edge = aresta
                                next_v = (r_v - 1, c_v)

                        if self.board.in_bounds('v_edge', r_v, c_v) and state.v_edges[r_v][c_v] == 1:
                            aresta = ('V', r_v, c_v)
                            if aresta not in traveled_edges:
                                new_edge = aresta
                                next_v = (r_v + 1, c_v)

                        if self.board.in_bounds('h_edge', r_v, c_v - 1) and state.h_edges[r_v][c_v - 1] == 1:
                            aresta = ('H', r_v, c_v - 1)
                            if aresta not in traveled_edges:
                                new_edge = aresta
                                next_v = (r_v, c_v - 1)

                        if self.board.in_bounds('h_edge', r_v, c_v) and state.h_edges[r_v][c_v] == 1:
                            aresta = ('H', r_v, c_v)
                            if aresta not in traveled_edges:
                                new_edge = aresta
                                next_v = (r_v, c_v + 1)

                        if new_edge is not None:
                            traveled_edges.add(new_edge)
                            current_v = next_v

                        else:
                            break

                    if total_active_edges != len(traveled_edges):
                        return False
                    else:
                        return True
                    
        return False

    def h(self, node: Node):
        """Função heuristica utilizada para a procura A*."""
        #Verifica se está mais próximo de chegar a uma solução
        #cada celula contem um numero o objetivo para saber o quao 
        #proximo estamos sera comparar com as arestas ativas nessas celulas
        #ou seja uma celula 2, com 1 arresta ativa tera um valor de 2 - 1,
        #assim um tabuleiro vazio tera um erro maximo e a cada arresta numa
        #celula numerada traz o numero mais perto do objetivo
        return node.state.h_value



# ── __main__ ───────────────────────────────────────────────────────────────———

def print_official(board: Board, state: SlitherlinkState):
    for r in range(board.rows):
        linha = []
        for c in range(board.columns):
            top    = state.h_edges[r][c]
            right  = state.v_edges[r][c + 1]
            bottom = state.h_edges[r + 1][c]
            left   = state.v_edges[r][c]
            
            def normaliza(v):
                return 1 if v == 1 else 0
            
            linha.append(f"{normaliza(top)}{normaliza(right)}{normaliza(bottom)}{normaliza(left)}")
        print(" ".join(linha))

if __name__ == "__main__":
    
    board = Board.parse_instance()

    if board is None:
        print("Erro ao ler o tabuleiro.")
    else:
        initial_state = SlitherlinkState(board.h_edges, board.v_edges)
        problem = Slitherlink(board)
        solution_node = depth_first_tree_search(problem)
        if solution_node is None:
            print("Erro na solução")
        else:
            solution_state = solution_node.state
            path = solution_node.path()
            print_official(board, solution_state)
