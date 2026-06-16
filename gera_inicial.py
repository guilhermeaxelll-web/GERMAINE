import numpy as np
from scipy.ndimage import gaussian_filter
import os

print("=== GERANDO CHUTE INICIAL SUAVIZADO PARA O FWI ===")

# Caminho do modelo verdadeiro que já existe e caminho de saída do novo modelo
caminho_true = 'par/start/marmousi_segy_true.vp'
caminho_initial = 'par/start/marmousi_initial.vp'

# Verifica se a pasta start existe
if not os.path.exists('par/start/'):
    os.makedirs('par/start/')

# Carrega a malha real (1700x350)
if os.path.exists(caminho_true):
    vp_true = np.fromfile(caminho_true, dtype='<f4').reshape(1701, 351)
    
    # Aplica o filtro Gaussiano para criar o modelo borrado
    vp_initial = gaussian_filter(vp_true, sigma=1.0)
    
    # Salva o arquivo no formato binário C (flatten e float32)
    vp_initial.flatten('C').astype('<f4').tofile(caminho_initial)
    
    print(f" Sucesso! O modelo inicial borrado foi salvo em: {caminho_initial}")
else:
    print(f" Erro: Não encontrei o modelo verdadeiro em {caminho_true}.")