# %% Setup
import os
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import dss

os.chdir('C:\\Users\\amy\\Desktop\\37Bus\\')   # ajustar o caminho
mydir = os.getcwd()

DSSText = dss.DSS.Text
DSSCircuit = dss.DSS.ActiveCircuit
DSSSolution = dss.DSS.ActiveCircuit.Solution

PV_BUSES = ['728', '733', '737', '740', '718', '720', '722', '742']
VMIN, VMAX = 0.93, 1.05


# %% Circuito e cargas
def compile_circuit():
    DSSText.Command = f'Compile "{mydir}/ieee37.dss"'


def preparar_cargas():
    ind_loads = ['s701a', 's701b', 's701c', 's728', 's737a', 's738a']
    resd_profile = [0.45, 0.40, 0.37, 0.35, 0.35, 0.40, 0.55, 0.65, 0.60, 0.50, 0.45, 0.45,
                    0.50, 0.48, 0.45, 0.45, 0.50, 0.65, 0.85, 0.95, 1.00, 0.95, 0.80, 0.60]
    ind_profile = [0.30, 0.28, 0.27, 0.27, 0.30, 0.35, 0.50, 0.70, 0.88, 0.95, 1.00, 1.00,
                   0.90, 0.95, 1.00, 0.98, 0.92, 0.80, 0.65, 0.50, 0.42, 0.38, 0.34, 0.32]

    DSSCircuit.LoadShapes.New('resd_loadshape')
    DSSCircuit.LoadShapes.Npts = 24
    DSSCircuit.LoadShapes.HrInterval = 1
    DSSCircuit.LoadShapes.Pmult = resd_profile

    DSSCircuit.LoadShapes.New('ind_loadshape')
    DSSCircuit.LoadShapes.Npts = 24
    DSSCircuit.LoadShapes.HrInterval = 1
    DSSCircuit.LoadShapes.Pmult = ind_profile

    for load in DSSCircuit.Loads.AllNames:
        DSSCircuit.SetActiveElement('load.%s' % load)
        if load.lower() in ind_loads:
            DSSCircuit.ActiveElement.Properties('daily').Val = 'ind_loadshape'
        else:
            DSSCircuit.ActiveElement.Properties('daily').Val = 'resd_loadshape'


def potencia_total_cargas():
    # soma das potencias nominais (o "pico pico")
    total = 0
    i = DSSCircuit.Loads.First
    while i:
        total += DSSCircuit.Loads.kW
        i = DSSCircuit.Loads.Next
    return total


def set_limites_tensao(pumin=VMIN, pumax=VMAX):
    DSSText.Command = f'set normvminpu={pumin}'
    DSSText.Command = f'set normvmaxpu={pumax}'


# %% PV
def pv_curvas():
    DSSText.Command = 'New XYcurve.PvsT npts=4 xarray=[0 25 75 100] yarray=[1.2 1 .8 .6]'
    DSSText.Command = 'New XYcurve.Effic npts=4 xarray=[.1 .2 .4 1] yarray=[0.86 .9 .93 .97]'
    DSSText.Command = 'New loadshape.Irrad npts=24 interval=1 mult=[0 0 0 0 0 0 .1 .2 .3 .5 .8 .9 1.0 1.0 .99 .9 .7 .4 .1 0 0 0 0 0]'
    DSSText.Command = 'New Tshape.Temp npts=24 interval=1 temp=[25 25 25 25 25 25 25 25 35 40 45 50 60 60 55 40 35 30 25 25 25 25 25 25]'


def criar_pvs(pmpp, kva):
    for i, bus in enumerate(PV_BUSES, start=1):
        DSSText.Command = (f'New PVSystem.PV_{i} phases=3 bus1={bus}.1.2.3 kv=4.8 conn=delta '
                           f'irrad=1.0 pmpp={pmpp} kva={kva} temperature=25 pf=1 '
                           f'%cutin=0.05 %cutout=0.05 effcurve=Effic P-tcurve=PvsT '
                           f'Daily=Irrad Tdaily=Temp')


def set_pv(ligado):
    estado = 'yes' if ligado else 'no'
    for i in range(1, len(PV_BUSES) + 1):
        DSSText.Command = f'Edit PVSystem.PV_{i} enabled={estado}'


