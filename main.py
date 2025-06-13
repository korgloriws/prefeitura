import streamlit as st


from balancete_vs_ctb.comparador_2 import main as main1 # VV
from leitor_de_pdf.precatorio import main as main2 # VV
from rec_vs_qgr.index import main as main3 #VV
from balanceteCamara_vs_balanceteSicof.server import main as main4 # VV
from consorcio.consorcio import main as main5 #VV
from posicao_de_bancos_vs_ctb.mainLinux import main as main6 #VV 
from balanceteSicof_VS_balanceteSicon.index import main as main7 # XX
from dedCamara_VS_dedSicof.index import main as main8 # VV
from restos_a_pagar.index import main as main9 #VV
from despesa_de_pessoal.main import main as main10 #VV
from comparadorCD.comparador import main as main11 #XX
from cismep.cismep import main as main12 # VV
#from comparador_Ar.main4 import main as main13
from fundeb.mainLinux import main as main14 #VV
#from Formulario_credor.mainLinux import main as main15 
from demonstrativo_da_saude.mainLinux import main as main16 #VV
from somatorio_ctb.main import main as main17 #VV
from mde.main import main as main18 #vv
from corretorMatriz.teste4 import main as main20 #VV
from comparador_emp.main import main as main21 #VV
from matriz_vs_balancete.teste4 import main as main22 # VV
from lqd.main import main as main23 #VV
from receita_corrente_liquida.main import main as main24 #VV
from anl.main import main as main25 ##VV
from ddr.main import main as main26 
#from execucaoOrcamentariaEFinanceira.mainLinux import main as main27 
from msc_ctb.index import main as main28 #VV
from tradutor_msc_ctb.tradutor import main as main29 #VV
from rec_vs_ementarioDaRceita.main import main as main30 #VV 
from fontes_co.main import main as main31
from somatorioMscBancoContaFonte.index3 import main as main32
from comparacao_saldo_encerramento.main import main as main33
from totalizador_ctb_fonte.main import main as main34
from depositos_judiciais.main import main as main35 
from relacao_trabalhadores_fgts.mainLinux import main as main36
from extrator_valor_nota_produto.main import main as main38
from comparador_de_pcasps.main import main as main39 # VV
from posicaoFonte_vs_msc.app import main as main40
from nota_servico_sepat.extrator_nfse import main as main41 





categorias_programas = {
    'Módulo da Contabilidade': {
        'Geradores De relatórios': ['Precatório', #'Formulário de credor / IR RFB',
        'Comparação dos saldos de encerramento','Comparador de PCASPs'],
        'Conciliações Mensais': ['Balancete da Câmara VS o Balancete do SICOF', 'DED Câmara VS DED SICOF', 'REC VS QGR', 'Restos a pagar Câmara VS SICOF',
        'Comparador crédito e débito', 'DDR'],
    },
    'Módulo de prestação de contas': {
        
        'Matriz': ['Corretor da Matriz', 'Matriz VS balancete', 'Corretor da MSC para o CTB', 'Matriz VS CTB','Somatório da matriz por Banco conta e fonte'],
        'Conciliações Mensais': [ 'Balancete Sicof VS balancete Sicon', 'Despesa com Pessoal', #'Execucão orcamentária e financeira', 
        'Balancete VS CTB', 'FUNDEB', #'Comparador Ar',
        'MDE', 'Receita corrente líquida','Demonstrativo da saúde', 'Posição de Bancos por Fonte VS MSC'],
        'Demais Conciliações': ['Somatório do CTB por orgãos','Totalizador do CTB por fonte',#'Posição de Bancos VS Matriz'
                                ],
        'Módulo AM': ['Consórcio das Mulheres', 'ICISMEP', 'Comparador do EMP', 'ANL'],
    },

    'Módulo Superintendencia de Finanças':{
       'Conciliações Mensais Receita': ['REC VS QGR', 'Rec VS ementário da receita', 'Fontes co','Posição de Bancos VS CTB','Depósitos judicias',],
       'Módulo AM': [ 'LQD' ],
       'Inspeção Financeira':["Relacão de trabalhadores do FGTS","Extrator de valor das notas fiscais de produtos","Soma NF SEPAT Serviços"],
    },
}


programas_funcoes = {
    'Balancete VS CTB': main1,
    'Precatório': main2,
    'REC VS QGR': main3,
    'Balancete da Câmara VS o Balancete do SICOF': main4,
    'Consórcio das Mulheres': main5,
    'Posição de Bancos VS CTB': main6,
    'Balancete Sicof VS balancete Sicon': main7,
    'DED Câmara VS DED SICOF': main8,
    'Restos a pagar Câmara VS SICOF': main9,
    'Despesa com Pessoal': main10,
    'Comparador crédito e débito': main11,
    'ICISMEP': main12,
    #'Comparador Ar': main13,
    'FUNDEB': main14,
    #'Formulário de credor / IR RFB': main15,
    'Demonstrativo da saúde': main16,
    'Somatório do CTB por orgãos': main17,
    'MDE': main18,
    'Corretor da Matriz': main20,
    'Comparador do EMP': main21,
    'Matriz VS balancete': main22,
    'LQD': main23,
    'Receita corrente líquida': main24,
    'ANL': main25,
    'DDR': main26,
    # 'Execucão orcamentária e financeira':main27,
    'Matriz VS CTB' : main28,
    'Corretor da MSC para o CTB' : main29,
    'Rec VS ementário da receita' : main30,
    'Fontes co': main31,
    'Somatório da matriz por Banco conta e fonte': main32,
    'Comparação dos saldos de encerramento': main33,
    'Totalizador do CTB por fonte': main34,
    'Depósitos judicias': main35,
    'Relacão de trabalhadores do FGTS': main36,
    'Extrator de valor das notas fiscais de produtos': main38,
    'Comparador de PCASPs': main39,
    'Posição de Bancos por Fonte VS MSC': main40,
    'Soma NF SEPAT Serviços': main41,
 
}


def get_all_programas():
    all_programas = []
    for categoria, subgrupos in categorias_programas.items():
        for subgrupo, programas in subgrupos.items():
            all_programas.extend(programas)
    return all_programas


st.sidebar.markdown("# SIC SEFAZ")



pesquisa = st.sidebar.text_input("Pesquisar programa")


categoria_selecionada = st.sidebar.selectbox('Escolha o Módulo', [''] + list(categorias_programas.keys())) if not pesquisa else ''
subgrupo_selecionado = ''
programa_selecionado = ''


if pesquisa:
    todos_programas = get_all_programas()
    programas_filtrados = [p for p in todos_programas if pesquisa.lower() in p.lower()]
    

    if programas_filtrados:
        programa_selecionado = st.sidebar.radio('Programas encontrados:', programas_filtrados)
    else:
        st.sidebar.write("Nenhum programa encontrado.")


if not pesquisa and categoria_selecionada:
    subgrupos = categorias_programas[categoria_selecionada]
    subgrupo_selecionado = st.sidebar.selectbox('Escolha o Subgrupo', [''] + list(subgrupos.keys()))

    if subgrupo_selecionado:
        programas = subgrupos[subgrupo_selecionado]
        programa_selecionado = st.sidebar.radio('Escolha o Aplicativo', programas)


if not programa_selecionado:
    st.markdown("## Bem-vindo(a) ao Sistema Interno de Conciliações da SEFAZ ! (^_^)/")
    st.markdown("Por favor, selecione um Módulo e um programa no menu ao lado para começar.")


if programa_selecionado and programa_selecionado in programas_funcoes:
    programas_funcoes[programa_selecionado]()
