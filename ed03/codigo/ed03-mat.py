import os
import pandas as pd
import numpy as np
import random

# diretório dos arquivos
diretorio_dos_arquivos = "/home/luiz/Área de Trabalho/ed03-funcoes"

# parâmetros de configuração
tamanho_populacao = 50
geracoes = 100
taxas_mutacao = {'baixa': 0.01, 'media': 0.05, 'alta': 0.1}
metodos_crossover = ['um_ponto', 'dois_pontos', 'uniforme']
valor_minimo = -10
valor_maximo = 10

criterio_parada = 'geracoes'
limiar_convergencia = 1e-5

# carregar os coeficientes do arquivo
def carregar_coeficientes(caminho):
    try:
        df = pd.read_csv(caminho, sep=None, engine='python')
    except Exception as e:
        print(f"erro ao ler o arquivo {caminho}: {e}")
        return []

    df.columns = df.columns.str.strip()

    if 'Coeficiente' not in df.columns:
        print(f"colunas encontradas: {list(df.columns)}")
        raise KeyError("a coluna 'Coeficiente' não foi encontrada no arquivo.")

    return df['Coeficiente'].values

# avaliar o individuo
def avaliar_individuo(individuo, coeficientes, tipo_otimizacao):
    fitness = np.dot(individuo, coeficientes)
    
    if tipo_otimizacao == 'maximizar':
        fitness = -fitness

    return fitness

# inicializar a população de forma aleatória ou heurística
def inicializar_populacao(coeficientes, modo='aleatoria'):
    genes = len(coeficientes)
    if modo == 'aleatoria':
        return [np.random.uniform(valor_minimo, valor_maximo, genes) for _ in range(tamanho_populacao)]
    elif modo == 'heuristica':
        base = np.linspace(valor_minimo, valor_maximo, genes)
        return [np.random.permutation(base) for _ in range(tamanho_populacao)]

# selecionar pais para o crossover
def selecionar_pais(populacao, fitness):
    idx = np.argsort(fitness)
    return [populacao[i] for i in idx[:2]]

# fazer o crossover entre os pais
def crossover(pai1, pai2, metodo):
    if metodo == 'um_ponto':
        ponto = random.randint(1, len(pai1) - 1)
        return np.concatenate([pai1[:ponto], pai2[ponto:]])
    elif metodo == 'dois_pontos':
        p1, p2 = sorted(random.sample(range(len(pai1)), 2))
        filho = np.array(pai1)
        filho[p1:p2] = pai2[p1:p2]
        return filho
    elif metodo == 'uniforme':
        return np.array([pai1[i] if random.random() < 0.5 else pai2[i] for i in range(len(pai1))])

# aplicar a mutação
def mutar(individuo, taxa_mutacao):
    return np.array([gene + np.random.normal(0, 1) if random.random() < taxa_mutacao else gene for gene in individuo])

# função principal do algoritmo genético
def algoritmo_genetico(coeficientes, metodo_crossover, taxa_mutacao, modo_inicializacao, tipo_otimizacao):
    populacao = inicializar_populacao(coeficientes, modo_inicializacao)
    historico_melhores = []

    for geracao in range(geracoes):
        fitness = [avaliar_individuo(ind, coeficientes, tipo_otimizacao) for ind in populacao]
        melhor = min(fitness)
        historico_melhores.append(melhor)

        if criterio_parada == 'convergencia' and geracao > 5:
            if abs(historico_melhores[-1] - historico_melhores[-5]) < limiar_convergencia:
                break

        nova_populacao = []
        for _ in range(tamanho_populacao):
            pais = selecionar_pais(populacao, fitness)
            filho = crossover(pais[0], pais[1], metodo_crossover)
            filho = mutar(filho, taxa_mutacao)
            nova_populacao.append(filho)

        populacao = nova_populacao

    melhor_fitness = min([avaliar_individuo(ind, coeficientes, tipo_otimizacao) for ind in populacao])
    return melhor_fitness, historico_melhores

# execução principal
if __name__ == "__main__":
    arquivos = [f for f in os.listdir(diretorio_dos_arquivos) if f.startswith("function_opt_")]
    for arquivo in arquivos:
        print(f"\narquivo: {arquivo}")
        caminho = os.path.join(diretorio_dos_arquivos, arquivo)
        coeficientes = carregar_coeficientes(caminho)

        for metodo in metodos_crossover:
            for taxa_nome, taxa_valor in taxas_mutacao.items():
                for modo_init in ['aleatoria', 'heuristica']:
                    resultado_minimo, historico_minimo = algoritmo_genetico(coeficientes, metodo, taxa_valor, modo_init, 'minimizar')
                    resultado_maximo, historico_maximo = algoritmo_genetico(coeficientes, metodo, taxa_valor, modo_init, 'maximizar')

                    print(f"metodo: {metodo:10} | mutacao: {taxa_nome:6} | init: {modo_init:9} | "
                          f"melhor resultado (min): {resultado_minimo:.4f} | melhor resultado (max): {resultado_maximo:.4f}")