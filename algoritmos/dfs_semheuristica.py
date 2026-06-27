#TRABALHO 1 - Inteligência Artificial
#Dupla: Alexia Yonamine e Kurt Rodrigues
#Algoritmo: DFS (sem heurística)

import time

#movimentos possíveis do cavalo
MOVIMENTOS_CAVALO = [
    (-2, -1), (-2, 1),
    (-1, -2), (-1, 2),
    (1, -2), (1, 2),
    (2, -1), (2, 1)
]


def casa_para_indice(linha, coluna):
    """Converte um par (linha, coluna) em um índice único de 0 a 63, utilizado no bitmask de casas visitadas."""
    return linha * 8 + coluna


def indice_para_casa(indice):
    """Operação inversa de casa_para_indice: converte o índice (0 a 63) de volta para o par (linha, coluna)."""
    return divmod(indice, 8)


def montar_tabuleiro():
    """
    Constrói o grafo do tabuleiro como lista de adjacência, modelando cada casa
    como um vértice e cada movimento legal do cavalo como uma aresta. O grafo é
    construído uma única vez e reutilizado durante toda a busca, evitando o
    recálculo dos movimentos a cada nó expandido.
    Retorna a lista 'adjacencia', onde adjacencia[i] contém os índices das
    casas alcançáveis pelo cavalo a partir da casa de índice i.
    """
    adjacencia = [[] for _ in range(64)]
    for linha in range(8):
        for coluna in range(8):
            origem = casa_para_indice(linha, coluna)
            for mov_linha, mov_coluna in MOVIMENTOS_CAVALO:
                nova_linha = linha + mov_linha
                nova_coluna = coluna + mov_coluna
                # A aresta só é adicionada se o destino permanece dentro dos limites do tabuleiro.
                if 0 <= nova_linha < 8 and 0 <= nova_coluna < 8:
                    destino = casa_para_indice(nova_linha, nova_coluna)
                    adjacencia[origem].append(destino)
    return adjacencia


#grafo do tabuleiro
GRAFO = montar_tabuleiro()


def sucessores(indice, visitados_mask):
    """
    Gera os índices das casas sucessoras (alcançáveis pelo cavalo) a partir de
    'indice' que ainda não foram visitadas no ramo atual, identificadas pelo
    bitmask 'visitados_mask'. A consulta é feita diretamente no grafo previamente
    construído.
    """
    for j in GRAFO[indice]:
        if not (visitados_mask >> j) & 1:   #bit desligado indica casa ainda não visitada
            yield j


class No:
    """
    Representa um nó da árvore de busca. Cada nó corresponde a uma casa ocupada
    em um caminho parcial explorado pelo DFS
    Atributos:
        indice - índice da casa atual (0 a 63);
        pai - nó antecessor na árvore (None para a raiz), utilizado na reconstrução do caminho;
        visitados - bitmask das casas já visitadas no ramo;
        profundidade - nível do nó na árvore, equivalente ao número de movimentos realizados até a casa atual.
    """
    __slots__ = ("indice", "pai", "visitados", "profundidade")

    def __init__(self, indice, pai, visitados):
        self.indice = indice
        self.pai = pai
        self.visitados = visitados
        self.profundidade = 0 if pai is None else pai.profundidade + 1


def reconstruir_caminho(no):
    """
    Reconstrói o caminho da raiz até 'no' percorrendo os ponteiros para o nó pai
    Retorna a sequência de casas (linha, coluna) na ordem em que foram visitadas.
    """
    caminho = []
    atual = no
    while atual is not None:
        caminho.append(indice_para_casa(atual.indice))
        atual = atual.pai
    caminho.reverse()
    return caminho


