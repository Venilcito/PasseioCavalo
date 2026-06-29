import time
import sys

TAMANHO_TABULEIRO = 8   # tabuleiro 8×8
MOVIMENTOS_L = [(-2, -1), (-2,  1), (-1, -2), (-1,  2), (1, -2), (1,  2), (2, -1), (2,  1)]

# retorna movimentos em L válidos e ainda não visitados
def get_vizinhos(pos, visitados):
    vizinhos = []
    for dx, dy in MOVIMENTOS_L:
        nx, ny = pos[0] + dx, pos[1] + dy
        if 0 <= nx < TAMANHO_TABULEIRO and 0 <= ny < TAMANHO_TABULEIRO \
                and (nx, ny) not in visitados:
            vizinhos.append((nx, ny))
    return vizinhos

def grau_warnsdorff(pos, visitados):
    # heurística de warnsdorff.
    # retorna quantos movimentos válidos ainda partem de pos
    # quanto menor, menos opções de saída

    return len(get_vizinhos(pos, visitados))

# Busca DFS com poda por f = g + h  (núcleo do IDA*)
def busca(caminho, visitados, g, limite, nos, tIni, tMax):
    #print(f"busca: {g}") # debug
    if tMax is not None and (time.perf_counter() - tIni) > tMax:
        # estourou o tempo, retorna -2 como erro
        return -2

    atual = caminho[-1]

    # h(n): Warnsdorff
    h = grau_warnsdorff(atual, visitados)
    f = g + h

    # poda de f
    if f > limite:
        return f

    # parada: todas casas visitadas
    if len(visitados) == TAMANHO_TABULEIRO * TAMANHO_TABULEIRO:
        return -1

    nos['expandidos'] += 1
    proximo_limite = float('inf')
    
    # ordenação por Warnsdorff: casas com menos saídas são exploradas primeiro
    vizinhos = get_vizinhos(atual, visitados)
    vizinhos.sort(key=lambda v: grau_warnsdorff(v, visitados | {v}))

    for vizinho in vizinhos:
        nos['gerados'] += 1
        caminho.append(vizinho)
        visitados.add(vizinho)

        resultado = busca(caminho, visitados, g + 1, limite, nos, tIni, tMax)

        if resultado == -1:
            return -1  # Propaga solução para cima na pilha
        
        if resultado == -2:
            return -2  # propaga erro para cima na pilha

        if resultado < proximo_limite:
            proximo_limite = resultado

        # Backtrack
        caminho.pop()
        visitados.remove(vizinho)

    return proximo_limite

# IDA*: gerencia o limite crescente
def ida_estrela(inicio, tMax=None):
    tempo_inicio = time.perf_counter()

    visitados = set(inicio)
    caminho = list(inicio)

    # limite inicial = custo exato de qualquer solução do passeio do cavalo
    limite = TAMANHO_TABULEIRO * TAMANHO_TABULEIRO - 1
    nos = {'gerados': 0, 'expandidos': 0}

    while True:
        resultado = busca(caminho, visitados, 0, limite, nos, tempo_inicio, tMax)
        tAtual = time.perf_counter() - tempo_inicio

        # achou a solução
        if resultado == -1:
            return list(caminho), nos['gerados'], nos['expandidos'], tAtual

        # não achou dentro do limite de tempo
        if resultado == -2:
            return list(caminho), nos['gerados'], nos['expandidos'], tAtual

        # Aumenta limite para o próximo menor f que foi podado
        limite = resultado


# pra rodar no terminal
if __name__ == "__main__":
    #caminho_preset = [(0, 0), (0, 1), (0, 2), (0, 3), (0, 4)]
    POS_INICIAL = [(3, 3)]

    resultado, gerados, expandidos, tempo = ida_estrela(POS_INICIAL, 0.1)
    #resultado, gerados, expandidos, tempo = ida_estrela(caminho_preset)

    if resultado:
        print("==========================================")
        print("IDA* + Heurística Warnsdorff tabuleiro 8x8")
        print("==========================================")

        print(f"Posição inicial: {POS_INICIAL}")
        print(f"Nós gerados: {gerados}")
        print(f"Nós expandidos: {expandidos}")
        print(f"Tempo de execução: {tempo:.5f} ms")

        tabuleiro = [[0] * TAMANHO_TABULEIRO for _ in range(TAMANHO_TABULEIRO)]
        for i, (x, y) in enumerate(resultado):
            tabuleiro[x][y] = i + 1

        print("\nTabuleiro (ordem de visita):")
        print("    " + "  ".join(str(c) for c in range(TAMANHO_TABULEIRO)))
        for i, linha in enumerate(tabuleiro):
            print(f"{i}   " + "  ".join(f"{casa:2d}" for casa in linha))

        print("\nCaminho (sequência de coordenadas):")
        print(resultado)
    else:
        print("Nenhum passeio completo foi encontrado.")