import pandas as pd
import numpy as np

df = pd.read_csv("imdb_top_1000.csv")


def melhorar_poster(url):
    if pd.isna(url) or not str(url).strip():
        return url
    url = str(url)
    if "._V1_" in url:
        url = url.split("._V1_")[0]
        return url + "._V1_UX300_CR0,0,300,440_AL_.jpg"
    return url


df["Poster_Link"] = df["Poster_Link"].apply(melhorar_poster)

# Converte o ano para número
df["Released_Year"] = pd.to_numeric(df["Released_Year"], errors="coerce")

# Remove o "min" da duração
df["Runtime"] = df["Runtime"].str.replace(" min", "", regex=False).astype(float)

# Preenche valores vazios nas colunas de texto
colunas_texto = ["Genre", "Director", "Star1", "Star2"]

for coluna in colunas_texto:
    df[coluna] = df[coluna].fillna("").astype(str).str.strip()


# Normaliza os valores entre 0 e 1
def normalizar_01(serie):
    minimo = serie.min()
    maximo = serie.max()
    return (serie - minimo) / (maximo - minimo)


# Normaliza os atributos numéricos
df["Year_norm"] = normalizar_01(df["Released_Year"])
df["Runtime_norm"] = normalizar_01(df["Runtime"])
df["IMDB_norm"] = normalizar_01(df["IMDB_Rating"])
df["Meta_norm"] = normalizar_01(df["Meta_score"])


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
def similaridade_filmes(filme_a, filme_b):
    similaridades = []
    pesos = []

    # Define os atributos usados e seus pesos
    atributos = [
        ("Genre", similaridade_jaccard, 3),
        ("Director", similaridade_categorica, 2),
        ("IMDB_norm", similaridade_numerica, 2),
        ("Meta_norm", similaridade_numerica, 1),
        ("Year_norm", similaridade_numerica, 1),
        ("Runtime_norm", similaridade_numerica, 1),
        ("Star1", similaridade_categorica, 2),
        ("Star2", similaridade_categorica, 1),
    ]

    # Calcula cada similaridade individual
    for atributo, funcao, peso in atributos:
        sim = funcao(filme_a[atributo], filme_b[atributo])

        if sim is not None:
            similaridades.append(sim)
            pesos.append(peso)

    # Retorna zero caso não exista nenhum atributo válido
    if not similaridades:
        return 0.0

    # Calcula a média ponderada das similaridades
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

    # Compara o filme escolhido com todos os outros
    for _, filme in df.iterrows():
        if filme["Series_Title"] == titulo:
            continue

        similaridade = similaridade_filmes(filme_escolhido, filme)

        resultados.append(
            {
                "Filme": filme["Series_Title"],
                "Genre": filme["Genre"],
                "Director": filme["Director"],
                "Star1": filme["Star1"],
                "Star2": filme["Star2"],
                "Released_Year": filme["Released_Year"],
                "Runtime": filme["Runtime"],
                "IMDB_Rating": filme["IMDB_Rating"],
                "Meta_score": filme["Meta_score"],
                "Poster_Link": filme["Poster_Link"],
                "Similaridade": similaridade,
            }
        )

    # Organiza os filmes do mais parecido para o menos parecido
    resultados = pd.DataFrame(resultados)
    resultados = resultados.sort_values(by="Similaridade", ascending=False)

    return resultados.head(quantidade)
