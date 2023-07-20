import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

st.title("MapScore")
st.subheader("Engenharia Cartográfica e de Agrimensura UFPR")

st.sidebar.text("Opções de filtro")

# Estatísticas das turmas: taxa de aprovação, reprovação (nota e frequência)
turmas = pd.read_csv("DADOS ALUNOS/turmas.csv", sep=';', encoding='ISO-8859-1')

ofertas = pd.read_csv("DADOS CURSO/ofertas.csv", sep=';', encoding='ISO-8859-1')

turmas['semestre'] = pd.Series(['OP.']*len(turmas), name='semestre')
for i in range(len(ofertas)):
    mask = ofertas.codigo[i] == turmas.codigo
    turmas.loc[mask,'semestre'] = ofertas.semestre[i]

# Adicionar informação do semestre à string do código
turmas['codigo'] = turmas['semestre'].astype(str) + '-' + turmas['codigo']

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

fig_pizza = go.Figure(data=[grafico_pizza], layout=layout)

#grafico_pizza = px.pie(dados_ano)
st.plotly_chart(fig_pizza)

#st.dataframe(turmas)


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
