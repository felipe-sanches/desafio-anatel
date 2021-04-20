#!/usr/bin/python3

# importar as bibliotecas necessárias
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import streamlit as st
from datetime import datetime

#importando base de dados para o dataframe
df = pd.read_csv('https://raw.githubusercontent.com/felipe-sanches/desafio-anatel/main/Base%20de%20dados%20final.xlsx%20-%20Sheet1.csv')


#Convertendo a coluna Data Entrega para o tipo datetime
df['Data Entrega'] = pd.to_datetime(df['Data Entrega'])

#Trocando virgulas por pontos e convertendo a coluna Pontuação para o tipo Float 
df['Pontuação'] = df['Pontuação'].str.replace(',', '.')
df['Pontuação'] = df['Pontuação'].astype(float)


#Título e descrição em Texto
st.title('Desafio - Processo Seletivo ANATEL')

st.markdown(
    """
    Este Dashboard interativo reflete a Análise de Dados feita para o Processo Seletivo da Anatel.
    Código-fonte disponível no meu [Portfólio no Github](https://github.com/felipe-sanches/data_science)

    -
    """
)


st.header('Proporção de Fiscais em análise de atv. centralizada')

lotacao = df['Unidade de Lotação'].unique()

#Filtrando os ficais
fiscais = df.loc[df['Unidade de Lotação'] != 'FIGF']

#filtrando entre os registros total dos fiscais, quais registros são de análises
analise = fiscais.loc[fiscais['Tipo de Ação'] == 'Análise']


#definindo quais sao as atividades centralizadas
centr = analise[analise['Atividades'].str.contains("SERV")]
centr = centr[centr['Atividades'].str.contains("entr")]
centr1= centr[centr['Atividades'].str.contains("SERV_08")]

result = centr.loc[centr.index.difference(centr1.index)]

total = fiscais['Usuários'].unique()
atvcentr = result['Usuários'].unique()

# Grafico de Pizza apresentando a proporção
labels = 'Total de fiscais', 'Fiscais atv centralizada'
sizes = [len(total), len(atvcentr)]
explode = (0, 0.1)  

fig, ax1 = plt.subplots(figsize = (10,6))
ax1.pie(sizes, explode=explode, labels=labels, autopct='%1.1f%%',shadow=True, startangle=90)
ax1.axis('equal')
st.pyplot(fig)

st.write('-')
st.header('Usuários com maior Pontuação')

#Definindo input de data inicial e final 
data_inicio = st.date_input('Selecione a Data Inicial', value = df['Data Entrega'].min() ,min_value= df['Data Entrega'].min(), max_value=df['Data Entrega'].max())
data_final = st.date_input('Selecione a Data Final', value = df['Data Entrega'].max() ,min_value= df['Data Entrega'].min(), max_value=df['Data Entrega'].max())

if data_final > data_inicio:
    periodo = df.loc[(df['Data Entrega'] > pd.to_datetime(data_inicio)) & (df['Data Entrega'] <= pd.to_datetime(data_final))]
else:
    st.error('Selecione uma data Final maior do que a Inicial')

#agrupando os usuarios segundo o periodo definido pelo usuario
soma = periodo['Pontuação'].groupby(periodo['Usuários']).sum()
score = soma.sort_values(ascending= True).tail(10)

st.write("Ranking Pontuação de Usuários de ", data_inicio,"a", data_final)


#Plotando gráfico
fig, ax = plt.subplots(figsize=(10,6))

score.plot(x="Usuários", y= "Pontuação", kind="barh", ax=ax)

ax.set_xlabel("Pontuação")
ax.set_ylabel("Usuários")
ax.legend()

for index, value in enumerate(score):
    plt.text(value, index, str(value))

st.pyplot(fig)


#Encontrando a unidade que mais pontuou
agrupapont = df['Pontuação'].groupby(df['Unidade de Lotação']).sum()
ordenapont = agrupapont.sort_values(ascending= False).head(10)

vis3 = df.loc[df['Unidade de Lotação'] == ordenapont.index[0]]
nome = ordenapont.index[0]

st.write('-')
st.header('Unidade com maior Pontuação em todo o período: ' +  nome)

lotacao = np.append(lotacao,'-')

#st.write(lotacao[1].type)

option = st.selectbox('Escolha a Unidade de Lotação que deseja comparar:',(lotacao), index = (len(lotacao)-1))

df2 = df.loc[df['Unidade de Lotação'] == option]
df2['Data Entrega'] = df2['Data Entrega'].dt.strftime('%Y-%m')


#tratando a variavel 'Data Entrega'
vis3['Data Entrega'] = vis3['Data Entrega'].dt.strftime('%Y-%m')


#mudando nome da coluna que sera exibido na legenda
vis3 = vis3.rename(columns={'Atividades': nome})
df2 = df2.rename(columns={'Atividades': option})


#Agrupando contagem de atividades por mes
maiorpont = vis3[nome].groupby(vis3['Data Entrega']).count()
comparado = df2[option].groupby(df2['Data Entrega']).count()


# plotando gráfico de analise 
fig1, ax = plt.subplots(nrows=1, ncols=1, figsize=(10,4))

maiorpont.plot(kind="line",ax=ax)
comparado.plot(kind="line",ax=ax)

ax.legend()
ax.set_xlabel("Mês")
ax.set_ylabel("Quant. Atividades")
ax.set_title("Atividades por mês")
plt.xticks(range(0,len(maiorpont.index)), maiorpont.index, rotation = 45)


st.pyplot(fig1)