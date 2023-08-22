import pandas as pd
import matplotlib.pyplot as plt

# Carregar os dados do arquivo CSV
df = pd.read_csv('Saldos_Diferentes.csv')

# Criar uma tabela a partir do DataFrame
table = plt.table(cellText=df.values,
                  colLabels=df.columns,
                  cellLoc='center',
                  loc='center')

# Configurar o estilo da tabela
table.auto_set_font_size(False)
table.set_fontsize(7)
table.scale(1.2, 1.2)

# Remover os eixos do gráfico
plt.axis('off')

# Exibir a tabela
plt.show()
