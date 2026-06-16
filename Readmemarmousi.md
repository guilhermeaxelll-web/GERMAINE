# FAST-FWI: Pipeline GERMAINE + Marmousi-2 Elástico

**Autor:** Guilherme Souza  
**Projeto:** FAST-FWI (Aceleração de Inversão Sísmica de Nova Geração)

## Visão Geral
Este repositório contém a automação e documentação do pipeline de modelagem e inversão sísmica (FWI) utilizando Diferenças Finitas através do pacote GERMAINE. O fluxo substitui os exemplos básicos do simulador, implementando a extração, adequação e inversão do modelo realista **Marmousi-2**.

Os resultados tradicionais (modelos invertidos com artefatos e suavizações) gerados por este pipeline atuarão como *baseline* e "chute inicial" (*a priori*) para o treinamento e validação da nossa arquitetura de Deep Learning.

---

## 1. Dependências e Instalação do Ambiente

O GERMAINE requer compiladores C/Fortran, MPI e bibliotecas avançadas de álgebra linear.

**Módulos do Supercomputador (SLURM):**
```bash
module load softwares/python/3.10.5-gnu8
module load libraries/openmpi/4.1.8-gnu8
module load libraries/blas/3.10.0-gnu8
module load libraries/lapack/3.10.0-gnu8
git clone [https://github.com/daniel-koehn/GERMAINE.git](https://github.com/daniel-koehn/GERMAINE.git)
cd GERMAINE/src
1.2 Troubleshooting de Compilação (SuiteSparse)
Caso o cluster não possua o SuiteSparse global instalado corretamente para a fatoração LU, instale-o localmente:

Baixe o SuiteSparse v4.5.6 e instale em ~/libs/SuiteSparse.

Edite o Makefile original do GERMAINE substituindo o usuário antigo (daniel-koehn) pelo usuário atual (gardosouza):
sed -i 's/daniel-koehn/gardosouza/g' Makefile
Compile com make germaine
### 2.1 Download do Marmousi-2 Oficial
Antes de preparar a malha, baixe o pacote elástico oficial do Marmousi hospedado no Open Source Geoscience e extraia o arquivo SEGY:

```bash
# Baixa o pacote compactado do Marmousi-2
wget [https://s3.amazonaws.com/open.source.geoscience/open_data/elastic-marmousi/elastic-marmousi-model.tar.gz](https://s3.amazonaws.com/open.source.geoscience/open_data/elastic-marmousi/elastic-marmousi-model.tar.gz)

# Extrai o conteúdo
tar -zxvf elastic-marmousi-model.tar.gz

# Entra na pasta e extrai o arquivo SEGY específico da velocidade P
cd elastic-marmousi-model/model/
tar -zxvf MODEL_P-WAVE_VELOCITY_1.25m.segy.tar.gz
mv MODEL_P-WAVE_VELOCITY_1.25m.segy ../../
cd ../../
2. Preparação do Modelo Marmousi-2O modelo original SEGY possui resolução muito alta (1.25m), o que geraria uma matriz de 13601 x 2801, exigindo Terabytes de RAM para o UMFPACK e derrubando o nó de processamento.Solução (Dizimação):Utilizamos o pacote simwave em um script Python para ler o SEGY e dizimar a malha tomando 1 ponto a cada 8.Novo Grid: NX = 1700, NY = 350, DH = 10.0mO GERMAINE exige a separação dos tensores físicos em arquivos binários sem cabeçalho (Little Endian, Float32). O script de preparação gera os 5 arquivos obrigatórios na pasta par/start/:.vp (Velocidade Compressional).vs (Velocidade de Cisalhamento - Zerada).rho (Densidade - Constante 2000 kg/m³).tp e .ts (Atenuação - Zerada)3. Fase 1: Modelagem Direta (Forward)A modelagem direta simula a aquisição sísmica, gerando o nosso "gabarito" (Sismogramas Observados - $d_{obs}$).Configuração do arquivo .inp:Ligar apenas a propagação: INVMAT = 0Apontar malha real: MFILE = start/marmousi_segy_trueAjustar o Grid: NX = 1700, NY = 350, DH = 10.0Os sismogramas binários gerados serão salvos no diretório seis/ e servirão de dado observado para a próxima etapa.4. Fase 2: Inversão (FWI)O FWI tenta recuperar o modelo verdadeiro iterativamente a partir de um modelo inicial desconhecido.4.1 Criando o Chute InicialAplicamos um filtro Gaussiano (sigma=15) sobre a malha de velocidade verdadeira para gerar um modelo "borrado" (marmousi_initial.vp).Regra Crítica (Densidade): O GERMAINE exige o par exato de arquivos para rodar. Como não invertemos a densidade no caso acústico básico, é obrigatório duplicar o arquivo de densidade verdadeira:
cp start/marmousi_segy_true.rho start/marmousi_initial.rho

4.2 Configuração do arquivo _fwi.inp
Ligar inversão: INVMAT = 1

Chute inicial: MFILE = start/marmousi_initial

Dados observados: DATA_DIR = obs/incl2

Pasta de saída: INV_MODELFILE = model/modelTest

Iterações de teste: ITERMAX = 5

4.3 Troubleshooting de Execução (Erro libumfpack.so.5)
O MPI costuma perder a referência de bibliotecas dinâmicas pesadas entre os nós computacionais.
Solução (Bypass):

Instalar o Miniconda localmente (~/miniconda_local).

Baixar o pacote via conda: conda install -c conda-forge suitesparse=5 -y.

No script de submissão do SLURM (.srm), forçar a exportação do caminho para os nós MPI:

Bash
export LD_LIBRARY_PATH=~/miniconda_local/lib:$LD_LIBRARY_PATH
mpirun -x LD_LIBRARY_PATH -np 16 ../bin/germaine GERMAINE_marmousi_fwi.inp ...

5. Visualização e Extração de Resultados
Ao final dos estágios de frequência, o FWI despeja arquivos binários do modelo atualizado (ex: modelTest_vp_stage_8.bin) na pasta model/.

Utilizamos um script Python (numpy + matplotlib) para:

Ler o array binário Float32.

Fazer o reshape (dobrar) utilizando as dimensões originais (NY, NX).

Plotar o mapa de calor com escala física de profundidade e distância e salvar o PNG em alta resolução para documentação.
