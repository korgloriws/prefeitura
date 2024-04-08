import streamlit as st

from balancete_vs_ctb.comparador_2 import main as main1
from leitor_de_pdf.leitorDePdf import main as main2
from rec_vs_qgr.index import main as main3
from balanceteCamara_vs_balanceteSicof.server import main as main4
from consorcio.consorcio import main as main5
from posicao_de_bancos_vs_ctb.index import main as main6
from balanceteSicof_VS_balanceteSicon.index import main as main7
from dedCamara_VS_dedSicof.index import main as main8
from restos_a_pagar.index import main as main9
from despesa_de_pessoal.main import main as main10
from comparadorCD.comparador import main as main11
from cismep.cismep import main as main12
from comparador_Ar.comparadorCsv2 import main as main13
from fundeb.main import main as main14
from Formulario_credor.main import main as main15
from demonstrativo_da_saude.main import main as main16 
from somatorio_ctb.main import main as main17
from mde.main import main as main18
from corretorMatriz.main import main as main20
from comparador_emp.main import main as main21
from matriz_vs_balancete.main import main as main22
from lqd.main import main as main23
from rreo_07.main import main as main24
from rreo_07.comparador.comparador import main as main25
from rreo_02.comparador.comparador import main as main26
from rreo_02.main import main as main27
from rreo_03.main import main as main28
from rreo_03.comparador.comparador import main as main29
from rreo_01.main import main as main30
from rreo_01.comparador.comparador import main as main31 
from rreo_04.main import main as main32
from rreo_04.comparador.comparador import main as main33
from receita_corrente_liquida.main import main as main34
from rgf_02.main import main as main35
from rgf_02.comparador.comaparador import main as main36

categorias_programas = {
    'Aplicativos de contabilidade': ['precatório','balanceteCamara_vs_balanceteSicof','dedCamara_VS_dedSicof','restos_a_pagar','comparadorCD','Formulario_credor'],
    'Aplicativos de prestação de contas': ['Balancete vs CTB','REC vs QGR', 'posicao_de_bancos_vs_ctb','balanceteSicof_VS_balanceteSicon','despesa_de_pessoal','comparador_Ar','fundeb','demonstrativo_da_saude','somatorio_ctb','mde','corretorMatriz', 'matriz_vs_balancete','receita_corrente_liquida'],
    'Aplicativos AM': ['consorcio','cismep', 'comparador_emp','lqd'],
    'RREO': ['rreo_07',"rreo_07\\comparador","rreo_02\\comparador","rreo_02","rreo_03",'rreo_03\\comparador',"rreo_01",'rreo_01\\comparador','rreo_04',"rreo_04\\comparador"],
    'RGF': ['rgf_02','rgf_02\\comparador',]
}

st.sidebar.markdown("# *Aplicativos da superintendências (^_^)/*")

categoria_selecionada = st.sidebar.selectbox('Escolha a categoria', [''] + list(categorias_programas.keys()))

programa_selecionado = ''
if categoria_selecionada != '':
    programa_selecionado = st.sidebar.radio('Escolha o programa', categorias_programas[categoria_selecionada])


if not programa_selecionado:
    st.markdown("## Bem-vindo(a) aos Aplicativos das Superintendências!")
    st.markdown("Por favor, selecione uma categoria e um programa no menu ao lado para começar.")




programas_funcoes = {
    'Balancete vs CTB': main1,
    'precatório': main2,
    'REC vs QGR': main3,
    'balanceteCamara_vs_balanceteSicof': main4,
    'consorcio': main5,
    'posicao_de_bancos_vs_ctb': main6,
    'balanceteSicof_VS_balanceteSicon': main7,
    'dedCamara_VS_dedSicof': main8,
    'restos_a_pagar': main9,
    'despesa_de_pessoal': main10,
    'comparadorCD': main11,
    'cismep': main12,
    'comparador_Ar': main13,
    'fundeb': main14,
    'Formulario_credor': main15,
    'demonstrativo_da_saude': main16,
    'somatorio_ctb': main17,
    'mde': main18,
    'corretorMatriz': main20,
    'comparador_emp': main21,
    'matriz_vs_balancete': main22,
    'lqd': main23,
    'rreo_07': main24,
    'rreo_07\\comparador': main25,
    'rreo_02\\comparador': main26,
    'rreo_02': main27,
    'rreo_03': main28,
    'rreo_03\\comparador': main29,
    'rreo_01': main30,
    'rreo_01\\comparador': main31,
    'rreo_04': main32,
    'rreo_04\\comparador':main33,
    'receita_corrente_liquida': main34,
    'rgf_02' : main35,
    'rgf_02\\comparador': main36,
}

if programa_selecionado and programa_selecionado in programas_funcoes:
    programas_funcoes[programa_selecionado]()
