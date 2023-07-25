import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import webbrowser

st.set_page_config(layout="wide")
#st.set_option('theme', base="light")


st.title("🗺️🎯 Map&Score 📚🚀")
st.subheader("Engenharia Cartográfica e de Agrimensura UFPR")

# Texto explicativo
st.write("Este dashboard foi criado para analisar os dados das turmas oferecidas por departamento e ano. "
         "Você pode utilizar os filtros na barra lateral para selecionar o ano e o departamento de interesse. "
         "Os gráficos apresentam informações sobre o rendimento acadêmico, número de matriculados, cancelados, "
         "aprovados e outras métricas relevantes. Explore os dados e descubra insights interessantes sobre as turmas!")

# Introdução
st.sidebar.title("Introdução")
st.sidebar.write("ℹ️ Este é um dashboard interativo que exibe informações sobre as turmas oferecidas por departamento e ano. "
                 "Use os filtros abaixo para explorar os dados.")

# Carregando os dados
turmas = pd.read_csv("DADOS ALUNOS/turmas.csv", sep=';', encoding='ISO-8859-1')
ofertas = pd.read_csv("DADOS CURSO/ofertas.csv", sep=';', encoding='ISO-8859-1')

turmas['semestre'] = pd.Series(['OP.']*len(turmas), name='semestre')
for i in range(len(ofertas)):
    mask = ofertas.codigo[i] == turmas.codigo
    turmas.loc[mask,'semestre'] = ofertas.semestre[i]

# Adicionar informação do semestre à string do código
turmas['codigo'] = turmas['semestre'].astype(str) + '-' + turmas['codigo']

# Opções para os filtros
# Filtrar por departamento
departamentos_disponiveis = ['Todos departamentos'] + turmas['departamento'].unique().tolist()
departamento_filtrado = st.sidebar.selectbox("Selecione um departamento:", departamentos_disponiveis)

if departamento_filtrado != 'Todos departamentos':
    turmas = turmas[turmas['departamento'] == departamento_filtrado]

# Filtrar por ano
anos_disponiveis = turmas['ano'].unique()
ano_filtrado = st.sidebar.selectbox("Selecione um ano:", anos_disponiveis)

if ano_filtrado:
    turmas = turmas[turmas['ano'] == ano_filtrado]

# Logo do curso
logo_curso_path = "IMAGEM/LOGO_TEXTO_VERTICAL.png"
# Logo do UFPR
logo_ufpr_path = "IMAGEM/LOGO_UFPR.png"

# Colocar as duas imagens lado a lado
col1, col2 = st.sidebar.columns(2)

# Inserir a primeira imagem na primeira coluna
col1.image(logo_curso_path, use_column_width=True)

# Inserir a segunda imagem na segunda coluna
col2.image(logo_ufpr_path, use_column_width=True)

st.sidebar.markdown("###### 👨‍💻 Developed by: Prof. Dr. Daniel Arana, Map&Ação")

# Gráfico de pizza
dados_ano = turmas.groupby('ano').agg({
    'aprovados': 'sum',
    'cancelados': 'sum',
    'reprovadosfrequencia': 'sum',
    'reprovadosnota': 'sum',
    'matriculados': 'sum',
    'total': 'sum',
    'vagasTotal': 'sum'
}).reset_index()

dados_ano = dados_ano.rename(columns={
    'matriculados': 'Matriculados',
    'cancelados': 'Cancelados',
    'aprovados': 'Aprovados',
    'reprovadosfrequencia': 'Repr. Frequência',
    'reprovadosnota': 'Repr. Nota',
    'total': 'Total',
    'vagasTotal': 'Vagas'
})

if ano_filtrado:
    dados_ano = dados_ano[dados_ano['ano'] == ano_filtrado]

atributos = ['Matriculados','Cancelados','Aprovados','Repr. Frequência','Repr. Nota']
valores = []
for i in atributos:
    valores.append(dados_ano[i].values[0])

# Definir as cores desejadas
corespi = ['rgb(305, 177,  64)', #laranja
           'rgb(198, 153, 239)',  #lilas
           'rgb( 94, 210,  94)', #verde
           'rgb(264,  89,  90)', #vermelho
           'rgb( 81, 169, 230)'] #azul

grafico_pizza = go.Pie(labels=['Matriculados','Cancelados','Aprovados','Repr. Frequência','Repr. Nota'],
                       values=valores,
                       marker=dict(colors=corespi))