def escalar_pv(fator, pmpp_base, kva_base):
    for i in range(1, len(PV_BUSES) + 1):
        DSSText.Command = f'Edit PVSystem.PV_{i} pmpp={pmpp_base * fator} kva={kva_base * fator}'


# %% Simulacao diaria (24 h)
def simular(loadmult=1.0, T=24):
    DSSText.Command = 'reset'
    DSSText.Command = 'set controlmode=static'
    DSSText.Command = 'set mode=daily'
    DSSText.Command = 'set stepsize=1h'
    DSSText.Command = 'set number=1'
    DSSText.Command = f'set loadmult={loadmult}'

    linhas = DSSCircuit.Lines.AllNames
    trafos = [n for n in DSSCircuit.Transformers.AllNames if 'reg' not in n.lower()]
    pvs = DSSCircuit.PVSystems.AllNames
    stos = DSSCircuit.Storages.AllNames

    def corrente_max(elem):
        n = elem.NumConductors
        return max(elem.CurrentsMagAng[0:2 * n:2])

    # capacidade (NormAmps) de cada elemento
    def capacidade(tipo, nomes):
        caps = []
        for n in nomes:
            DSSCircuit.SetActiveElement(f'{tipo}.{n}')
            caps.append(DSSCircuit.ActiveElement.NormalAmps)
        return np.array(caps)

    cap_linhas = capacidade('Line', linhas)
    cap_trafos = capacidade('Transformer', trafos)

    res = {
        'P': np.zeros(T), 'Q': np.zeros(T), 'perdas_kW': np.zeros(T),
        'vmax': np.zeros(T), 'vmin': np.zeros(T),
        'load_linhas': np.zeros((len(linhas), T)),
        'load_trafos': np.zeros((len(trafos), T)),
        'pv_kW': np.zeros((len(pvs), T)),
        'sto_kW': np.zeros((len(stos), T)),
        'linhas': linhas, 'trafos': trafos, 'pvs': pvs, 'stos': stos,
    }

    for h in range(T):
        DSSSolution.Solve()

        res['P'][h] = DSSCircuit.TotalPower[0]      # negativo = subestacao entregando
        res['Q'][h] = DSSCircuit.TotalPower[1]
        res['perdas_kW'][h] = DSSCircuit.Losses[0] / 1000

        v = np.concatenate([DSSCircuit.AllNodeVmagPUByPhase(f) for f in (1, 2, 3)])
        v = v[v > 0]
        res['vmax'][h] = v.max()
        res['vmin'][h] = v.min()

        for i, l in enumerate(linhas):
            DSSCircuit.SetActiveElement('Line.%s' % l)
            res['load_linhas'][i, h] = corrente_max(DSSCircuit.ActiveElement) / cap_linhas[i]

        for i, t in enumerate(trafos):
            DSSCircuit.SetActiveElement('Transformer.%s' % t)
            res['load_trafos'][i, h] = corrente_max(DSSCircuit.ActiveElement) / cap_trafos[i]

        for i, p in enumerate(pvs):
            DSSCircuit.SetActiveElement('PVSystem.%s' % p)
            res['pv_kW'][i, h] = DSSCircuit.ActiveElement.TotalPowers[0]

        for i, s in enumerate(stos):
            DSSCircuit.SetActiveElement('Storage.%s' % s)
            res['sto_kW'][i, h] = DSSCircuit.ActiveElement.TotalPowers[0]

    return res


# %% Metricas
def metricas(res):
    """Resumo de um cenario: sobretensao, sobrecarga, fluxo reverso e perdas."""
    reverso = res['P'] > 0   # potencia positiva na subestacao = fluxo reverso
    return {
        'vmax (pu)': res['vmax'].max(),
        'vmin (pu)': res['vmin'].min(),
        'horas sobretensao': int((res['vmax'] > VMAX).sum()),
        'horas subtensao': int((res['vmin'] < VMIN).sum()),
        'loading max linhas (pu)': res['load_linhas'].max(),
        'linhas sobrecarregadas': int((res['load_linhas'].max(axis=1) > 1).sum()),
        'loading max trafos (pu)': res['load_trafos'].max(),
        'trafos sobrecarregados': int((res['load_trafos'].max(axis=1) > 1).sum()),
        'horas fluxo reverso': int(reverso.sum()),
        'energia reversa (kWh)': res['P'][reverso].sum(),
        'perdas (kWh)': res['perdas_kW'].sum(),
        'perdas (%)': abs(res['perdas_kW'].sum() / res['P'].sum() * 100),
    }


