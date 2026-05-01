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
            return [] #tem que devolver um erro
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

        if r_v > 0:
            val = state.v_edges[r_v - 1][c_v]
            if val == 1: active += 1
            elif val == 0: free += 1

        if r_v < self.rows:
            val = state.v_edges[r_v][c_v]
            if val == 1: active += 1
            elif val == 0: free += 1

        if c_v > 0:
            val = state.h_edges[r_v][c_v - 1]
            if val == 1: active += 1
            elif val == 0: free += 1

        if c_v < self.columns:
            val = state.h_edges[r_v][c_v]
            if val == 1: active += 1
            elif val == 0: free += 1

        return active, free

    def is_ok_active(self, state: SlitherlinkState, edge: tuple):
        """Verifica se é seguro ativar esta aresta."""
        tipo, r_edge, c_edge = edge

        if tipo == 'V':
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

        return True
    
    def is_ok_blocked(self, state: SlitherlinkState, edge: tuple):
        """Verifica se é seguro ativar esta aresta."""
        tipo, r_edge, c_edge = edge

        if tipo == 'V':
            r_v1, c_v1 = r_edge, c_edge
            r_v2, c_v2 = r_edge + 1, c_edge
        else:
            r_v1, c_v1 = r_edge, c_edge
            r_v2, c_v2 = r_edge, c_edge + 1

        active_v1, free_v1 = self.get_vertex_status(state, r_v1, c_v1)
        active_v2, free_v2 = self.get_vertex_status(state, r_v2, c_v2)


        if (active_v1 == 1 and free_v1 == 1) or (active_v2 == 1 and free_v2 == 1):
            return False
        
        return True

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
        initial = SlitherlinkState(self.h_edges, self.v_edges)
        super().__init__(initial)



    def actions(self, state: SlitherlinkState):
        """Retorna uma lista de ações que podem ser executadas a
        partir do estado passado como argumento."""
        #cada ação vai ser composta pela informação de onde está a arresta e o que fazer com ela
        # -2 = x
        # para poder por uma cruz preciso saber:
                        #  se ao colocar vou impedir que a cell seja completa
                        #  ou seja tenho que verificar ambas as celulas da arresta
                        #  verificar se essas celulas existem existem
                        #  verificar se a celula tem um numero
        
        for r in range(self.board.rows):
            for c in range(self.board.columns):
                
                cell_edges = self.board.get_cell_edges(r, c)
                

                for type, r_edge, c_edge in cell_edges:

                    actions = []
                    
                    if type == 'H' and state.h_edges[r_edge][c_edge] == 0:

                        is_up = True
                        if r_edge > 0:
                            is_up = not self.board.is_limit_reached(state, r_edge - 1, c_edge)

                        is_down = True
                        if r_edge < self.board.rows:
                            is_down = not self.board.is_limit_reached(state, r_edge, c_edge)
                        
                        if is_down and is_up and self.board.is_ok_active(state, ('H', r_edge, c_edge)):
                            actions.append(('H', r_edge, c_edge, 1))
                        
                        is_up = True
                        if r_edge > 0:
                            cell = self.board.board[r_edge - 1][c_edge]
                            if cell != -1 and (self.board.get_unknown_edges(state, r_edge - 1, c_edge) - 1) + (self.board.get_active_edges(state, r_edge - 1, c_edge)) < cell:
                                is_up = False

                        is_down = True
                        if r_edge < self.board.rows:
                            cell = self.board.board[r_edge][c_edge]
                            if cell != -1 and (self.board.get_unknown_edges(state, r_edge, c_edge) - 1) + (self.board.get_active_edges(state, r_edge, c_edge)) < cell:
                                is_down = False

                        if is_down and is_up and self.board.is_ok_blocked(state, ('H', r_edge, c_edge)):
                            actions.append(('H', r_edge, c_edge, 2))

                        return actions

                    elif type == 'V' and state.v_edges[r_edge][c_edge] == 0:

                        is_left = True
                        if c_edge > 0:
                            is_left = not self.board.is_limit_reached(state, r_edge, c_edge - 1)

                        is_right = True
                        if c_edge < self.board.columns:
                            is_right = not self.board.is_limit_reached(state, r_edge, c_edge)

                        if is_left and is_right and self.board.is_ok_active(state, ('V', r_edge, c_edge)):
                            actions.append(('V', r_edge, c_edge, 1))

                        is_left = True
                        if c_edge > 0:
                            cell = self.board.board[r_edge][c_edge - 1]
                            if cell != -1 and (self.board.get_unknown_edges(state, r_edge, c_edge - 1) - 1) + (self.board.get_active_edges(state, r_edge, c_edge - 1)) < cell:
                                is_left = False

                        is_right = True
                        if c_edge < self.board.rows:
                            cell = self.board.board[r_edge][c_edge]
                            if cell != -1 and (self.board.get_unknown_edges(state, r_edge, c_edge) - 1) + (self.board.get_active_edges(state, r_edge, c_edge)) < cell:
                                is_right = False

                        if is_left and is_right and self.board.is_ok_blocked(state, ('V', r_edge, c_edge)):
                            actions.append(('V', r_edge, c_edge, 2))
                        
                        return actions
                    
        return []
    


    def result(self, state: SlitherlinkState, action):
        """Retorna o estado resultante de executar a 'action' sobre
        'state' passado como argumento. A ação a executar deve ser uma
        das presentes na lista obtida pela execução de
        self.actions(state)."""
        h_edges = [list(line) for line in state.h_edges]
        v_edges = [list(line) for line in state.v_edges]

        type, r_edge, c_edge, do = action
        
        if type == 'H':
            h_edges[r_edge][c_edge] = do

        if type == 'V':
            v_edges[r_edge][c_edge] = do
            
        h_edges_state = tuple(tuple(line) for line in h_edges)
        v_edges_state = tuple(tuple(line) for line in v_edges)

        return SlitherlinkState(h_edges_state, v_edges_state)


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

                        if r_v > 0 and state.v_edges[r_v - 1][c_v] == 1:
                            aresta = ('V', r_v - 1, c_v)
                            if aresta not in traveled_edges:
                                new_edge = aresta
                                next_v = (r_v - 1, c_v)

                        if r_v < self.board.rows and state.v_edges[r_v][c_v] == 1:
                            aresta = ('V', r_v, c_v)
                            if aresta not in traveled_edges:
                                new_edge = aresta
                                next_v = (r_v + 1, c_v)

                        if c_v > 0 and state.h_edges[r_v][c_v - 1] == 1:
                            aresta = ('H', r_v, c_v - 1)
                            if aresta not in traveled_edges:
                                new_edge = aresta
                                next_v = (r_v, c_v - 1)

                        if c_v < self.board.columns and state.h_edges[r_v][c_v] == 1:
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
        # TODO
        pass


