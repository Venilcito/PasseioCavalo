import time
import sys

POS_INICIAL = (1, 1)    # (linha, coluna), 0-indexado
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
    """
    h(n) — Heurística de Warnsdorff.
    Retorna quantos movimentos válidos ainda partem de `pos`,
    assumindo que `pos` já está marcada como visitada em `visitados`.
    Quanto menor, mais "crítica" é a casa (menos opções de saída).
    """
    return len(get_vizinhos(pos, visitados))

# Busca DFS com poda por f = g + h  (núcleo do IDA*)
def busca(caminho, visitados, g, limite, nos):
    """
    DFS a partir do último elemento de `caminho`.

    Retorna:
      -1            → solução encontrada (`caminho` já está preenchido)
      float('inf')  → sem vizinhos disponíveis (beco sem saída)
      f > limite    → menor f podado nesta subárvore (próximo limite)
    """
    atual = caminho[-1]

    # h(n): Warnsdorff — `atual` já está em `visitados`
    h = grau_warnsdorff(atual, visitados)
    f = g + h

    # Poda de f: custo estimado supera o limite atual
    if f > limite:
        return f

    # Critério de parada: todas as casas visitadas
    if len(visitados) == TAMANHO_TABULEIRO * TAMANHO_TABULEIRO:
        return -1

    nos['expandidos'] += 1
    proximo_limite = float('inf')
    
    """
    O nó só é contado como expandido se não foi podado pelo f e não é o nó objetivo. 
    Se cair em qualquer um dos return acima, a função termina sem incrementar o contador. 
    A condição existe — só não está escrita como if, está estruturada no fluxo.
    """
    
    # Ordenação por Warnsdorff: casas com menos saídas são exploradas primeiro
    # (evita deixar casas "encurraladas" para o final)
    vizinhos = get_vizinhos(atual, visitados)
    vizinhos.sort(key=lambda v: grau_warnsdorff(v, visitados | {v}))

    for vizinho in vizinhos:
        nos['gerados'] += 1
        caminho.append(vizinho)
        visitados.add(vizinho)

        resultado = busca(caminho, visitados, g + 1, limite, nos)

        if resultado == -1:
            return -1  # Propaga solução para cima na pilha

        if resultado < proximo_limite:
            proximo_limite = resultado

        # Backtrack
        caminho.pop()
        visitados.remove(vizinho)

    return proximo_limite

# IDA*: gerencia o limite crescente
def ida_estrela(inicio):
    visitados = set(inicio)
    caminho   = list(inicio)

    # Threshold inicial = custo exato de qualquer solução do passeio do cavalo
    limite = TAMANHO_TABULEIRO * TAMANHO_TABULEIRO - 1

    nos = {'gerados': 0, 'expandidos': 0}
    iteracoes = 0

    while True:
        iteracoes += 1
        resultado = busca(caminho, visitados, 0, limite, nos)

        # achou a solução
        if resultado == -1:
            return list(caminho), nos['gerados'], nos['expandidos'], iteracoes

        # sem saídas possíveis, mesmo com threshold maior, não há solução
        if resultado == float('inf'):
            return None, nos['gerados'], nos['expandidos'], iteracoes

        # Aumenta limite para o próximo menor f que foi podado
        limite = resultado

# Execução principal
#if __name__ == "__main__":
    #caminho_preset = [(0, 0), (0, 1), (0, 2), (0, 3), (0, 4)]

    tempo_inicio = time.time()
    resultado, gerados, expandidos, iteracoes = ida_estrela(POS_INICIAL)
    #resultado, gerados, expandidos, iteracoes = ida_estrela(caminho_preset)
    tempo_total = (time.time() - tempo_inicio) * 1000

    if resultado:
        print("\n=== Passeio do Cavalo — IDA* + Warnsdorff ===\n")
        print(f"Posição inicial: {POS_INICIAL}")
        #print(f"Número de movimentos: {len(resultado) - 1}")
        print(f"Nós gerados: {gerados}")
        print(f"Nós expandidos: {expandidos}")
        #print(f"Iterações IDA*: {iteracoes}")
        print(f"Tempo de execução: {tempo_total:.5f} ms")

        # Monta e exibe o tabuleiro com a ordem de visita
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