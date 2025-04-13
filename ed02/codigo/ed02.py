import csv
import time
import psutil
from queue import PriorityQueue
from collections import deque

# caminho do arquivo csv com os puzzles
caminho_csv = '/home/luiz/Área de Trabalho/ed02/ed02-puzzle8.csv'

# o estado objetivo, ou seja, o resultado final esperado
estado_objetivo = '123456780'

# função para ler os puzzles a partir do arquivo csv
def ler_puzzles(caminho):
    puzzles = []
    with open(caminho, newline='', encoding='utf-8') as arquivo:
        leitor = csv.DictReader(arquivo)
        for linha in leitor:
            # cada linha do csv é transformada em um estado, juntando as colunas
            estado = ''.join(linha[coluna] for coluna in linha)
            puzzles.append(estado)
    return puzzles

# função que gera os vizinhos, ou seja, os estados possíveis a partir do estado atual
def gerar_vizinhos(estado):
    vizinhos = []
    indice = estado.index('0')  # encontra a posição do '0', que é a peça vazia
    linha, coluna = divmod(indice, 3)  # divide o índice em linha e coluna

    # movimentos possíveis (cima, baixo, esquerda, direita)
    movimentos = {
        'cima': -3,
        'baixo': 3,
        'esquerda': -1,
        'direita': 1
    }

    for direcao, deslocamento in movimentos.items():
        novo_indice = indice + deslocamento
        # verifica se o movimento é válido
        if direcao == 'cima' and linha == 0: continue
        if direcao == 'baixo' and linha == 2: continue
        if direcao == 'esquerda' and coluna == 0: continue
        if direcao == 'direita' and coluna == 2: continue

        # cria o novo estado trocando as peças
        novo_estado = list(estado)
        novo_estado[indice], novo_estado[novo_indice] = novo_estado[novo_indice], novo_estado[indice]
        vizinhos.append(''.join(novo_estado))  # adiciona o novo estado à lista de vizinhos

    return vizinhos

# função heurística simples: conta quantas peças estão fora do lugar
def heuristica_mal_colocadas(estado):
    return sum(1 for i, c in enumerate(estado) if c != '0' and c != estado_objetivo[i])

# função heurística de manhattan: calcula a distância de cada peça até seu lugar correto
def heuristica_manhattan(estado):
    distancia = 0
    for i, valor in enumerate(estado):
        if valor == '0':
            continue
        pos_objetivo = estado_objetivo.index(valor)
        x1, y1 = divmod(i, 3)  # posição atual
        x2, y2 = divmod(pos_objetivo, 3)  # posição objetivo
        distancia += abs(x1 - x2) + abs(y1 - y2)  # soma a distância de manhattan
    return distancia

# função de busca em largura (bfs), que explora os estados em camadas
def busca_largura(inicio):
    visitados = set()
    fila = deque([(inicio, [])])  # fila com o estado inicial

    while fila:
        estado, caminho = fila.popleft()  # pega o primeiro estado na fila
        if estado == estado_objetivo:
            return caminho + [estado]  # se encontrar o objetivo, retorna o caminho
        visitados.add(estado)
        # verifica todos os vizinhos do estado
        for vizinho in gerar_vizinhos(estado):
            if vizinho not in visitados:
                fila.append((vizinho, caminho + [estado]))  # adiciona o vizinho à fila

# função de busca em profundidade (dfs), que vai fundo nos estados até atingir o limite
def busca_profundidade(inicio, limite=30):
    visitados = set()
    pilha = [(inicio, [])]  # pilha com o estado inicial

    while pilha:
        estado, caminho = pilha.pop()  # pega o último estado da pilha
        if estado == estado_objetivo:
            return caminho + [estado]  # se encontrar o objetivo, retorna o caminho
        if len(caminho) >= limite:
            continue  # se atingir o limite de profundidade, ignora esse caminho
        visitados.add(estado)
        # verifica todos os vizinhos do estado
        for vizinho in gerar_vizinhos(estado):
            if vizinho not in visitados:
                pilha.append((vizinho, caminho + [estado]))  # adiciona o vizinho à pilha

# função de busca gulosa, que escolhe o estado com a menor heurística (estado mais próximo do objetivo)
def busca_gulosa(inicio):
    visitados = set()
    fila = PriorityQueue()  # fila de prioridade com os estados
    fila.put((heuristica_mal_colocadas(inicio), inicio, []))  # coloca o estado inicial na fila

    while not fila.empty():
        _, estado, caminho = fila.get()  # pega o estado com menor heurística
        if estado == estado_objetivo:
            return caminho + [estado]  # se encontrar o objetivo, retorna o caminho
        visitados.add(estado)
        # verifica todos os vizinhos do estado
        for vizinho in gerar_vizinhos(estado):
            if vizinho not in visitados:
                fila.put((heuristica_mal_colocadas(vizinho), vizinho, caminho + [estado]))  # adiciona o vizinho à fila

# função de busca A*, que combina o custo do caminho com a heurística
def busca_a_estrela(inicio):
    visitados = set()
    fila = PriorityQueue()  # fila de prioridade com os estados
    fila.put((heuristica_manhattan(inicio), 0, inicio, []))  # coloca o estado inicial na fila

    while not fila.empty():
        f, g, estado, caminho = fila.get()  # pega o estado com menor prioridade
        if estado == estado_objetivo:
            return caminho + [estado]  # se encontrar o objetivo, retorna o caminho
        if estado in visitados:
            continue
        visitados.add(estado)
        # verifica todos os vizinhos do estado
        for vizinho in gerar_vizinhos(estado):
            if vizinho not in visitados:
                custo = g + 1  # custo do caminho
                prioridade = custo + heuristica_manhattan(vizinho)  # prioridade combina custo e heurística
                fila.put((prioridade, custo, vizinho, caminho + [estado]))  # adiciona o vizinho à fila

# função que mede o tempo de execução, o uso de memória e o número de passos
def medir(algoritmo, estado_inicial):
    inicio_tempo = time.time()
    processo = psutil.Process()
    memoria_antes = processo.memory_info().rss
    caminho = algoritmo(estado_inicial)
    memoria_depois = processo.memory_info().rss
    fim_tempo = time.time()

    return {
        'passos': len(caminho) - 1 if caminho else -1,  # calcula o número de passos
        'tempo': fim_tempo - inicio_tempo,  # tempo de execução
        'memoria_kb': (memoria_depois - memoria_antes) / 1024  # memória usada
    }

# função principal onde o código começa a rodar
def principal():
    puzzles = ler_puzzles(caminho_csv)  # lê os puzzles do arquivo csv
    resultados = []

    # testa os puzzles um por um
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

        # imprime os resultados para cada algoritmo
        for nome, dados in resultado.items():
            print(f"{nome}:")
            if dados['passos'] == -1:
                print("  passos: não foi possível resolver.")  # se não conseguiu resolver
            else:
                print(f"  passos: {dados['passos']}")  # mostra o número de passos
            print(f"  tempo de execução: {dados['tempo']:.4f} segundos")  # mostra o tempo de execução
            print(f"  memória usada: {dados['memoria_kb']:.2f} KB\n")  # mostra a memória usada
        resultados.append(resultado)

# inicia o programa
if __name__ == '__main__':
    principal()