layout = go.Layout(title='Dados globais do ano: %s' %ano_filtrado )

# Grafico de pizza
fig_pizza = go.Figure(data=[grafico_pizza], layout=layout)
st.plotly_chart(fig_pizza,use_container_width=True)

with st.expander("Fonte dos dados: SIGA."):
    st.write("O gráfico de pizza é configurado para exibir cinco categorias: Matriculados, Cancelados, Aprovados, Repr. Frequência (Reprovados por Frequência) e Repr. Nota (Reprovados por Nota). "
             "Neste contexto, ele pode ser usado para fornecer uma visão geral do desempenho acadêmico dos alunos, mostrando quantos estão matriculados, quantos foram aprovados, quantos foram reprovados por frequência, quantos foram reprovados por nota e quantos cancelaram a disciplina.")

#st.write("Fonte dos dados: SIGA", font='size': 10)


# Agrupando os dados para o gráfico de Rendimento Acadêmico
dados_agrupados = turmas.groupby('codigo').agg({
    'aprovados': 'sum',
    'cancelados': 'sum',
    'reprovadosfrequencia': 'sum',
    'reprovadosnota': 'sum',
    'matriculados': 'sum',
    'total': 'sum',
    'vagasTotal': 'sum'
}).reset_index()

dados_agrupados = dados_agrupados.rename(columns={
    'codigo': 'Código',
    'matriculados': 'Matriculados',
    'cancelados': 'Cancelados',
    'aprovados': 'Aprovados',
    'reprovadosfrequencia': 'Repr. Frequência',
    'reprovadosnota': 'Repr. Nota'
})

# Criar gráfico de barra com o número de matriculados por disciplina
fig_rendimento = px.bar(dados_agrupados,
                        x='Código',y=['Matriculados','Cancelados','Aprovados', 'Repr. Frequência', 'Repr. Nota'],
                        barmode='stack', title='Rendimento Acadêmico por Disciplina')

fig_rendimento.update_layout(legend={'x': 0.99, 'y': 0.99, 'xanchor': 'right', 'yanchor': 'top'})
fig_rendimento.update_yaxes(range=[0, 100])

# Definir as cores desejadas
cores = ['rgb(94, 210, 94)',
         'rgb(198, 153, 239)',
         'rgb(264, 89, 90)',
         'rgb(81, 169, 230)',
         'rgb(305, 177, 64)']

# Atualizar as cores das barras
for i, cor in enumerate(cores):
    fig_rendimento.update_traces(marker_color=cor, selector=dict(type='bar', name=dados_agrupados.columns[i+1]))

st.plotly_chart(fig_rendimento,use_container_width=True)
with st.expander("Fonte dos dados: SIGA."):
    st.write("O gráfico apresenta o rendimento acadêmico por disciplina, exibindo a distribuição proporcional dos resultados dos alunos em cada uma delas. Cada barra representa uma disciplina e é dividida em cinco segmentos, cada um correspondendo a uma categoria de rendimento: Matriculados, Cancelados, Aprovados, Reprovados por Frequência e Reprovados por Nota. "
             "A altura de cada barra representa o número total de alunos matriculados na disciplina, enquanto as cores dos segmentos representam a proporção de alunos com resultados acadêmicos diferentes."
             "O gráfico é interativo, permitindo ao usuário clicar sobre as categorias da legenda para habilitar ou desabilitar a exibição das barras correspondentes, o que possibilita uma análise mais detalhada das disciplinas específicas de interesse. "
             "Os número de 1 a 9 como prefixos aos códigos das disciplinas indicam o período de acordo com o  Projeto Pedagógico do Curso. O prefixo \"OP\" sinaliza as disciplinas optativas")

# Agrupando os dados para o gráfico de Rendimento %
matr = (dados_agrupados['Matriculados'] / dados_agrupados['total'])* 100
can = (dados_agrupados['Cancelados'] / dados_agrupados['total'])* 100
apr = (dados_agrupados['Aprovados'] / dados_agrupados['total'])* 100
ref = (dados_agrupados['Repr. Frequência'] / dados_agrupados['total'])* 100
ren = (dados_agrupados['Repr. Nota'] / dados_agrupados['total'])* 100

dados_agrupados_p = pd.DataFrame({
    'Código': dados_agrupados['Código'],
    'Matriculados': matr,
    'Cancelados': can,
    'Aprovados': apr,
    'Repr. Frequência': ref,
    'Repr. Nota': ren
})