def tem_violacao(m):
    return (m['horas sobretensao'] > 0 or m['horas subtensao'] > 0
            or m['linhas sobrecarregadas'] > 0 or m['trafos sobrecarregados'] > 0
            or m['horas fluxo reverso'] > 0)


# %% Graficos
def plot_envoltoria(res, titulo=''):
    h = np.arange(len(res['vmax']))
    fig, ax = plt.subplots(figsize=(7, 4))
    ax.fill_between(h, res['vmin'], res['vmax'], alpha=0.25)
    ax.plot(h, res['vmax'], label='vmax')
    ax.plot(h, res['vmin'], label='vmin')
    ax.axhline(VMAX, color='r', linestyle='--', linewidth=0.8)
    ax.axhline(VMIN, color='r', linestyle='--', linewidth=0.8)
    ax.set_title('Tensao maxima e minima ' + titulo, fontsize=9)
    ax.set_xlabel('hora')
    ax.set_ylabel('p.u.')
    ax.legend()
    plt.show()


def plot_subestacao(res, titulo=''):
    fig, axs = plt.subplots(1, 3, figsize=(15, 4))
    axs[0].plot(-res['P'])
    axs[0].set_title('Potencia ativa na subestacao ' + titulo)
    axs[0].set_ylabel('kW')
    axs[1].plot(-res['Q'])
    axs[1].set_title('Potencia reativa na subestacao')
    axs[1].set_ylabel('kvar')
    axs[2].plot(res['perdas_kW'])
    axs[2].set_title('Perdas ativas')
    axs[2].set_ylabel('kW')
    for ax in axs:
        ax.set_xlabel('hora')
    plt.show()


def plot_loading(res, chave, titulo=''):
    """chave: 'load_linhas' ou 'load_trafos'"""
    nomes = res['linhas'] if chave == 'load_linhas' else res['trafos']
    df = pd.DataFrame(res[chave].T, columns=nomes)
    df.plot(figsize=(6, 3), legend=False)
    plt.axhline(1, color='r', linestyle='--', linewidth=0.8)
    plt.title('Carregamento ' + titulo, fontsize=9)
    plt.xlabel('hora')
    plt.ylabel('pu')
    plt.show()


def plot_geracao(res, chave, titulo):
    """chave: 'pv_kW' ou 'sto_kW'"""
    nomes = res['pvs'] if chave == 'pv_kW' else res['stos']
    for i, n in enumerate(nomes):
        plt.plot(res[chave][i], label=n)
    plt.title(titulo)
    plt.xlabel('hora')
    plt.ylabel('kW')
    plt.legend()
    plt.grid()
    plt.show()


# %% Parte I: preparar tudo
compile_circuit()
preparar_cargas()
set_limites_tensao()
pv_curvas()

P_TOTAL = potencia_total_cargas()
PMPP_BASE = P_TOTAL / len(PV_BUSES)
KVA_BASE = PMPP_BASE
print(f'Carga total nominal: {P_TOTAL:.0f} kW, cada PV: {PMPP_BASE:.0f} kW')

criar_pvs(PMPP_BASE, KVA_BASE)


# %% Parte I: os 4 cenarios
CENARIOS = {
    '1. sem PV, carga 100%': (False, 1.0),
    '2. sem PV, carga 20%': (False, 0.2),
    '3. com PV, carga 20%': (True, 0.2),
    '4. com PV, carga 100%': (True, 1.0),
}


def rodar_cenarios():
    resultados = {}
    for nome, (pv, lm) in CENARIOS.items():
        set_pv(pv)
        resultados[nome] = simular(loadmult=lm)
    return resultados


resultados = rodar_cenarios()
tabela = pd.DataFrame({n: metricas(r) for n, r in resultados.items()})
print(tabela)


