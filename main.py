import pandas as pd
from dash import Dash, html, dcc
import plotly.express as px
import dash

import numpy as np

colors = {
    'background': 'white',
    'text': '#004AAD'
}

# Estatísticas das turmas: taxa de aprovação, reprovação (nota e frequência)
turmas = pd.read_csv("DADOS ALUNOS/turmas.csv", sep=';', encoding='ISO-8859-1')

ofertas = pd.read_csv("DADOS CURSO/ofertas.csv", sep=';', encoding='ISO-8859-1')

turmas['semestre'] = pd.Series(['OP.']*len(turmas), name='semestre')
for i in range(len(ofertas)):
    mask = ofertas.codigo[i] == turmas.codigo
    turmas.loc[mask,'semestre'] = ofertas.semestre[i]

# Adicionar informação do semestre à string do código
turmas['codigo'] = turmas['semestre'].astype(str) + '-' + turmas['codigo']

#turmas.sort_values(by=['semestre','ano'],ascending=False, inplace=True)
turmas_sorted = turmas.sort_values(by=['semestre','ano', 'codigo'], ascending=[False, False, True])
#turmas.sort_values(by='ano',ascending=False, inplace=True)

turmas['departamento'] = turmas['departamento'].replace({
    'Departamento de Expressão Gráfica': 'Expressão Gráfica',
    'Departamento de Física':'Física',
    'Departamento de Geografia':'Geografia',
    'Departamento de Geologia':'Geologia',
    'Departamento de Geomática':'Geomática',
    'Departamento de Hidráulica e Saneamento': 'Hidráulica e Saneamento',
    'Departamento de Informática':'Informática',
    'Departamento de Matemática':'Matemática',
    'Departamento de Transportes':'Transportes',
    'Departamento de Estatística':'Estatística',
})


# Opções para os filtros
anos_disponiveis = turmas['ano'].unique()
departamentos_disponiveis = ['Todos departamentos'] + turmas['departamento'].unique().tolist()

# Criar a aplicação Dash
app = dash.Dash(__name__)

# Alterar estilo do texto
text_style = {
    'fontFamily': 'Arial, sans-serif',
    'fontSize': '24px',
    'fontWeight': 'bold',
    'textAlign': 'center',
    'color': colors['text']
}

# Alterar estilo do contêiner
container_style = {
    'backgroundColor': colors['background'],
    'padding': '20px',
    'borderRadius': '5px',
    'boxShadow': '0 2px 5px rgba(0, 0, 0, 0.1)'
}

# Criar gráfico de barra com o número de matriculados por disciplina
fig_matriculados = px.bar(turmas, x='codigo', y='matriculados', title='Número de Matriculados por Disciplina')

fig_matriculados.update_layout(
    font_color=colors['text'],
    legend={'x': 1, 'y': 1, 'xanchor': 'right', 'yanchor': 'top'}
)

# Criar gráfico de barra com o rendimento acadêmico em forma de porcentagem
fig_rendimento_porcentagem = px.bar(turmas, x='codigo', y=(turmas['aprovados'] / turmas['total']) * 100,
                                    title='Rendimento Acadêmico em Porcentagem')

fig_rendimento_porcentagem.update_layout(
    font_color=colors['text'],
    legend={'x': 1, 'y': 1, 'xanchor': 'right', 'yanchor': 'top', 'orientation': 'v'}
)

# Criar gráfico de barra com a porcentagem de ocupação de vagas
fig_ocupacao_vagas = px.bar(turmas, x='codigo', y='vagasTotal',
                            title='Ocupação de vagas em disciplinas')

fig_ocupacao_vagas.update_layout(
    font_color=colors['text'],
    legend={'x': 1, 'y': 1, 'xanchor': 'right', 'yanchor': 'top', 'orientation': 'v'}
)

# Layout da aplicação
app.layout = html.Div(
    children=[
        html.H1(
            children='MapScore: Eng. Cartográfica e de Agrimensura UFPR',
            style={'fontFamily': 'Arial, sans-serif', **text_style}
        ),
        html.Div(
            style={'display': 'flex'},
            children=[
                html.Div(
                    style={'width': '85%'},
                    children=[
                        dcc.Graph(id='rendimento-matriculados', figure=fig_matriculados)
                    ]
                ),
                html.Div(
                    style={'width': '15%'},
                    children=[
                        html.P('--', style={'fontSize': '20px', 'fontFamily': 'Arial, sans-serif','color': colors['background']}),
                        html.P('--', style={'fontSize': '20px', 'fontFamily': 'Arial, sans-serif','color': colors['background']}),
                        html.P('Opções de filtro', style={'fontSize': '20px', 'fontFamily': 'Arial, sans-serif'}),
                        html.Label('Selecione os Departamentos:', style={'fontSize': '12px', 'fontFamily': 'Arial, sans-serif'}),
                        dcc.Checklist(
                            id='departamento-checklist',
                            options=[{'label': departamento, 'value': departamento} for departamento in departamentos_disponiveis],
                            value=[departamentos_disponiveis[0]],  # Atualize para uma lista contendo a opção "Todos departamentos"
                            style={'display': 'block', 'flexWrap': 'wrap', 'fontSize': '12px', 'fontFamily': 'Arial, sans-serif'}
                        ),
                        html.P('Selecione o Ano:', style={'fontSize': '12px', 'fontFamily': 'Arial, sans-serif'}),
                        dcc.Dropdown(
                            id='ano-dropdown',
                            options=[{'label': str(ano), 'value': ano} for ano in anos_disponiveis],
                            value=anos_disponiveis[0],
                            style={'width': '100px', 'margin': '0 auto', 'fontSize': '12px', 'fontFamily': 'Arial, sans-serif'}
                        )
                    ]
                )
            ]
        ),
        dcc.Graph(id='rendimento-porcentagem', figure=fig_rendimento_porcentagem),
        dcc.Graph(id='ocupacao-vagas', figure=fig_ocupacao_vagas)
    ]
)


