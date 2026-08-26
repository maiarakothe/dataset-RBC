import streamlit as st
import pandas as pd

# Importa funções do main
from main import (
    df,
    encontrar_similares,
    reutilizar,
    reter_caso
)

# Define as configurações da página
st.set_page_config(
    page_title="RBC - Filmes Similares",
    page_icon="🎬",
    layout="wide"
)



# SESSION STATE
# Faz com que a página não tenha somente informações temporárias, permetindo a interação com o usuário

if "resultado" not in st.session_state:
    st.session_state.resultado = pd.DataFrame()

if "filme_escolhido" not in st.session_state:
    st.session_state.filme_escolhido = None

if "recomendacao" not in st.session_state:
    st.session_state.recomendacao = None

if "avaliado" not in st.session_state:
    st.session_state.avaliado = False


# TÍTULO

st.title("🎬 RBC - Filmes Similares")

st.write(
    "Sistema de recomendação de filmes baseado em "
    "Raciocínio Baseado em Casos."
)

# SELEÇÃO DO FILME

filmes = sorted(
    df["Series_Title"]
    .dropna()
    .unique()
)

filme_escolhido = st.selectbox(
    "Escolha um filme:",
    filmes
)


quantidade = st.slider(
    "Quantidade de filmes similares:",
    min_value=1,
    max_value=10,
    value=5
)


# 1. RECUPERAÇÃO
if st.button(
    "🔎 Encontrar filmes similares",
    use_container_width=True
):

    resultado = encontrar_similares(
        filme_escolhido,
        quantidade
    )

    st.session_state.resultado = resultado
    st.session_state.filme_escolhido = filme_escolhido

    # Nova busca = nova recomendação
    st.session_state.recomendacao = None
    st.session_state.avaliado = False


# Recupera o resultado salvo
resultado = st.session_state.resultado


