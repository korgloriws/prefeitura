import streamlit as st

from balancete_vs_ctb.comparador_2 import main as main1
from leitor_de_pdf.leitorDePdf import main as main2
from rec_vs_qgr.index import main as main3
from camara_vs_sicof.server import main as main4
from organizador_E_filtro.index import main as main5


st.sidebar.markdown("# **Aplicativos da Contabilidade**")
programa_selecionado = st.sidebar.radio(
    'Escolha entre as opções',
    ('Balancete vs CTB', 'precatório', 'REC vs QGR', 'camara_vs_sicof', 'organizador_E_filtro')
)

if programa_selecionado == 'Balancete vs CTB':
    main1()
elif programa_selecionado == 'precatório':
    main2()
elif programa_selecionado == 'REC vs QGR':
    main3()
elif programa_selecionado == 'camara_vs_sicof':
    main4()
elif programa_selecionado == 'organizador_E_filtro':
    main5()