# ── __main__ ───────────────────────────────────────────────────────────────———

if __name__ == "__main__":
    
    board = Board.parse_instance()

    if board is None:
        print("Erro ao ler o tabuleiro.")
    else:
        state = SlitherlinkState(board.h_edges, board.v_edges)
        problem = Slitherlink(board)

        print("\n=== A EXECUTAR TESTE DE 10 JOGADAS ===")
        estado_atual = state

        for i in range(36):
            acoes_possiveis = problem.actions(estado_atual)
            print(acoes_possiveis)
            if not acoes_possiveis:
                print(f"\nJogada {i+1}: Beco sem saída! Não há mais ações possíveis.")
                break

            acao_escolhida = acoes_possiveis[0]
            print(f"\n\n==================================================")
            print(f"--- Jogada {i+1}: A aplicar ação {acao_escolhida} ---")
            print(f"==================================================")

            estado_atual = problem.result(estado_atual, acao_escolhida)

            # ----------------------------------------------------
            # 1. FORMATO OFICIAL (TRBL)
            # ----------------------------------------------------
            print("\n> Formato de Output Oficial:")
            for r in range(board.rows):
                linha_output = []
                for c in range(board.columns):
                    top = estado_atual.h_edges[r][c]
                    right = estado_atual.v_edges[r][c + 1]
                    bottom = estado_atual.h_edges[r + 1][c]
                    left = estado_atual.v_edges[r][c]
                    cell_string = f"{top}{right}{bottom}{left}"
                    linha_output.append(cell_string)
                print(" ".join(linha_output))

            # ----------------------------------------------------
            # 2. FORMATO VISUAL (Grelha Desenhada)
            # ----------------------------------------------------
            print("\n> Formato Visual (Arestas Ativas):")
            for r in range(board.rows):
                # Imprimir as arestas HORIZONTAIS de cima desta linha
                h_line = "+"
                for c in range(board.columns):
                    if estado_atual.h_edges[r][c] == 1:
                        h_line += "---+"
                    else:
                        h_line += "   +"
                print(h_line)

                # Imprimir as arestas VERTICAIS e os números das células
                v_line = ""
                for c in range(board.columns):
                    edge = "|" if estado_atual.v_edges[r][c] == 1 else " "
                    val = board.board[r][c]
                    cell_str = "." if val == -1 else str(val)
                    v_line += f"{edge} {cell_str} "
                
                # Falta a última aresta vertical à direita do tabuleiro
                last_edge = "|" if estado_atual.v_edges[r][board.columns] == 1 else " "
                v_line += last_edge
                print(v_line)

            # Imprimir a ÚLTIMA linha de arestas horizontais (fundo do tabuleiro)
            h_line = "+"
            for c in range(board.columns):
                if estado_atual.h_edges[board.rows][c] == 1:
                    h_line += "---+"
                else:
                    h_line += "   +"
            print(h_line)