def busca_dfs(inicio, limite_tempo=None, limite_nos=None):
    """
    Resolve o Passeio do Cavalo aberto em um tabuleiro 8x8 pela de Busca em
    Profundidade (DFS) sem heurística, a partir da casa 'inicio'. Parâmetros
    opcionais 'limite_tempo' e 'limite_nos' param a execução caso os
    limites colocados sejam violados
    Retorna (caminho, metricas): o caminho é a sequência de casas da solução
    (ou None, se não achar) e métricas agrupadas com os dados de desempenho
    """
    inicio = tuple(inicio)
    indice_inicial = casa_para_indice(inicio[0], inicio[1])

    #raiz da árvore de busca, correspondente à casa inicial.
    raiz = No(indice_inicial, None, 1 << indice_inicial)

    pilha = [raiz]

    nos_gerados = 1
    nos_expandidos = 0

    tempo_inicio = time.perf_counter()

    while pilha:
        no = pilha.pop()   #remoção do topo da pilha (LIFO)
        nos_expandidos += 1

        #verifica se todas as 64 casas foram visitadas
        if no.profundidade + 1 == 64:
            caminho = reconstruir_caminho(no)
            return caminho, monta_metricas(
                nos_gerados, nos_expandidos,
                time.perf_counter() - tempo_inicio,
                status="solucao_encontrada")

        #expansão do nó: os sucessores são inseridos na pilha. Inserção em ordem invertida garante que o primeiro movimento de MOVIMENTOS_CAVALO seja o primeiro a ser explorado
        filhos = list(sucessores(no.indice, no.visitados))
        for j in reversed(filhos):
            pilha.append(No(j, no, no.visitados | (1 << j)))
            nos_gerados += 1

        # Critérios de parada opcionais, por número de nós gerados e por tempo.
        if limite_nos is not None and nos_gerados > limite_nos:
            return None, monta_metricas(
                nos_gerados, nos_expandidos,
                time.perf_counter() - tempo_inicio,
                status="limite_de_nos_atingido")
        if limite_tempo is not None and (time.perf_counter() - tempo_inicio) > limite_tempo:
            return None, monta_metricas(
                nos_gerados, nos_expandidos,
                time.perf_counter() - tempo_inicio,
                status="limite_de_tempo_atingido")

    #Pilha vazia indica espaço de busca esgotado. No tabuleiro 8x8 esta situação não ocorre, pois existe solução a partir de qualquer casa inicial.
    return None, monta_metricas(
        nos_gerados, nos_expandidos,
        time.perf_counter() - tempo_inicio, status="sem_solucao")


def monta_metricas(gerados, expandidos, tempo, status):
    """Agrupa as métricas de desempenho utilizadas para comparação"""
    return {
        "status": status,
        "nos_gerados": gerados,
        "nos_expandidos": expandidos,
        "tempo_segundos": tempo,
    }


def imprime_tabuleiro(caminho):
    """Exibe o tabuleiro indicando a ordem de visitação de cada casa (1 corresponde à casa inicial)."""
    if not caminho:
        print("(sem caminho para exibir)")
        return
    ordem = {casa: i + 1 for i, casa in enumerate(caminho)}
    for linha in range(8):
        celulas = []
        for coluna in range(8):
            valor = ordem.get((linha, coluna), 0)
            celulas.append(str(valor).rjust(2) if valor else "..")
        print(" ".join(celulas))


def validar_passeio(caminho):
    """
    Verifica validade do passeio aberto: todas as 64 casas devem ser 
    visitadas exatamente uma vez e cada transição deve representar um movimento permitido do cavalo.
    """
    if caminho is None:
        return False
    if len(caminho) != 64 or len(set(caminho)) != len(caminho):
        return False
    for (l1, c1), (l2, c2) in zip(caminho, caminho[1:]):
        if (abs(l1 - l2), abs(c1 - c2)) not in [(1, 2), (2, 1)]:
            return False
    return True


def resolve_e_relata(inicio, **limites):
    """Executa a busca a partir de 'inicio' e apresenta métricas obtidas e o tabuleiro resolvido."""
    print(f"\nINICIANDO caminho na linha {inicio[0] + 1} e coluna {inicio[1] + 1}")
    caminho, m = busca_dfs(inicio, **limites)
    print(f"Status: {m['status']}")
    print(f"Nos gerados: {m['nos_gerados']:,}")
    print(f"Nos expandidos: {m['nos_expandidos']:,}")
    print(f"Tempo (s): {m['tempo_segundos']:.2f}")
    if caminho:
        print(f"Passeio valido: {validar_passeio(caminho)}\n")
        imprime_tabuleiro(caminho)


def ler_casa_inicial():
    """
    Pede ao usuário a casa inicial (linha e coluna de 1 a 8) e converte
    para a representação interna em base 0. A leitura é repetida até que uma
    entrada válida seja fornecida.
    """
    print("\nInsira a linha e coluna iniciais (enumeradas de 1 a 8):")
    while True:
        try:
            linha = int(input("  -> Linha inicial (1 a 8): "))
            coluna = int(input("  -> Coluna inicial (1 a 8): "))
        except ValueError:
            print("   X Entrada inválida: digite apenas numeros inteiros.\n")
            continue
        if 1 <= linha <= 8 and 1 <= coluna <= 8:
            return (linha - 1, coluna - 1)   # Conversão para base 0.
        print("  X Fora do tabuleiro. Use valores de 1 a 8.\n")

def dfs_interface(inicio):
     # Recebe [(linha, coluna)] da interface
    if isinstance(inicio, list):
        inicio = inicio[0]
        
    caminho, metricas = busca_dfs(inicio)
    return (caminho, metricas["nos_gerados"], metricas["nos_expandidos"], 0)

if __name__ == "__main__":
    print("=======================================")
    print("DFS PURO (sem heuristica) tabuleiro 8x8")
    print("=======================================")

    inicio = ler_casa_inicial()   #usuário define casa de origem do passeio

    resolve_e_relata(inicio, limite_tempo=None)