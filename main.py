from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from pandas.errors import EmptyDataError
import pandas as pd
import numpy as np


# Lê o DataSet
df = pd.read_csv("imdb_top_1000.csv")

# Melhora a resolução da imagem dos pôsters carregados
def melhorar_poster(url):
    if pd.isna(url) or not str(url).strip():
        return url
    url = str(url)
    if "._V1_" in url:
        url = url.split("._V1_")[0]
        return url + "._V1_UX300_CR0,0,300,440_AL_.jpg"
    return url

# Aplica a melhoria do poster
df["Poster_Link"] = df["Poster_Link"].apply(melhorar_poster)

# Converte o ano para número
df["Released_Year"] = pd.to_numeric(df["Released_Year"], errors="coerce")

# Remove o "min" da duração
df["Runtime"] = df["Runtime"].str.replace(" min", "", regex=False).astype(float)

# Preenche valores vazios nas colunas de texto
colunas_texto = ["Genre", "Director", "Star1", "Star2", "Overview"]


# Converte a classificação indicativa para uma faixa etária aproximada.
def normalizar_certificate(certificate):

    # Caso não exista classificação
    if pd.isna(certificate):
        return np.nan

    # Padroniza o texto
    certificate = str(certificate).strip().upper()

    # Mapeia as classificações para uma idade aproximada.
    classificacoes = {
        "U": 0,
        "G": 0,
        "PG": 10,
        "GP": 10,
        "PG-13": 13,
        "UA": 13,
        "U/A": 13,
        "TV-14": 14,
        "16": 16,
        "R": 18,
        "A": 18,
        "TV-MA": 18,
        "APPROVED": 0,
        "PASSED": 0,
        "UNRATED": np.nan,
    }

    idade = classificacoes.get(certificate, np.nan)

    # Converte a idade para uma escala de 0 a 1.
    if pd.isna(idade):
        return np.nan

    return idade / 18


# Cria a coluna que será utilizada pelo RBC.
df["Certificate_norm"] = df["Certificate"].apply(normalizar_certificate)

# Tira os espaços em branco dos textos
for coluna in colunas_texto:
    df[coluna] = df[coluna].fillna("").astype(str).str.strip()

# Cria uma representação numérica dos textos dos filmes.
vectorizer = TfidfVectorizer(stop_words="english")

overview_tfidf = vectorizer.fit_transform(df["Overview"])


# Normaliza os valores entre 0 e 1
def normalizar_01(serie):
    minimo = serie.min()
    maximo = serie.max()
    return (serie - minimo) / (maximo - minimo)


# Normaliza os atributos numéricos
df["Year_norm"] = normalizar_01(df["Released_Year"])
df["Runtime_norm"] = normalizar_01(df["Runtime"])



def similaridade_overview(indice_a, indice_b):
    """
    Calcula a similaridade entre os Overviews
    de dois filmes utilizando similaridade do cosseno.
    """

    vetor_a = overview_tfidf[indice_a]
    vetor_b = overview_tfidf[indice_b]

    return cosine_similarity(vetor_a, vetor_b)[0][0]


# Calcula a similaridade entre dois valores numéricos
def similaridade_numerica(valor_a, valor_b):
    if pd.isna(valor_a) or pd.isna(valor_b):
        return None

    return 1 - abs(valor_a - valor_b)


# Compara dois valores categóricos
def similaridade_categorica(valor_a, valor_b):
    if not valor_a or not valor_b:
        return None

    return 1.0 if valor_a == valor_b else 0.0


# Compara os gêneros usando Jaccard
def similaridade_jaccard(generos_a, generos_b):
    conjunto_a = {g.strip().lower() for g in generos_a.split(",") if g.strip()}

    conjunto_b = {g.strip().lower() for g in generos_b.split(",") if g.strip()}

    if not conjunto_a or not conjunto_b:
        return None

    return len(conjunto_a.intersection(conjunto_b)) / len(conjunto_a.union(conjunto_b))


# Calcula a similaridade entre dois filmes
def similaridade_filmes(filme_a, filme_b, indice_a, indice_b):

    similaridades = []
    pesos = []

    atributos = [
        ("Genre", similaridade_jaccard, 3),
        ("Director", similaridade_categorica, 2),
        ("Year_norm", similaridade_numerica, 1),
        ("Runtime_norm", similaridade_numerica, 1),
        ("Certificate_norm", similaridade_numerica, 2),
        ("Star1", similaridade_categorica, 2),
        ("Star2", similaridade_categorica, 1),
    ]

    # Compara os atributos tradicionais
    for atributo, funcao, peso in atributos:

        sim = funcao(filme_a[atributo], filme_b[atributo])

        if sim is not None:
            similaridades.append(sim)
            pesos.append(peso)

    # Compara o conteúdo das sinopses
    sim_overview = similaridade_overview(indice_a, indice_b)

    similaridades.append(sim_overview)

    # Peso da sinopse
    pesos.append(3)

    if not similaridades:
        return 0.0

    return np.average(similaridades, weights=pesos)


