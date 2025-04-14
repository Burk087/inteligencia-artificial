import csv
import time
import psutil
from queue import PriorityQueue
from collections import deque

# caminho do arquivo csv com os puzzles
CAMINHO_CSV = '/home/luiz/Área de Trabalho/ed02/ed02-puzzle8.csv'

# estado objetivo que estamos tentando alcançar
ESTADO_OBJETIVO = '123456780'

def ler_puzzles(caminho):
    #le os puzzles a partir do arquivo csv
    puzzles = []
    with open(caminho, newline='', encoding='utf-8') as arquivo:
        leitor = csv.DictReader(arquivo)
        for linha in leitor:
            # junta os valores das colunas em uma única string
            estado = ''.join(linha[coluna] for coluna in linha)
            puzzles.append(estado)
    return puzzles

def gerar_vizinhos(estado):
    # gera os vizinhos de um estado, trocando a posição do '0'
    vizinhos = []
    indice = estado.index('0')  
    linha, coluna = divmod(indice, 3)  

    # possíveis movimentos para o '0' (cima, baixo, esquerda, direita)
    movimentos = {
        'cima': -3,
        'baixo': 3,
        'esquerda': -1,
        'direita': 1
    }

    # verifica os movimentos possíveis
    for direcao, deslocamento in movimentos.items():
        novo_indice = indice + deslocamento
        if direcao == 'cima' and linha == 0: continue  
        if direcao == 'baixo' and linha == 2: continue  
        if direcao == 'esquerda' and coluna == 0: continue  
        if direcao == 'direita' and coluna == 2: continue  

        # troca as posições do '0' e do vizinho
        novo_estado = list(estado)
        novo_estado[indice], novo_estado[novo_indice] = novo_estado[novo_indice], novo_estado[indice]
        vizinhos.append(''.join(novo_estado))

    return vizinhos

def heuristica_mal_colocadas(estado):
    #calcula a heurística de mal colocadas (número de peças fora do lugar)
    return sum(1 for i, c in enumerate(estado) if c != '0' and c != ESTADO_OBJETIVO[i])

def heuristica_manhattan(estado):
    #calcula a heurística de manhattan (distância das peças até o seu lugar correto)
    distancia = 0
    for i, valor in enumerate(estado):
        if valor == '0':
            continue
        pos_objetivo = ESTADO_OBJETIVO.index(valor)
        x1, y1 = divmod(i, 3)
        x2, y2 = divmod(pos_objetivo, 3)
        distancia += abs(x1 - x2) + abs(y1 - y2)
    return distancia

def busca_largura(inicio):
    #implementa a busca em largura
    visitados = set()  
    fila = deque([(inicio, [])])  

    while fila:
        estado, caminho = fila.popleft()  
        if estado == ESTADO_OBJETIVO:  
            return caminho + [estado]
        if estado in visitados:  
            continue
        visitados.add(estado)
        for vizinho in gerar_vizinhos(estado):
            if vizinho not in visitados:
                fila.append((vizinho, caminho + [estado]))
    return None

def busca_profundidade(inicio, limite=30):
    #implementa a busca em profundidade com limite de profundidade
    visitados = set()  
    pilha = [(inicio, [])]  

    while pilha:
        estado, caminho = pilha.pop()  
        if estado == ESTADO_OBJETIVO:  
            return caminho + [estado]
        if len(caminho) >= limite or estado in visitados:  
            continue
        visitados.add(estado)
        for vizinho in gerar_vizinhos(estado):
            if vizinho not in visitados:
                pilha.append((vizinho, caminho + [estado]))
    return None

def busca_gulosa(inicio):
    # implementa a busca gulosa
    visitados = set()  
    fila = PriorityQueue()  
    fila.put((heuristica_mal_colocadas(inicio), inicio, []))  

    while not fila.empty():
        _, estado, caminho = fila.get()  
        if estado == ESTADO_OBJETIVO:  
            return caminho + [estado]
        if estado in visitados:  
            continue
        visitados.add(estado)
        for vizinho in gerar_vizinhos(estado):
            if vizinho not in visitados:
                fila.put((heuristica_mal_colocadas(vizinho), vizinho, caminho + [estado]))
    return None

def busca_a_estrela(inicio):
    # implementa a busca A*
    visitados = set() 
    fila = PriorityQueue()  
    fila.put((heuristica_manhattan(inicio), 0, inicio, []))  
    
    while not fila.empty():
        f, g, estado, caminho = fila.get()  
        if estado == ESTADO_OBJETIVO: 
            return caminho + [estado]
        if estado in visitados:  
            continue
        visitados.add(estado)
        for vizinho in gerar_vizinhos(estado):
            if vizinho not in visitados:
                custo = g + 1
                prioridade = custo + heuristica_manhattan(vizinho)
                fila.put((prioridade, custo, vizinho, caminho + [estado]))
    return None

def medir(algoritmo, estado_inicial):
    # mede o desempenho de um algoritmo (tempo e memória)
    processo = psutil.Process()  
    memoria_antes = processo.memory_info().rss  
    inicio_tempo = time.time()  

    caminho = algoritmo(estado_inicial)  

    fim_tempo = time.time()  
    memoria_depois = processo.memory_info().rss  
    memoria_usada = max(0, (memoria_depois - memoria_antes) / 1024)  

    return {
        'passos': len(caminho) - 1 if caminho else -1,
        'tempo': fim_tempo - inicio_tempo,
        'memoria_kb': memoria_usada
    }

def principal():
    # função principal que executa o programa
    puzzles = ler_puzzles(CAMINHO_CSV)  
    resultados = []

    for indice, puzzle in enumerate(puzzles):
        print(f"\n==========================")
        print(f" Puzzle {indice + 1}")
        print(f" Estado inicial: {puzzle}")
        print(f"==========================")

        resultado = {
            '> Busca em Largura': medir(busca_largura, puzzle),
            '> Busca em Profundidade': medir(busca_profundidade, puzzle),
            '> Busca Gulosa': medir(busca_gulosa, puzzle),
            '> Algoritmo A*': medir(busca_a_estrela, puzzle)
        }

        # exibe os resultados de cada algoritmo
        for nome, dados in resultado.items():
            print(f"{nome}:")
            if dados['passos'] == -1:
                print("  passos: não foi possível resolver.")
            else:
                print(f"  passos: {dados['passos']}")
            print(f"  tempo de execução: {dados['tempo']:.4f} segundos")
            print(f"  memória usada: {dados['memoria_kb']:.2f} KB\n")

        resultados.append(resultado)

if __name__ == '__main__':
    principal()  # chama a função principal para rodar o programa