# %% Parte I: aumento gradual do PV no cenario 4
def varrer_pv(fatores=(1.0, 1.25, 1.5, 2.0, 2.5, 3.0)):
    set_pv(True)
    linhas_tab = {}
    primeira = {}   # fator em que cada violacao aparece pela primeira vez
    for f in fatores:
        escalar_pv(f, PMPP_BASE, KVA_BASE)
        m = metricas(simular(loadmult=1.0))
        linhas_tab[f'{f}x'] = m
        for chave in ['horas sobretensao', 'linhas sobrecarregadas',
                      'trafos sobrecarregados', 'horas fluxo reverso']:
            if m[chave] > 0 and chave not in primeira:
                primeira[chave] = f
    escalar_pv(1.0, PMPP_BASE, KVA_BASE)   # volta ao valor base
    return pd.DataFrame(linhas_tab), primeira


tab_sweep, primeira_violacao = varrer_pv()
print(tab_sweep)
print('Primeira violacao em cada metrica:', primeira_violacao)


# %% Parte II: storage
def storage_curvas():
    DSSText.Command = 'New XYcurve.Eff npts=4 xarray=[.1 .2 .4 1] yarray=[0.86 .9 .93 .97]'
    DSSText.Command = ('New LoadShape.dispatch_shape npts=24 interval=1 '
                       'mult=[0 0 0 0 0 0 0 0 0 0 -0.3 -0.4 -0.45 -0.45 -0.45 -0.4 -0.15 0.2 0.4 0.6 0.6 0.4 0.2 0]')


def add_storage(nome, bus, kw, kwh, kv=4.8, phases=3, conn='delta', stored=20, reserve=20):
    DSSText.Command = (f'New Storage.{nome} phases={phases} bus1={bus} kv={kv} conn={conn} '
                       f'kWrated={kw} kWhrated={kwh} %stored={stored} %reserve={reserve} '
                       f'effcurve=Eff dispmode=follow daily=dispatch_shape pf=1')


def set_storage(nomes_ligados):
    for n in DSSCircuit.Storages.AllNames:
        estado = 'yes' if n in [x.lower() for x in nomes_ligados] else 'no'
        DSSText.Command = f'Edit Storage.{n} enabled={estado}'


storage_curvas()

# central: um so, ajustar barra, kW e kWh
add_storage('StoCentral', '709.1.2.3', 2464, 10000)
# distribuido: dois, perto dos PVs (ajustar barras)
add_storage('Sto1', '728.1.2.3', 1232, 5000)
add_storage('Sto2', '737.1.2.3', 1232, 5000)


# %% Parte II: comparar central x distribuido (cenario 4 com PV)
def comparar_storage():
    set_pv(True)
    out = {}
    set_storage([])
    out['sem storage'] = simular(loadmult=1.0)
    set_storage(['StoCentral'])
    out['central'] = simular(loadmult=1.0)
    set_storage(['Sto1', 'Sto2'])
    out['distribuido'] = simular(loadmult=1.0)
    return out


res_sto = comparar_storage()
print(pd.DataFrame({n: metricas(r) for n, r in res_sto.items()}))


# %% Parte III: ilhamento e corte de carga
# carga (kW) em ordem de corte, menor prioridade primeiro (confirmar)
CARGAS_ILHA = [('S736b', 42), ('S741c', 42), ('S732c', 42), ('S734c', 42), ('S735c', 85),
               ('S733a', 85), ('S740c', 85), ('S738a', 126), ('S737a', 140)]


def ilhar(linha):
    DSSText.Command = f'Open Line.{linha} Term=1'


def cortar_cargas(n_corte):
    for nome, kw in CARGAS_ILHA[:n_corte]:
        DSSText.Command = f'Edit Load.{nome} enabled=no'


def rodar_ilha(linha='L27', n_corte=0):
    # recompila pra comecar de um estado limpo (linha fechada, cargas ligadas)
    compile_circuit()
    preparar_cargas()
    set_limites_tensao()
    pv_curvas()
    criar_pvs(PMPP_BASE, KVA_BASE)
    storage_curvas()
    add_storage('StoCentral', '709.1.2.3', 2464, 10000)
    ilhar(linha)
    cortar_cargas(n_corte)
    return simular(loadmult=1.0)

# FALTA: tempo de sobrevivencia (ver ate que hora a bateria/tensao aguenta)
# e a logica de quem forma a ilha. Isso depende de como voce vai modelar.