# Criar gráfico de barra com o rendimento acadêmico em forma de porcentagem
fig_rendimento_p = px.bar(dados_agrupados_p,
                          x='Código',
                          y=['Matriculados','Cancelados','Aprovados', 'Repr. Frequência', 'Repr. Nota'],
                          barmode='stack',title='Rendimento Acadêmico em Porcentagem',
                          labels={'x': 'Código', 'y': 'Porcentagem', 'color': 'Variável'})

fig_rendimento_p.update_layout(barmode='stack')

# Atualizar as cores das barras
for i, cor in enumerate(cores):
    fig_rendimento_p.update_traces(marker_color=cor, selector=dict(type='bar', name=dados_agrupados.columns[i+1]))

st.plotly_chart(fig_rendimento_p,use_container_width=True)

with st.expander("Fonte dos dados: SIGA."):
    st.write("O gráfico apresenta o rendimento acadêmico em forma de porcentagem por disciplina, exibindo a proporção de alunos com diferentes resultados acadêmicos em relação ao número total de matriculados em cada disciplina. Cada barra representa uma disciplina e é dividida em cinco segmentos, cada um correspondendo a uma categoria de rendimento: Matriculados, Cancelados, Aprovados, Reprovados por Frequência e Reprovados por Nota. "
             "A altura de cada barra representa a porcentagem de alunos em relação ao total de matriculados na disciplina, possibilitando uma análise mais precisa do desempenho acadêmico. "
             "O gráfico é interativo, permitindo ao usuário clicar sobre as categorias da legenda para habilitar ou desabilitar a exibição das barras correspondentes, o que possibilita uma análise mais detalhada das disciplinas específicas de interesse. "
             "Os número de 1 a 9 como prefixos aos códigos das disciplinas indicam o período de acordo com o  Projeto Pedagógico do Curso. O prefixo \"OP\" sinaliza as disciplinas optativas")


# Agrupando os dados para o gráfico de Ocupação de Vaga

dados_ocup = pd.DataFrame({
    'Código': dados_agrupados['Código'],
    'Vagas ocupadas': dados_agrupados['total'],
    'Vagas não ocupadas': dados_agrupados['vagasTotal'] - dados_agrupados['total']
})

fig_ocupacao = px.bar(dados_ocup,
                      x='Código',
                      y=['Vagas ocupadas','Vagas não ocupadas'],
                      barmode='stack',title='Ocupação de vagas em disciplinas',
                      labels={'x': 'Código', 'y': 'Número de vagas', 'color': 'Variável'})

fig_ocupacao.update_layout(barmode='stack')
fig_ocupacao.update_layout(legend={'x': 0.99, 'y': 0.99, 'xanchor': 'right', 'yanchor': 'top'})
fig_ocupacao.update_yaxes(range=[0, 100])

# Definir as cores desejadas
coresi = ['rgb(81, 169, 230)',
         'rgb(264, 89, 90)']

# Atualizar as cores das barras
for i, cor in enumerate(coresi):
    fig_ocupacao.update_traces(marker_color=cor, selector=dict(type='bar', name=dados_ocup.columns[i+1]))

st.plotly_chart(fig_ocupacao,use_container_width=True)

with st.expander("Fonte dos dados: SIGA."):
    st.write("O gráfico exibe a ocupação de vagas em disciplinas do curso de Engenharia Cartográfica e de Agrimensura da UFPR. "
             "Cada barra representa uma disciplina e é dividida em dois segmentos, sendo um correspondente ao número de vagas ocupadas e outro ao número de vagas não ocupadas. "
             "A altura de cada barra representa a quantidade de vagas em cada categoria, possibilitando a visualização clara da proporção de vagas ocupadas e não ocupadas em cada disciplina. "
             "O gráfico é interativo e permite ao usuário clicar sobre as categorias da legenda para habilitar ou desabilitar a exibição das barras correspondentes, possibilitando uma análise mais detalhada das disciplinas específicas de interesse. "
             "Os número de 1 a 9 como prefixos aos códigos das disciplinas indicam o período de acordo com o  Projeto Pedagógico do Curso. O prefixo \"OP\" sinaliza as disciplinas optativas")


# Botão para direcionar o usuário à página do curso
st.write('Clique no botão abaixo para acessar a página do curso:')
if st.button('Página do Curso'):
    # Redirecionar o usuário para a página do curso
    import webbrowser
    webbrowser.open('https://cartografica.ufpr.br')