# MOSTRAR RESULTADOS
if not resultado.empty:

    filme = df[
        df["Series_Title"] ==
        st.session_state.filme_escolhido
    ].iloc[0]


    # FILME ESCOLHIDO
    st.subheader("🎬 Filme escolhido")

    col1, col2 = st.columns([1, 2])


    with col1:
        # Carrega o poster do filme
        poster = filme.get(
            "Poster_Link",
            ""
        )

        if pd.notna(poster) and str(poster).strip():

            st.image(
                poster,
                width=250
            )

    # Define a tabela com as informações do filme
    with col2:

        st.markdown(
            f"### {filme['Series_Title']}"
        )

        st.write(
            f"🎭 **Gênero:** {filme['Genre']}"
        )

        st.write(
            f"🎬 **Diretor:** {filme['Director']}"
        )

        st.write(
            f"👤 **Ator 1:** {filme['Star1']}"
        )

        st.write(
            f"👤 **Ator 2:** {filme['Star2']}"
        )

        st.write(
            f"📅 **Ano:** "
            f"{int(filme['Released_Year'])}"
        )

        st.write(
            f"⏱️ **Duração:** "
            f"{filme['Runtime']:.0f} min"
        )

        st.write(
            f"⭐ **IMDb:** "
            f"{filme['IMDB_Rating']}"
        )

        if pd.notna(filme["Meta_score"]):

            st.write(
                f"🎯 **Meta Score:** "
                f"{filme['Meta_score']:.0f}"
            )

        else:

            st.write(
                "🎯 **Meta Score:** "
                "Não disponível"
            )


    # 2. REUTILIZAÇÃO
    # Usa as informações recuperadas do DataSet e recomenda o filme mais similar de forma separada.
    if st.session_state.recomendacao is None:

        st.session_state.recomendacao = (
            reutilizar(resultado)
        )


    recomendacao = (
        st.session_state.recomendacao
    )


    st.divider()

    st.subheader(
        "⭐ Recomendação do sistema"
    )


    st.success(
        f"Com base nos filmes recuperados, "
        f"nossa principal recomendação é: "
        f"**{recomendacao['Filme']}**"
    )


    percentual_recomendacao = (
        recomendacao["Similaridade"] * 100
    )


    st.write(
        f"Similaridade: "
        f"**{percentual_recomendacao:.2f}%**"
    )


    # 3. REVISÃO
    # Com base na recomendação feita pelo sistema, o usuário indica se achou adequada ou não.
    st.subheader(
        "📝 Revisão da recomendação"
    )

    # Constroi a sessão que permite o usuário interragir.
    avaliacao = st.radio(
        "Você gostou dessa recomendação?",
        ["👍 Sim", "👎 Não"],
        key="avaliacao_recomendacao"
    )


    if st.button(
        "Registrar avaliação",
        use_container_width=True
    ):

        if not st.session_state.avaliado:

            # 4. RETENÇÃO
            # Utiliza a opinião do usuário sobre a recomendação similar.
            # As informações sobre a recomendação feita, sobre o filme e sobre a opinião do usuário
            # são salvas em uma pasta "casos_rbc_csv" 
            if avaliacao == "👍 Sim":

                reter_caso(
                    st.session_state.filme_escolhido,
                    recomendacao["Filme"],
                    recomendacao["Similaridade"],
                    "positiva"
                )

                st.session_state.avaliado = True

                # Retorna o feedback da avaliação feita
                st.success(
                    "✅ Avaliação registrada! "
                    "O caso foi armazenado "
                    "na base de casos."
                )


            else:

                reter_caso(
                    st.session_state.filme_escolhido,
                    recomendacao["Filme"],
                    recomendacao["Similaridade"],
                    "negativa"
                )

                st.session_state.avaliado = True

                # Retorna o feedback da avaliação feita
                st.warning(
                    "⚠️ Avaliação registrada como "
                    "negativa. O caso foi armazenado "
                    "na base de casos."
                )


        else:

            st.info(
                "Esta recomendação já foi avaliada."
            )


    # FILMES SIMILARES
    st.divider()

    st.subheader(
        "🍿 Filmes similares"
    )

    # Numera cada filme começando do 1.
    for posicao, (_, filme) in enumerate(
        resultado.iterrows(),
        start=1
    ):
        # Mostra o percentual sem levar em consideração a avaliação do usuário.
        percentual = (
            filme["Similaridade"] * 100
        )

        # Mostra o percentual levando em consideração a avaliação do usuário.
        score_rbc = (
            filme["Score_RBC"] * 100
        )

        with st.container(
            border=True
        ):

            # Configurações do pôster dos filmes similares
            col_poster, col_info, col_score = (
                st.columns([1, 4, 1])
            )


            with col_poster:

                poster = filme.get(
                    "Poster_Link",
                    ""
                )

                if (
                    pd.notna(poster)
                    and str(poster).strip()
                ):

                    st.image(
                        poster,
                        width=200
                    )

            # Carrega informações dos filmes similares
            with col_info:

                st.markdown(
                    f"### #{posicao} — "
                    f"{filme['Filme']}"
                )

                st.write(
                    f"🎭 **Gênero:** "
                    f"{filme['Genre']}"
                )

                st.write(
                    f"🎬 **Diretor:** "
                    f"{filme['Director']}"
                )

                st.write(
                    f"👤 **Ator 1:** "
                    f"{filme['Star1']}"
                )

                st.write(
                    f"👤 **Ator 2:** "
                    f"{filme['Star2']}"
                )

                st.write(
                    f"📅 **Ano:** "
                    f"{int(filme['Released_Year'])}"
                )

                st.write(
                    f"⏱️ **Duração:** "
                    f"{filme['Runtime']:.0f} min"
                )

                st.write(
                    f"⭐ **IMDb:** "
                    f"{filme['IMDB_Rating']}"
                )

                if pd.notna(
                    filme["Meta_score"]
                ):

                    st.write(
                        f"🎯 **Meta Score:** "
                        f"{filme['Meta_score']:.0f}"
                    )

                else:

                    st.write(
                        "🎯 **Meta Score:** "
                        "Não disponível"
                    )

            # Exibe e Formata o percentual de similaridade dos filmes com o filme principal.
            with col_score:

                st.metric(
                    "Similaridade",
                    f"{percentual:.2f}%"
                )

                st.metric(
                    "Score RBC",
                    f"{score_rbc:.2f}%"
                )


else:

    st.info(
        "Escolha um filme e clique em "
        "'Encontrar filmes similares'."
    )