@app.callback(
    dash.dependencies.Output('rendimento-matriculados', 'figure'),
    [dash.dependencies.Input('ano-dropdown', 'value'),
     dash.dependencies.Input('departamento-checklist', 'value')]
)
def update_grafico_matriculados(ano_selecionado, departamentos_selecionados):
    if 'Todos departamentos' in departamentos_selecionados:
        dados_filtrados = turmas[turmas['ano'] == ano_selecionado]
    else:
        dados_filtrados = turmas[(turmas['ano'] == ano_selecionado) & (turmas['departamento'].isin(departamentos_selecionados))]

    dados_agrupados = dados_filtrados.groupby('codigo').agg({
        'aprovados': 'sum',
        'cancelados': 'sum',
        'reprovadosfrequencia': 'sum',
        'reprovadosnota': 'sum',
        'matriculados': 'sum'
    }).reset_index()

    dados_agrupados = dados_agrupados.rename(columns={
        'codigo': 'Código',
        'matriculados': 'Matriculados',
        'cancelados': 'Cancelados',
        'aprovados': 'Aprovados',
        'reprovadosfrequencia': 'Repr. Frequência',
        'reprovadosnota': 'Repr. Nota'
    })
    fig = px.bar(dados_agrupados,
                 x='Código',
                 y=['Matriculados','Cancelados','Aprovados', 'Repr. Frequência', 'Repr. Nota'],
                 barmode='stack', title='Rendimento Acadêmico por Disciplina')
    fig.update_layout(barmode='stack')
    fig.update_layout(legend={'x': 0.99, 'y': 0.99, 'xanchor': 'right', 'yanchor': 'top'})
    fig.update_yaxes(range=[0, 100])

    return fig

@app.callback(
    dash.dependencies.Output('rendimento-porcentagem', 'figure'),
    [dash.dependencies.Input('ano-dropdown', 'value'),
     dash.dependencies.Input('departamento-checklist', 'value')]
)
def update_grafico_porcentagem(ano_selecionado, departamentos_selecionados):
    if 'Todos departamentos' in departamentos_selecionados:
        dados_filtrados = turmas[turmas['ano'] == ano_selecionado]
    else:
        dados_filtrados = turmas[(turmas['ano'] == ano_selecionado) & (turmas['departamento'].isin(departamentos_selecionados))]

    dados_agrupados = dados_filtrados.groupby('codigo').agg({
        'aprovados': 'sum',
        'cancelados': 'sum',
        'reprovadosfrequencia': 'sum',
        'reprovadosnota': 'sum',
        'matriculados': 'sum',
        'total': 'sum'
    }).reset_index()

    matr = (dados_agrupados['matriculados'] / dados_agrupados['total'])* 100
    can = (dados_agrupados['cancelados'] / dados_agrupados['total'])* 100
    apr = (dados_agrupados['aprovados'] / dados_agrupados['total'])* 100
    ref = (dados_agrupados['reprovadosfrequencia'] / dados_agrupados['total'])* 100
    ren = (dados_agrupados['reprovadosnota'] / dados_agrupados['total'])* 100

    dados_agrupados_p = pd.DataFrame({
        'Código': dados_agrupados['codigo'],
        'Matriculados': matr,
        'Cancelados': can,
        'Aprovados': apr,
        'Repr. Frequência': ref,
        'Repr. Nota': ren
    })

    fig = px.bar(dados_agrupados_p,
                 x='Código',
                 y=['Matriculados','Cancelados','Aprovados', 'Repr. Frequência', 'Repr. Nota'],
                 barmode='stack',title='Rendimento Acadêmico em Porcentagem',
                 labels={'x': 'Código', 'y': 'Porcentagem', 'color': 'Variável'})
    fig.update_layout(barmode='stack')

    return fig

@app.callback(
    dash.dependencies.Output('ocupacao-vagas', 'figure'),
    [dash.dependencies.Input('ano-dropdown', 'value'),
     dash.dependencies.Input('departamento-checklist', 'value')]
)
def update_grafico_ocupacao(ano_selecionado, departamentos_selecionados):
    if 'Todos departamentos' in departamentos_selecionados:
        dados_filtrados = turmas[turmas['ano'] == ano_selecionado]
    else:
        dados_filtrados = turmas[(turmas['ano'] == ano_selecionado) & (turmas['departamento'].isin(departamentos_selecionados))]

    dados_agrupados = dados_filtrados.groupby('codigo').agg({
        'total': 'sum',
        'vagasTotal': 'sum',
    }).reset_index()

    dados_ocup = pd.DataFrame({
        'Código': dados_agrupados['codigo'],
        'Vagas ocupadas': dados_agrupados['total'],
        'Vagas não ocupadas': dados_agrupados['vagasTotal'] - dados_agrupados['total']
    })

    fig = px.bar(dados_ocup,
                 x='Código',
                 y=['Vagas ocupadas','Vagas não ocupadas'],
                 barmode='stack',title='Ocupação de vagas em disciplinas',
                labels={'x': 'Código', 'y': 'Número de vagas', 'color': 'Variável'})
    fig.update_layout(barmode='stack')
    fig.update_layout(legend={'x': 0.99, 'y': 0.99, 'xanchor': 'right', 'yanchor': 'top'})
    fig.update_yaxes(range=[0, 100])

    return fig


# Executar a aplicação
if __name__ == '__main__':
    app.run_server(debug=True)
