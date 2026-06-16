from simwave import read_2D_segy
import numpy as np
import os

print("Lendo o SEGY do Marmousi-2 (Resolucao 1.25m)...")
marmousi_model = read_2D_segy('MODEL_P-WAVE_VELOCITY_1.25m.segy')

# Dizimacao: Pegamos 1 ponto a cada 8 para converter a malha de 1.25m para 10m
# 13601 // 8 = 1700 | 2801 // 8 = 350
marmousi_vp_10m = marmousi_model[::8, ::8].astype('<f4')

# GERMAINE espera Vp, Vs, Densidade e tensores de atenuacao (mesmo no modo acustico)
# Vamos preencher o resto com zeros ou constantes para estabilidade
marmousi_rho = np.full_like(marmousi_vp_10m, 2000.0) # Densidade constante (2000 kg/m3)
marmousi_zeros = np.zeros_like(marmousi_vp_10m)      # Zeros para Vs e Atenuacao

output_dir = "par/start"
os.makedirs(output_dir, exist_ok=True)

print("Exportando os 5 tensores para o GERMAINE...")
# 1. Velocidade P (.vp)
with open(os.path.join(output_dir, "marmousi_segy_true.vp"), 'wb') as f:
    f.write(marmousi_vp_10m.flatten('C').tobytes())
# 2. Velocidade S (.vs - zerada)
with open(os.path.join(output_dir, "marmousi_segy_true.vs"), 'wb') as f:
    f.write(marmousi_zeros.flatten('C').tobytes())
# 3. Densidade (.rho - constante 2000)
with open(os.path.join(output_dir, "marmousi_segy_true.rho"), 'wb') as f:
    f.write(marmousi_rho.flatten('C').tobytes())
# 4. Atenuacao P (.tp - zerada)
with open(os.path.join(output_dir, "marmousi_segy_true.tp"), 'wb') as f:
    f.write(marmousi_zeros.flatten('C').tobytes())
# 5. Atenuacao S (.ts - zerada)
with open(os.path.join(output_dir, "marmousi_segy_true.ts"), 'wb') as f:
    f.write(marmousi_zeros.flatten('C').tobytes())

print("Sucesso! Malha 1700x350 (DH=10m) pronta na pasta par/start/")
