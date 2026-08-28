# RBC de Filmes

## Sobre o projeto

Este projeto implementa um sistema de **Raciocínio Baseado em Casos (RBC)** para encontrar filmes parecidos com um filme escolhido pelo usuário.

O sistema utiliza o dataset `imdb_top_1000.csv`. O filme escolhido é comparado com os outros filmes do dataset e cada comparação gera uma porcentagem de similaridade.

O projeto também implementa o ciclo completo dos **4 Rs do RBC**:

- **Recuperar:** encontra os filmes mais semelhantes.
- **Reutilizar:** utiliza o filme mais semelhante como recomendação.
- **Revisar:** permite que o usuário avalie a recomendação.
- **Reter:** armazena a avaliação para influenciar recomendações futuras.

A interface foi desenvolvida utilizando **Streamlit**.

## Como funciona

Primeiro, os dados são carregados e tratados. O ano e a duração são convertidos para números e os valores numéricos são normalizados entre 0 e 1.

A classificação indicativa também é convertida para uma idade aproximada e normalizada.

As sinopses dos filmes são transformadas utilizando **TF-IDF** e comparadas através da **similaridade do cosseno**.

Depois, o filme escolhido é comparado com todos os outros filmes utilizando diferentes atributos. Cada atributo possui um peso de acordo com sua importância.

A similaridade final é calculada através de uma **média ponderada**.

## Dados utilizados

| Atributo | Método | Peso |
|---|---|---:|
| Genre | Jaccard | 3 |
| Director | Igualdade | 2 |
| Released Year | Similaridade numérica | 1 |
| Runtime | Similaridade numérica | 1 |
| Certificate | Similaridade numérica | 2 |
| Star1 | Igualdade | 2 |
| Star2 | Igualdade | 1 |
| Overview | TF-IDF + cosseno | 3 |

### Gênero

O gênero recebeu peso **3** e é comparado utilizando o **índice de Jaccard**, pois um filme pode possuir mais de um gênero.

### Diretor

O diretor recebeu peso **2**. Se os dois filmes possuem o mesmo diretor, a similaridade é 1; caso contrário, é 0.

### Ano e duração

`Released_Year` e `Runtime` recebem peso **1** cada.

Os valores são normalizados entre 0 e 1. Quanto mais próximos forem os valores, maior será a similaridade.

### Classificação

`Certificate` recebe peso **2**. As classificações indicativas são convertidas para uma idade aproximada e depois normalizadas.

### Atores

`Star1` recebe peso **2** e `Star2` recebe peso **1**.

A comparação verifica se o ator é o mesmo nos dois filmes.

### Sinopse

`Overview` recebe peso **3**.

As sinopses são transformadas em vetores utilizando **TF-IDF** e comparadas através da **similaridade do cosseno**.

## Dados que não foram utilizados

Algumas informações do dataset não participam diretamente do cálculo da similaridade:

- `Series_Title` – utilizado apenas para identificar o filme;
- `Poster_Link` – utilizado somente para exibir o pôster na interface;
- `Gross`;
- `No_of_Votes`;
- `Star3`;
- `Star4`;
- `IMDb_Rating`;
- `Meta_Score`;

## Experiências Retidas

As avaliações realizadas pelo usuário são armazenadas no arquivo:

```text
casos_rbc.csv
```

Quando uma recomendação possui uma avaliação anterior:
* **Avaliação positiva:** aumenta o `Score_RBC` em **2%**.
* **Avaliação negativa:** reduz o `Score_RBC` em **2%**.

Assim, experiências anteriores podem influenciar a ordem das recomendações futuras.

---

## Instalação e Execução

Para instalar as bibliotecas necessárias, execute:

```bash
pip install -r requirements.txt
```

Para executar o sistema:

```bash
streamlit run interface.py
```