# Encontra os filmes mais parecidos com o escolhido
def encontrar_similares(titulo, quantidade=5):
    filme_escolhido = df[df["Series_Title"] == titulo]

    # Verifica se o filme existe no dataset
    if filme_escolhido.empty:
        print(f"Filme '{titulo}' não encontrado.")
        return pd.DataFrame()

    filme_escolhido = filme_escolhido.iloc[0]
    resultados = []

    indice_escolhido = df[df["Series_Title"] == titulo].index[0]

    # Compara o filme escolhido com todos os outros
    for indice, filme in df.iterrows():

        if filme["Series_Title"] == titulo:
            continue

        similaridade = similaridade_filmes(
            filme_escolhido, filme, indice_escolhido, indice
        )

        resultados.append(
            {
                "Filme": filme["Series_Title"],
                "Genre": filme["Genre"],
                "Director": filme["Director"],
                "Star1": filme["Star1"],
                "Star2": filme["Star2"],
                "Certificate": filme["Certificate"],
                "Overview": filme["Overview"],
                "Released_Year": filme["Released_Year"],
                "Runtime": filme["Runtime"],
                "Poster_Link": filme["Poster_Link"],
                "Similaridade": similaridade,
            }
        )

    # Organiza os filmes do mais parecido para o menos parecido
    resultados = pd.DataFrame(resultados)
    resultados = resultados.sort_values(by="Similaridade", ascending=False)

    resultados = aplicar_experiencias_retentidas(titulo, resultados)

    return resultados.head(quantidade)


# 2 R - Reutilização
def reutilizar(resultados):
    """
    REUTILIZAÇÃO:
    Utiliza o caso mais semelhante recuperado
    para gerar uma recomendação.
    """

    if resultados.empty:
        return None

    return resultados.iloc[0]


# Armazena a recomendação do usuário no arquivo "casos_rbc_csv".
def reter_caso(filme_pesquisado, filme_recomendado, similaridade, avaliacao):
    novo_caso = pd.DataFrame(
        [
            {
                "Filme_Pesquisado": filme_pesquisado,
                "Filme_Recomendado": filme_recomendado,
                "Similaridade": similaridade,
                "Avaliacao": avaliacao,
            }
        ]
    )

    arquivo = "casos_rbc.csv"

    try:
        # Tenta carregar casos já armazenados.
        casos = pd.read_csv(arquivo)

        # Adiciona um novo caso ao existentes.
        casos = pd.concat([casos, novo_caso], ignore_index=True)
    except FileNotFoundError:
        casos = novo_caso

    # Cria o arquivo se ele não existir.
    casos.to_csv(arquivo, index=False)

    return True


# Trata o erro caso o arquivo exista mas esta vazio.
from pandas.errors import EmptyDataError


# Carrega os casos anteriores.
def carregar_casos_retidos():

    arquivo = "casos_rbc.csv"

    # Define as colunas esperadas.
    colunas = ["Filme_Pesquisado", "Filme_Recomendado", "Similaridade", "Avaliacao"]

    try:

        casos = pd.read_csv(arquivo)

        # Verifica se o arquivo possui as colunas esperadas
        if not all(coluna in casos.columns for coluna in colunas):
            return pd.DataFrame(columns=colunas)

        return casos

    # Se o arquivo nao existir ou estiver vazio, retorna colunas vazias.
    except (FileNotFoundError, EmptyDataError):

        return pd.DataFrame(columns=colunas)


# Aplica as avaliações do usuário (caso exista)
def aplicar_experiencias_retentidas(titulo, resultados):
    casos = carregar_casos_retidos()

    # Se não têm nenhuma avaliação sobre o filme naquele caso, mostra a similaridade original.
    if casos.empty:
        resultados["Score_RBC"] = resultados["Similaridade"]
        return resultados

    # Copia os resultados para não modificar nada no DataSet original.
    resultados = resultados.copy()

    # Ganha a similaridade original. Caso tenha alguma avaliação no caso
    # a similaridade do "Score_RBC" aumenta 2% (casos positivos) ou
    # diminuí 2% (casos negativos).
    resultados["Score_RBC"] = resultados["Similaridade"]

    casos_filme = casos[casos["Filme_Pesquisado"] == titulo]

    for _, caso in casos_filme.iterrows():

        filme = caso["Filme_Recomendado"]

        if caso["Avaliacao"] == "positiva":

            resultados.loc[resultados["Filme"] == filme, "Score_RBC"] += 0.02

        elif caso["Avaliacao"] == "negativa":

            resultados.loc[resultados["Filme"] == filme, "Score_RBC"] -= 0.02

    # Mantém o Score_RBC entre 0 e 1
    resultados["Score_RBC"] = resultados["Score_RBC"].clip(0, 1)

    # Ordena os valores
    return resultados.sort_values(by="Score_RBC", ascending=False)