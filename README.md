# Dashboard Explorat\u00f3rio Vigitel com Streamlit e MongoDB

Aplicação interativa para exploração de microdados do Vigitel usando **Streamlit** no front-end e **MongoDB** como fonte de dados. O projeto foi estruturado para análise descritiva, com filtros dinâmicos, indicadores de IMC, sobrepeso e obesidade, além de visualizações por ano, cidade, sexo, faixa etária e escolaridade.

## Visão geral

O dashboard foi pensado para apoiar análises exploratórias de saúde pública a partir de microdados do Vigitel. A aplicação carrega os dados diretamente de uma collection no MongoDB, trata campos principais e permite calcular métricas simples ou ponderadas com base no campo `peso_amostral`.

### Funcionalidades

- Conexão com MongoDB usando `pymongo`
- Interface web com Streamlit
- Filtros por ano, cidade, sexo, faixa etária, escolaridade e categoria de IMC
- Cálculo de IMC médio
- Cálculo de prevalência de sobrepeso
- Cálculo de prevalência de obesidade
- Opção de ponderação por `peso_amostral`
- Gráficos interativos com Plotly
- Exportação da base filtrada em CSV

## Estrutura do projeto

```text
.
├── app.py
├── requirements.txt
└── .streamlit/
    └── secrets.toml
```

## Tecnologias utilizadas

| Tecnologia | Finalidade |
|---|---|
| Streamlit | Interface e execução do dashboard |
| MongoDB | Armazenamento dos microdados |
| PyMongo | Conexão Python com MongoDB |
| Pandas | Manipulação e transformação dos dados |
| Plotly | Visualizações interativas |

## Estrutura esperada dos dados

A collection do MongoDB deve conter documentos com estrutura semelhante à abaixo:

```json
{
  "_id": {"$oid": "69bb14bc3884adc347b996e2"},
  "ano": 2006,
  "cidade": 10,
  "peso_amostral": 593.0910034179688,
  "idade": 64,
  "faixa_idade": "55-64",
  "sexo_cod": 2,
  "sexo": "Feminino",
  "esc_anos": 5,
  "esc_grupo": "0-8 anos",
  "peso_kg": 73,
  "altura_cm": 166,
  "altura_m": 1.66,
  "imc": 26.491508201480624,
  "cat_imc": "Sobrepeso",
  "sobrepeso": 1,
  "obeso": 0
}
```

### Campos principais

| Campo | Descrição |
|---|---|
| `ano` | Ano da observação |
| `cidade` | Código da cidade/capital |
| `peso_amostral` | Peso amostral do registro |
| `idade` | Idade do entrevistado |
| `faixa_idade` | Faixa etária categorizada |
| `sexo_cod` / `sexo` | Sexo do entrevistado |
| `esc_anos` | Anos de estudo |
| `esc_grupo` | Grupo de escolaridade |
| `peso_kg` | Peso em quilogramas |
| `altura_cm` / `altura_m` | Altura em centímetros e metros |
| `imc` | Índice de massa corporal |
| `cat_imc` | Categoria de IMC |
| `sobrepeso` | Indicador binário de sobrepeso |
| `obeso` | Indicador binário de obesidade |

## Mapeamento de cidades

O projeto inclui o mapeamento das 27 localidades cobertas pelo Vigitel:

- Aracaju
- Belém
- Belo Horizonte
- Boa Vista
- Campo Grande
- Cuiabá
- Curitiba
- Florianópolis
- Fortaleza
- Goiânia
- João Pessoa
- Macapá
- Maceió
- Manaus
- Natal
- Palmas
- Porto Alegre
- Porto Velho
- Recife
- Rio Branco
- Rio de Janeiro
- Salvador
- São Luís
- São Paulo
- Teresina
- Vitória
- Distrito Federal

> Importante: o código numérico da variável `cidade` deve ser validado conforme o dicionário da base utilizada.

## Instalação

### 1. Clonar ou copiar o projeto

Coloque os arquivos `app.py` e `requirements.txt` em uma pasta local.

### 2. Criar ambiente virtual (opcional, mas recomendado)

```bash
python -m venv .venv
```

Ativar no Windows:

```bash
.venv\Scripts\activate
```

Ativar no Linux/macOS:

```bash
source .venv/bin/activate
```

### 3. Instalar dependências

```bash
pip install -r requirements.txt
```

## Configuração do MongoDB

Crie a pasta `.streamlit` na raiz do projeto e adicione o arquivo `secrets.toml`:

```toml
[mongo]
uri = "mongodb+srv://SEU_USUARIO:SUA_SENHA@cluster0.xxxxx.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0"
```

Se estiver usando MongoDB local, a URI pode ser algo como:

```toml
[mongo]
uri = "mongodb://localhost:27017/"
```

## Como executar

Com as dependências instaladas e o `secrets.toml` configurado, rode:

```bash
streamlit run app.py
```

Ao abrir a aplicação, informe no menu lateral:

- Nome do banco
- Nome da collection

Exemplo:

- Banco: `CD-IA`
- Collection: `Bdnr`

## Como o dashboard funciona

A aplicação:

1. Conecta ao MongoDB
2. Lê todos os documentos da collection informada
3. Converte os dados para `DataFrame`
4. Aplica tratamentos básicos de tipos
5. Cria o nome da cidade a partir do código
6. Disponibiliza filtros interativos na sidebar
7. Calcula indicadores simples ou ponderados
8. Exibe gráficos e tabela detalhada
9. Permite exportar a base filtrada em CSV

## Indicadores disponíveis

### Indicadores gerais

- Quantidade de registros filtrados
- IMC médio
- Prevalência de sobrepeso
- Prevalência de obesidade
- Peso médio

### Indicadores ponderados

Quando a opção de ponderação está ativada, os cálculos usam o campo `peso_amostral`.

Exemplo conceitual de prevalência ponderada:

```text
soma(indicador * peso_amostral) / soma(peso_amostral)
```

## Abas do dashboard

### 1. Visão geral

- Série temporal de obesidade por ano
- Ranking das cidades com maior prevalência de sobrepeso
- Distribuição por categoria de IMC
- Composição por sexo e categoria de IMC

### 2. Sexo

- Obesidade por sexo
- IMC médio por sexo

### 3. Faixa etária

- Sobrepeso por faixa etária
- Heatmap de obesidade por ano e faixa etária

### 4. Escolaridade

- Obesidade por escolaridade
- IMC médio por escolaridade

### 5. Microdados

- Tabela detalhada com os registros filtrados
- Download da base em CSV

## Possíveis melhorias

Algumas evoluções recomendadas para próximas versões:

- Validar automaticamente o mapeamento real do código de cidade
- Criar comparação entre dois anos específicos
- Adicionar ranking de capitais por obesidade
- Incluir filtros salvos ou presets de análise
- Criar tema claro/escuro customizado
- Adicionar textos automáticos com insights
- Publicar no Streamlit Community Cloud

## Observações

- O projeto é voltado para análise exploratória e descritiva.
- O desempenho dependerá do volume de documentos carregados do MongoDB.
- Para bases muito grandes, vale implementar paginação, agregações no MongoDB ou cache mais agressivo.

## Autor

Projeto desenvolvido para exploração de dados do Vigitel com foco em Streamlit, MongoDB e análise descritiva.
