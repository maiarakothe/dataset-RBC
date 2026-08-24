# RBC de Filmes

## Sobre o projeto

Este projeto implementa um sistema de **Raciocínio Baseado em Casos (RBC)** para encontrar filmes parecidos com um filme escolhido.

O sistema utiliza o dataset `imdb_top_1000.csv`. O filme escolhido é comparado com os outros filmes do dataset e cada comparação gera uma porcentagem de similaridade. No final, são mostrados os 5 filmes mais similares.

## Como funciona

Primeiro, os dados são carregados e tratados. O ano e a duração são convertidos para números e os valores numéricos são normalizados entre 0 e 1.

Depois, o filme escolhido é comparado com todos os outros filmes utilizando diferentes atributos. Cada atributo possui um peso de acordo com sua importância para a comparação.

A similaridade final é calculada através de uma **média ponderada**.

## Dados utilizados

Foram escolhidos os seguintes atributos:

| Atributo      | Tipo       | Método                | Peso |
| ------------- | ---------- | --------------------- | ---: |
| Genre         | Categórico | Jaccard               |    3 |
| Director      | Categórico | Igualdade             |    2 |
| IMDb Rating   | Numérico   | Similaridade numérica |    2 |
| Meta Score    | Numérico   | Similaridade numérica |    1 |
| Released Year | Numérico   | Similaridade numérica |    1 |
| Runtime       | Numérico   | Similaridade numérica |    1 |
| Star1         | Categórico | Igualdade             |    2 |
| Star2         | Categórico | Igualdade             |    1 |

### Gênero

O gênero recebeu peso **3** porque é um dos principais fatores usados para identificar filmes semelhantes.

### Diretor

O diretor recebeu peso **2**. Se os dois filmes possuem o mesmo diretor, a similaridade desse atributo é 1. Caso contrário, é 0.

### IMDb

A nota do IMDb recebeu peso **2**. Como é um valor numérico, os valores são normalizados e comparados pela distância entre eles.

### Meta Score

O Meta Score recebeu peso **1** e também utiliza a comparação numérica normalizada.

### Ano

O ano de lançamento recebeu peso **1**. Filmes com anos próximos possuem maior similaridade nesse atributo.

### Duração

A duração recebeu peso **1**. Filmes com duração próxima possuem maior similaridade.

### Atores

`Star1` recebeu peso **2** e `Star2` recebeu peso **1**.

A comparação verifica se o ator é o mesmo nos dois filmes.


## Dados que não foram utilizados

O dataset possui outras informações que não foram utilizadas no cálculo da similaridade.

Entre elas estão:

* `Poster_Link`
* `Series_Title`
* `Overview`
* `Certificate`
* `Gross`
* `No_of_Votes`
* `Star3`
* `Star4`


`Series_Title` é utilizado apenas para identificar o filme, mas não participa do cálculo.

`Poster_Link` não foi utilizado porque a imagem do filme não ajuda diretamente no cálculo da similaridade.

`Overview` também não foi utilizado porque seria necessário aplicar técnicas de processamento de texto para comparar as descrições.

`Certificate` não foi utilizado porque a classificação indicativa não foi considerada relevante para definir se dois filmes são parecidos.

`Gross` e `No_of_Votes` também ficaram de fora porque representam principalmente informações comerciais e de popularidade, e não características do conteúdo do filme.

Para rodar:
`streamlit run interface.py`
