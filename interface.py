import streamlit as st
import pandas as pd

from main import df, encontrar_similares

st.set_page_config(page_title="RBC - Filmes Similares", page_icon="🎬", layout="wide")

st.title("🎬 RBC - Filmes Similares")
st.write("Sistema de recomendação de filmes baseado em " "Raciocínio Baseado em Casos.")

filmes = sorted(df["Series_Title"].dropna().unique())

filme_escolhido = st.selectbox("Escolha um filme:", filmes)

quantidade = st.slider(
    "Quantidade de filmes similares:", min_value=1, max_value=10, value=5
)

if st.button("🔎 Encontrar filmes similares", use_container_width=True):
    resultado = encontrar_similares(filme_escolhido, quantidade)
    filme = df[df["Series_Title"] == filme_escolhido].iloc[0]

    st.subheader("🎬 Filme escolhido")
    col1, col2 = st.columns([1, 2])

    with col1:
        poster = filme.get("Poster_Link", "")
        if pd.notna(poster) and str(poster).strip():
            st.image(poster, width=250)

    with col2:
        st.markdown(f"### {filme['Series_Title']}")
        st.write(f"🎭 **Gênero:** {filme['Genre']}")
        st.write(f"🎬 **Diretor:** {filme['Director']}")
        st.write(f"👤 **Ator 1:** {filme['Star1']}")
        st.write(f"👤 **Ator 2:** {filme['Star2']}")
        st.write(f"📅 **Ano:** " f"{int(filme['Released_Year'])}")
        st.write(f"⏱️ **Duração:** " f"{filme['Runtime']:.0f} min")
        st.write(f"⭐ **IMDb:** " f"{filme['IMDB_Rating']}")
        if pd.notna(filme["Meta_score"]):
            st.write(f"🎯 **Meta Score:** " f"{filme['Meta_score']:.0f}")
        else:
            st.write("🎯 **Meta Score:** Não disponível")

    st.divider()

    st.subheader("🍿 Filmes similares")

    if resultado.empty:
        st.warning("Nenhum filme similar encontrado.")
    else:
        for posicao, (_, filme) in enumerate(resultado.iterrows(), start=1):
            percentual = filme["Similaridade"] * 100

            with st.container(border=True):
                col_poster, col_info, col_score = st.columns([1, 4, 1])

                with col_poster:
                    poster = filme.get("Poster_Link", "")
                    if pd.notna(poster) and str(poster).strip():
                        st.image(poster, width=200)

                with col_info:
                    st.markdown(f"### #{posicao} — " f"{filme['Filme']}")
                    st.write(f"🎭 **Gênero:** " f"{filme['Genre']}")
                    st.write(f"🎬 **Diretor:** " f"{filme['Director']}")
                    st.write(f"👤 **Ator 1:** " f"{filme['Star1']}")
                    st.write(f"👤 **Ator 2:** " f"{filme['Star2']}")
                    st.write(f"📅 **Ano:** " f"{int(filme['Released_Year'])}")
                    st.write(f"⏱️ **Duração:** " f"{filme['Runtime']:.0f} min")
                    st.write(f"⭐ **IMDb:** " f"{filme['IMDB_Rating']}")
                    if pd.notna(filme["Meta_score"]):
                        st.write(f"🎯 **Meta Score:** " f"{filme['Meta_score']:.0f}")
                    else:
                        st.write("🎯 **Meta Score:** " "Não disponível")

                with col_score:
                    st.metric("Similaridade", f"{percentual:.2f}%")
