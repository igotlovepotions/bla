#!/usr/bin/env python
# coding: utf-8

# Setup
# 

# In[ ]:


get_ipython().system('pip install numpy')
get_ipython().system('pip install pypiwin32')
get_ipython().system('pip install pandas')
get_ipython().system('pip install matplotlib')
get_ipython().system('pip install dss-python')


# In[ ]:


import numpy as np    #np, mpl and pd serve as a nicknames
import matplotlib as mpl
import matplotlib.pyplot as plt
import pandas as pd
import os
import dss #OpenDss Module

os.chdir('C:\\Users\\amy\\Desktop\\37Bus\\')   # force going to the working folder (ADJUST FOR YOUR OWN PATH!)
mydir=os.getcwd()                          # mydir stores the working path

dss_engine = dss.DSS
DSSText = dss_engine.Text                                                      
DSSCircuit = dss_engine.ActiveCircuit                                            
DSSSolution = dss_engine.ActiveCircuit.Solution                                      
ControlQueue = dss_engine.ActiveCircuit.CtrlQueue  


# Parte I 
# • a instalação de sistemas PV deve ser distribuída por pelo menos 20% das barras do sistema. 
# • inicialmente, o total de geração PV deve ser dimensionado para atender à demanda total, 
# considerando as cargas com o valor de pico. 
# • fazer as simulações para os seguintes cenários: - 1. sistema sem geração PV e cargas com valor de pico; - 2. sistema sem geração PV e cargas com 20% do valor de pico;  - 3. sistema com geração PV e cargas com 20% do valor de pico; - 4. sistema com geração PV e cargas com valor de pico. 
# • Em cada cenário, as métricas sobretensão e sobrecarga nas linhas e transformadores devem 
# ser avaliadas; bem como o nível de fluxo reverso e perdas no sistema. 
# • Para o cenário 4, caso não haja violação de limites operativos de tensão e carregamento nos 
# elementos, aumente gradativamente a geração PV e verifique em quais níveis de geração PV 
# as violações ocorrem. 
# • Compare e discuta os resultados obtidos. 
# Parte II 
# • Agregar ao circuito com elevada capacidade de geração instalada, um sistema de 
# armazenamento de energia (armazenamento central e armazenamento distribuído), de forma 
# que a energia excedente seja armazenada e os impactos da geração renovável sejam 
# mitigados. Compare os resultados obtidos com as duas abordagens. 
# Parte III 
# • Crie uma Microrrede em parte do circuito e mostre a operação ilhada da rede, avaliando seu 
# tempo de sobrevivência. Simule o ilhamento em diferentes cenários.  
# • Aplique uma metodologia de corte de carga para aumento de tempo de sobrevivência.

# ## Simulação 1: PV false, loadmult=1
# 
# Referência do alimentador, sem nada de PV e com a carga cheia. Tudo que vier depois se compara com essa.
# 
# Ordem: reset, cargas, solve, potência e perdas, potência das cargas, tensão, trafos, linhas, subestação.

# In[ ]:


import pprint
data = {'name': 'John', 'age': 30, 'children': [{'name': 'Jane', 'age': 10}, {'name': 'Doe', 'age': 8}]}
pprint.pprint(data)


# In[ ]:


def compile():
    DSSText.Command = 'Compile ' + mydir + '/ieee37.dss'

    Elenames = DSSCircuit.AllElementNames
    Loadnames = DSSCircuit.Loads.AllNames
    Busnames = DSSCircuit.AllBusNames
    Trafonames = DSSCircuit.Transformers.AllNames
    Linenames = DSSCircuit.Lines.AllNames

def  get_elements():
    compile()
# Get all element names and store in variant array of strings
Elenames = DSSCircuit.AllElementNames
print('List of elements')
print ('Total:' +  str(len(Elenames)))
print(Elenames)

# Get all load names and store in variant array of strings
Loadnames = DSSCircuit.Loads.AllNames
print('List of Loads')
print ('Total:' +  str(len(Loadnames)))
print(Loadnames)

# Get all bus names and store in variant array of strings
Busnames = DSSCircuit.AllBusNames
print('List of Buses')
print ('Total:' +  str(len(Busnames)))
print(Busnames)

# Get all transformers names and store in variant array of strings
Trafonames = DSSCircuit.Transformers.AllNames
print('List of Transformers')
print ('Total:' +  str(len(Trafonames)))
print(Trafonames)

# Get all line names and store in variant array of strings
Linenames = DSSCircuit.Lines.AllNames
print('List of Lines')
print ('Total:' +  str(len(Linenames)))
print(Linenames)


# In[ ]:


def compile():
    DSSText.Command = f'Compile "{mydir}/ieee37.dss"'

def get_all_elements():
    Elenames = DSSCircuit.AllElementNames
    Loadnames = DSSCircuit.Loads.AllNames
    Busnames = DSSCircuit.AllBusNames
    Trafonames = DSSCircuit.Transformers.AllNames
    Linenames = DSSCircuit.Lines.AllNames
    Pvnames = DSSCircuit.PVSystems.AllNames
    Storagenames = DSSCircuit.Storages.AllNames

    return Elenames, Loadnames, Busnames, Trafonames, Linenames, Pvnames, Storagenames


# In[ ]:


compile()


# In[ ]:


get_elements()


# In[ ]:


def preparar_cargas():
    ind_loads = ['s701a', 's701b', 's701c', 's728', 's737a', 's738a']

    resd_profile = [0.45, 0.40, 0.37, 0.35, 0.35, 0.40, 0.55, 0.65, 0.60, 0.50, 0.45, 0.45, 0.50, 0.48, 0.45, 0.45, 0.50, 0.65, 0.85, 0.95, 1.00, 0.95, 0.80, 0.60]

    ind_profile = [0.30, 0.28, 0.27, 0.27, 0.30, 0.35, 0.50, 0.70, 0.88, 0.95, 1.00, 1.00, 0.90, 0.95, 1.00, 0.98, 0.92, 0.80, 0.65, 0.50, 0.42, 0.38, 0.34, 0.32]

    # Criar os loadshapes
    DSSCircuit.LoadShapes.New('resd_loadshape')
    DSSCircuit.LoadShapes.Npts = 24
    DSSCircuit.LoadShapes.HrInterval = 1
    DSSCircuit.LoadShapes.Pmult = resd_profile

    DSSCircuit.LoadShapes.New('ind_loadshape')
    DSSCircuit.LoadShapes.Npts = 24
    DSSCircuit.LoadShapes.HrInterval = 1
    DSSCircuit.LoadShapes.Pmult = ind_profile
    print('Loadshapes created')
    # Atribuir aos loads
    for load in Loadnames:
        DSSCircuit.SetActiveElement('load.%s' % load)
        if load.lower() in ind_loads:
            DSSCircuit.ActiveElement.Properties('daily').Val = 'ind_loadshape'
        else:
            DSSCircuit.ActiveElement.Properties('daily').Val = 'resd_loadshape' 


# In[ ]:


preparar_cargas()


# In[ ]:


def loadmult(load_factor):
    DSSText.Command = f'set loadmult = {load_factor}'
    print(f'Load multiplier set to {load_factor}')


# In[ ]:


def configure_power_flow(simulation_time, Loadnames, Linenames, DSSCircuit, DSSSolution, DSSText):
    DSSText.Command = 'reset'
    DSSText.Command = 'set controlmode=static'
    DSSText.Command = 'set mode=daily'
    DSSText.Command = 'set stepsize=1h'
    DSSText.Command = 'set number=1'

    Pvnames = DSSCircuit.PVSystems.AllNames
    Storagenames = DSSCircuit.Storages.AllNames
    onlytrafo = [n for n in DSSCircuit.Transformers.AllNames if 'reg' not in n.lower()]

    T = simulation_time
    Total_Act_Power = np.zeros(T)
    Total_React_Power = np.zeros(T)
    Total_Act_Losses = np.zeros(T)
    Total_React_Losses = np.zeros(T)
    busVpuA = [None] * T
    busVpuB = [None] * T
    busVpuC = [None] * T

    Trafo_Max_Amp = np.zeros((len(onlytrafo), T))
    Load_kW = np.zeros((len(Loadnames), T))
    Load_kvar = np.zeros((len(Loadnames), T))
    Line_Max_Amp = np.zeros((len(Linenames), T))
    PV_kW = np.zeros((len(Pvnames), T))
    Storage_kW = np.zeros((len(Storagenames), T))

    def max_current(elem):
        ncond = elem.NumConductors
        return max(elem.CurrentsMagAng[0:2*ncond:2])

    for h in range(T):
        DSSSolution.Solve()

        Total_Act_Power[h], Total_React_Power[h] = DSSCircuit.TotalPower[0], DSSCircuit.TotalPower[1]
        Total_Act_Losses[h] = DSSCircuit.Losses[0] / 1000
        Total_React_Losses[h] = DSSCircuit.Losses[1] / 1000

        busVpuA[h] = DSSCircuit.AllNodeVmagPUByPhase(1)
        busVpuB[h] = DSSCircuit.AllNodeVmagPUByPhase(2)
        busVpuC[h] = DSSCircuit.AllNodeVmagPUByPhase(3)

        for i, t in enumerate(onlytrafo):
            DSSCircuit.SetActiveElement('Transformer.%s' % t)
            Trafo_Max_Amp[i, h] = max_current(DSSCircuit.ActiveElement)

        for i, l in enumerate(Loadnames):
            DSSCircuit.SetActiveElement('Load.%s' % l)
            Load_kW[i, h] = DSSCircuit.ActiveElement.TotalPowers[0]
            Load_kvar[i, h] = DSSCircuit.ActiveElement.TotalPowers[1]

        for i, l in enumerate(Linenames):
            DSSCircuit.SetActiveElement('Line.%s' % l)
            Line_Max_Amp[i, h] = max_current(DSSCircuit.ActiveElement)

        for i, p in enumerate(Pvnames):
            DSSCircuit.SetActiveElement('PVSystem.%s' % p)
            PV_kW[i, h] = DSSCircuit.ActiveElement.TotalPowers[0]

        for i, s in enumerate(Storagenames):
            DSSCircuit.SetActiveElement('Storage.%s' % s)
            Storage_kW[i, h] = DSSCircuit.ActiveElement.TotalPowers[0]

    return (Total_Act_Power, Total_React_Power, Total_Act_Losses, Total_React_Losses,
            busVpuA, busVpuB, busVpuC, Trafo_Max_Amp, Load_kW, Load_kvar,
            Line_Max_Amp, PV_kW, Storage_kW)


# In[ ]:


configure_power_flow(simulation_time=24, Loadnames=Loadnames, Linenames=Linenames, DSSCircuit=DSSCircuit, DSSSolution=DSSSolution, DSSText=DSSText)


# In[ ]:


print(onlytrafo)
DSSCircuit.Transformers.Name = onlytrafo[0]
print(len(DSSCircuit.Transformers.WdgCurrents), DSSCircuit.Transformers.WdgCurrents[:6])


# In[ ]:


configure_power_flow(24, Loadnames, Linenames, DSSCircuit, DSSSolution, DSSText)


# In[ ]:


DSSSolution.Converged


# In[ ]:


print(DSSCircuit.TotalPower)
print(sum(DSSCircuit.TotalPower))


# In[ ]:


def Results_Energy():
    #DSSCircuit.Transformers.Name = 'xfm1'
    #DSSCircuit.Transformers.WdgCurrents
    # 
    # # Circuit kWh and Losses kWh
    kWh_SC1 = np.sum(Total_Act_Power)
    kVArh_SC1 = np.sum(Total_React_Power)
    kWh_Loss_SC1 = np.sum(Total_Act_Losses) 
    kVArh_Loss_SC1 = np.sum(Total_React_Losses)

    print("Total kWh delivered to the network: %.3f kWh" %kWh_SC1)
    print("Total kVAr delivered to the network: %.3f kvarh" %kVArh_SC1)
    print("Total active losses: %.3f kWh" %kWh_Loss_SC1)
    print("Percent losses: %.3f" %abs(((kWh_Loss_SC1/kWh_SC1)*100)) + "%")
    print("Total reactive losses %.3f kVArh" %kVArh_Loss_SC1)


# In[ ]:


Results_Energy()


# In[ ]:


def Results_Voltage():
    #get node names
    nodesA=(DSSCircuit.AllNodeNamesByPhase(1))#nodes in phase 1
    nodesB=(DSSCircuit.AllNodeNamesByPhase(2))#nodes in phase 2
    nodesC=(DSSCircuit.AllNodeNamesByPhase(3))#nodes in phase 3

    #Each dataframes will have 24 rows and a column for voltages of each node
    dfbusVpuA_SC1 = pd.DataFrame(np.vstack(busVpuA_SC1),columns=nodesA)
    dfbusVpuB_SC1 = pd.DataFrame(np.vstack(busVpuB_SC1),columns=nodesB)
    dfbusVpuC_SC1 = pd.DataFrame(np.vstack(busVpuC_SC1),columns=nodesC)

    # Drop dataframe columns related to the voltage regulators
    columns_to_drop = [col for col in dfbusVpuA_SC1.columns if col.startswith('reg')]
    dfbusVpuA_SC1 = dfbusVpuA_SC1.drop(columns=columns_to_drop)

    columns_to_drop = [col for col in dfbusVpuB_SC1.columns if col.startswith('reg')]
    dfbusVpuB_SC1 = dfbusVpuB_SC1.drop(columns=columns_to_drop)

    columns_to_drop = [col for col in dfbusVpuC_SC1.columns if col.startswith('reg')]
    dfbusVpuC_SC1 = dfbusVpuC_SC1.drop(columns=columns_to_drop)

    #plots

    ax = dfbusVpuA_SC1.plot(figsize=(6,3))
    plt.title('Voltage at all nodes - phase 1',fontsize=9)
    plt.legend(fontsize=6,loc="upper left") 
    plt.yticks(fontsize=8)
    plt.xlabel("hour",fontsize=8)
    plt.ylabel("p.u.",fontsize=8)
    plt.xticks([0,3,6,9,12,15,18,21,24],fontsize=8)

    ax = dfbusVpuB_SC1.plot(figsize=(6,3))
    plt.title('Voltage at all nodes - phase 2',fontsize=9)
    plt.legend(fontsize=6,loc="upper left") 
    plt.yticks(fontsize=8)
    plt.xlabel("hour",fontsize=8)
    plt.ylabel("p.u.",fontsize=8)
    plt.xticks([0,3,6,9,12,15,18,21,24],fontsize=8)

    ax = dfbusVpuC_SC1.plot(figsize=(6,3))
    plt.title('Voltage at all nodes - phase 3',fontsize=9)
    plt.legend(fontsize=6,loc="upper left") 
    plt.yticks(fontsize=8)
    plt.xlabel("hour",fontsize=8)
    plt.ylabel("p.u.",fontsize=8)
    plt.xticks([0,3,6,9,12,15,18,21,24],fontsize=8)

    plt.show()


# In[ ]:


Results_Voltage()


# In[ ]:


def plot_envoltoria():
    fases = {
        'Fase A': dfbusVpuA_SC1,
        'Fase B': dfbusVpuB_SC1,
        'Fase C': dfbusVpuC_SC1,
    }
    cores = ['tab:blue', 'tab:orange', 'tab:green']

    fig, ax = plt.subplots(figsize=(7, 4))
    for (nome, df), cor in zip(fases.items(), cores):
        df = df.replace(0, np.nan)
        vmax = df.max(axis=1)
        vmin = df.min(axis=1)
        ax.fill_between(df.index, vmin, vmax, color=cor, alpha=0.25, label=nome)
        ax.plot(df.index, vmax, color=cor, linewidth=0.8)
        ax.plot(df.index, vmin, color=cor, linewidth=0.8)

    ax.axhline(1.05, color='r', linestyle='--', linewidth=0.8)
    ax.axhline(0.93, color='r', linestyle='--', linewidth=0.8)
    ax.set_title('Tensão máxima e mínima por fase', fontsize=9)
    ax.set_xlabel('hora', fontsize=8)
    ax.set_ylabel('p.u.', fontsize=8)
    ax.set_xticks([0, 3, 6, 9, 12, 15, 18, 21, 24])
    ax.tick_params(labelsize=8)
    ax.legend(fontsize=7, loc='upper left')
    plt.show()


# In[ ]:


plot_envoltoria()


# In[ ]:


def results_transformer_amps_loading():
    #Max_Transf_Amps = np.max(Transf_Amps_loading, axis=2)
    #display(Max_Transf_Amps)
    #display(Transf_Amps_loading)
    #DSSCircuit.SetActiveElement('line.632645')
    #display(DSSCircuit.ActiveElement.Name)
    #display(DSSCircuit.ActiveElement.CurrentsMagAng)
    #display(DSSCircuit.ActiveElement.CurrentsMagAng[0:12:2])
    #display(max(DSSCircuit.ActiveElement.CurrentsMagAng[0:12:2])

    Transf_Wdg1_Amps = np.zeros((len(onlytrafo),24,3))#to store all phases current magnitude at HV side winding )   
    Transf_Amps_loading = np.zeros((len(onlytrafo),24,3))#to store all phases Amps loading at HV side 
    #Transf_Max_Amps_loading = np.zeros((len(onlytrafo),24))#to store maximun amps loading at HV side (the maximun of the three phases)       
    #amp_rate=[0 for i in range(len(onlytrafo))]

    #calculate Amps loading at each phase in pu for each transformer
    for itrafo, trafo in enumerate(onlytrafo):
            DSSCircuit.SetActiveElement('Transformer.%s' %(trafo))
            amp_rate = DSSCircuit.ActiveElement.NormalAmps#get Normal ampere rating (OpenDSS defines it for Winding 1)
            Transf_Wdg1_Amps[itrafo,:,0]=(np.sqrt(All_Wdg_Amp[itrafo,:,0]**2+All_Wdg_Amp[itrafo,:,1]**2))#HV side Wdg current , phase 1
            Transf_Wdg1_Amps[itrafo,:,1]=(np.sqrt(All_Wdg_Amp[itrafo,:,8]**2+All_Wdg_Amp[itrafo,:,9]**2)) #HV side Wdg current , phase 2
            Transf_Wdg1_Amps[itrafo,:,2]=(np.sqrt(All_Wdg_Amp[itrafo,:,16]**2+All_Wdg_Amp[itrafo,:,17]**2))#HV side Wdg current , phase 3

            Transf_Amps_loading[itrafo,:,0]=Transf_Wdg1_Amps[itrafo,:,0]/amp_rate #HV side Amps loading, phase 1 
            Transf_Amps_loading[itrafo,:,1]=Transf_Wdg1_Amps[itrafo,:,1]/amp_rate #HV side Amps loading, phase 2
            Transf_Amps_loading[itrafo,:,2]=Transf_Wdg1_Amps[itrafo,:,2]/amp_rate #HV side Amps loading, phase 3

    #*********For each transformer, at each hour, get the maximun loading of the three phases
    Max_Transf_Amps = np.max(Transf_Amps_loading, axis=2)

    #Each dataframe has 24 rows and a column for Amps loading of each transformer
    dfAmpsTrafo_phA_SC1 = pd.DataFrame(np.vstack(Transf_Amps_loading[:,:,0].T),columns=onlytrafo)
    dfAmpsTrafo_phB_SC1 = pd.DataFrame(np.vstack(Transf_Amps_loading[:,:,1].T),columns=onlytrafo)
    dfAmpsTrafo_phC_SC1 = pd.DataFrame(np.vstack(Transf_Amps_loading[:,:,2].T),columns=onlytrafo)

    dfAmpsTrafo_Max_SC1 = pd.DataFrame(np.vstack(Max_Transf_Amps[:,:].T),columns=onlytrafo)

    #plots
    ax = dfAmpsTrafo_phA_SC1.plot(figsize=(6,3))
    plt.title('Transformer Amps Loading - phase 1',fontsize=9)
    plt.legend(fontsize=6,loc="upper left") 
    plt.yticks(fontsize=8)
    plt.xlabel("hour",fontsize=8)
    plt.ylabel("p.u.",fontsize=8)
    plt.xticks([0,3,6,9,12,15,18,21,24],fontsize=8)

    ax = dfAmpsTrafo_phB_SC1.plot(figsize=(6,3))
    plt.title('Transformer Amps Loading - phase 2',fontsize=9)
    plt.legend(fontsize=6,loc="upper left") 
    plt.yticks(fontsize=8)
    plt.xlabel("hour",fontsize=8)
    plt.ylabel("p.u.",fontsize=8)
    plt.xticks([0,3,6,9,12,15,18,21,24],fontsize=8)

    ax = dfAmpsTrafo_phC_SC1.plot(figsize=(6,3))
    plt.title('Transformer Amps Loading - phase 3',fontsize=9)
    plt.legend(fontsize=6,loc="upper left") 
    plt.yticks(fontsize=8)
    plt.xlabel("hour",fontsize=8)
    plt.ylabel("p.u.",fontsize=8)
    plt.xticks([0,3,6,9,12,15,18,21,24],fontsize=8)

    ax = dfAmpsTrafo_Max_SC1.plot(figsize=(6,3))
    plt.title('Transformer Maximun Amps Loading',fontsize=9)
    plt.legend(fontsize=6,loc="upper left") 
    plt.yticks(fontsize=8)
    plt.xlabel("hour",fontsize=8)
    plt.ylabel("p.u.",fontsize=8)
    plt.xticks([0,3,6,9,12,15,18,21,24],fontsize=8)

    plt.show()


# In[ ]:


results_transformer_amps_loading()


# In[ ]:


def  Results_for_load_power():
    #display(All_Wdg_Amp[1,:,:])
    #display(All_Wdg_Amp[1,:,0])
    #display(Transf_Amps_loading[:,:,0])
    #display((Transf_Amps_loading[:,:,1]))
    #display(dfAmpsTrafo_phA_SC1)


    #*******------Results for load power
    #each dataframe has a column associated with each load and 24 lines
    dfLoad_kW = pd.DataFrame(np.vstack(Load_kW[:,:].T),columns=Loadnames)
    dfLoad_kvar = pd.DataFrame(np.vstack(Load_kvar[:,:].T),columns=Loadnames)

    #plots
    ax = dfLoad_kW.plot(figsize=(6,3))
    plt.title('Load active power',fontsize=9)
    plt.legend(fontsize=6,loc="upper left") 
    plt.yticks(fontsize=8)
    plt.xlabel("hour",fontsize=8)
    plt.ylabel("kW",fontsize=8)
    plt.xticks([0,3,6,9,12,15,18,21,24],fontsize=8)

    ax = dfLoad_kvar.plot(figsize=(6,3))
    plt.title('Load reactive power',fontsize=9)
    plt.legend(fontsize=6,loc="upper left") 
    plt.yticks(fontsize=8)
    plt.xlabel("hour",fontsize=8)
    plt.ylabel("kvar",fontsize=8)
    plt.xticks([0,3,6,9,12,15,18,21,24],fontsize=8)
    plt.show()


# In[ ]:


Results_for_load_power()


# In[ ]:


def Results_for_substation():
    Total_Act_Power_Sub = [x * -1 for x in Total_Act_Power]
    Total_React_Power_Sub = [x * -1 for x in Total_React_Power]
    #Create figure
    plt.figure(figsize=(15,4))
    plt.suptitle('Power at the substation')

    #Active power
    plt.subplot(1,3,1)
    plt.plot(Total_Act_Power_Sub)
    plt.title('Circuit active power',fontsize=9)
    plt.yticks(fontsize=8)
    plt.xlabel("hour",fontsize=8)
    plt.ylabel("kW",fontsize=8)
    plt.xticks([0,3,6,9,12,15,18,21,24],fontsize=8)

    #Reactive power
    plt.subplot(1,3,2)
    plt.plot(Total_React_Power_Sub)
    plt.title('Circuit reactive power',fontsize=9)
    plt.yticks(fontsize=8)
    plt.xlabel("hour",fontsize=8)
    plt.ylabel("kvar",fontsize=8)
    plt.xticks([0,3,6,9,12,15,18,21,24],fontsize=8)

    #Losses
    # Calculate the percentage of total active losses to total active power
    percentage_losses = [abs(loss / power) * 100 for loss, power in zip(Total_Act_Losses, Total_Act_Power)]

    plt.subplot(1,3,3)
    plt.plot(percentage_losses)
    plt.title('Circuit total active losses',fontsize=9)
    plt.yticks(fontsize=8)
    plt.xlabel("hour",fontsize=8)
    plt.ylabel("%",fontsize=8)
    plt.xticks([0,3,6,9,12,15,18,21,24],fontsize=8)

    plt.show()


# In[ ]:


Results_for_substation()


# In[ ]:


def Results_for_Line_Amps_Loading():

    Line_Max_Loading = np.zeros((len(Linenames),24))
    for iline, line in enumerate(Linenames):
        DSSCircuit.SetActiveElement('Line.%s' %(line))
        amp_rate = DSSCircuit.ActiveElement.NormalAmps
        Line_Max_Loading[iline,:] = Line_Max_Amp[iline,:]/amp_rate

    dfLine_Max_Amp = pd.DataFrame(np.vstack(Line_Max_Loading[:,:].T),columns=Linenames)

    #plots
    ax = dfLine_Max_Amp.plot(figsize=(6,3))
    plt.title('Line Amps Loading',fontsize=9)
    plt.legend(fontsize=6,loc="upper left") 
    plt.yticks(fontsize=8)
    plt.xlabel("hour",fontsize=8)
    plt.ylabel("pu",fontsize=8)
    plt.xticks([0,3,6,9,12,15,18,21,24],fontsize=8)

    plt.show()


# In[ ]:


Results_for_Line_Amps_Loading()


# In[ ]:


def Pvsystemsetup():
    #Define curves fo the PV System: TempxPerature x Output Power(pu) and Output Power(pu) x Inversor efficiency
    #(there is no irradiance curce because it won´t be a daily simulation)
    DSSText.Command = 'New XYcurve.PvsT npts=4 xarray=[0 25 75 100] yarray=[1.2 1 .8 .6]'
    DSSText.Command = 'New XYcurve.Effic npts=4 xarray=[.1 .2 .4 1] yarray=[0.86 .9 .93 .97]'
    DSSText.Command = 'New loadshape.Irrad npts=24 interval=1  mult=[0 0 0 0 0 0 .1 .2 .3 .5 .8 .9 1.0 1.0 .99 .9 .7 .4 .1 0 0 0 0 0] '
    DSSText.Command = 'New Tshape.Temp npts=24 interval=1 temp=[25 25 25 25 25 25 25 25 35 40 45 50 60 60 55 40 35 30 25 25 25 25 25 25]'
    print('PV system curves created')


# In[ ]:


Pvsystemsetup()


# In[ ]:


def Pvsystem(pmpp_x, kva_inv):

    DSSText.Command = 'New PVSystem.PV_1 phases=3 bus1=728.1.2.3 kv=4.8 conn=delta irrad=1.0 pmpp=' + str(pmpp_x) + ' kva=' + str(kva_inv) + ' temperature=25 pf=1 %cutin=0.05 %cutout=0.05 effcurve=Effic P-tcurve=PvsT Daily=Irrad Tdaily=Temp'
    DSSText.Command = 'New PVSystem.PV_2 phases=3 bus1=733.1.2.3 kv=4.8 conn=delta irrad=1.0 pmpp=' + str(pmpp_x) + ' kva=' + str(kva_inv) + ' temperature=25 pf=1 %cutin=0.05 %cutout=0.05 effcurve=Effic P-tcurve=PvsT Daily=Irrad Tdaily=Temp'
    DSSText.Command = 'New PVSystem.PV_3 phases=3 bus1=737.1.2.3 kv=4.8 conn=delta irrad=1.0 pmpp=' + str(pmpp_x) + ' kva=' + str(kva_inv) + ' temperature=25 pf=1 %cutin=0.05 %cutout=0.05 effcurve=Effic P-tcurve=PvsT Daily=Irrad Tdaily=Temp'
    DSSText.Command = 'New PVSystem.PV_4 phases=3 bus1=740.1.2.3 kv=4.8 conn=delta irrad=1.0 pmpp=' + str(pmpp_x) + ' kva=' + str(kva_inv) + ' temperature=25 pf=1 %cutin=0.05 %cutout=0.05 effcurve=Effic P-tcurve=PvsT Daily=Irrad Tdaily=Temp'
    DSSText.Command = 'New PVSystem.PV_5 phases=3 bus1=718.1.2.3 kv=4.8 conn=delta irrad=1.0 pmpp=' + str(pmpp_x) + ' kva=' + str(kva_inv) + ' temperature=25 pf=1 %cutin=0.05 %cutout=0.05 effcurve=Effic P-tcurve=PvsT Daily=Irrad Tdaily=Temp'
    DSSText.Command = 'New PVSystem.PV_6 phases=3 bus1=720.1.2.3 kv=4.8 conn=delta irrad=1.0 pmpp=' + str(pmpp_x) + ' kva=' + str(kva_inv) + ' temperature=25 pf=1 %cutin=0.05 %cutout=0.05 effcurve=Effic P-tcurve=PvsT Daily=Irrad Tdaily=Temp'
    DSSText.Command = 'New PVSystem.PV_7 phases=3 bus1=722.1.2.3 kv=4.8 conn=delta irrad=1.0 pmpp=' + str(pmpp_x) + ' kva=' + str(kva_inv) + ' temperature=25 pf=1 %cutin=0.05 %cutout=0.05 effcurve=Effic P-tcurve=PvsT Daily=Irrad Tdaily=Temp'
    DSSText.Command = 'New PVSystem.PV_8 phases=3 bus1=742.1.2.3 kv=4.8 conn=delta irrad=1.0 pmpp=' + str(pmpp_x) + ' kva=' + str(kva_inv) + ' temperature=25 pf=1 %cutin=0.05 %cutout=0.05 effcurve=Effic P-tcurve=PvsT Daily=Irrad Tdaily=Temp'
    print('PV systems created with pmpp=' + str(pmpp_x) + ' and kva=' + str(kva_inv))


# In[ ]:


Pvsystem(3000, 3000)


# In[ ]:


def pvplot():
    # Create a figure and axis
    fig, ax = plt.subplots(figsize=(7, 4))

    # Plot the PV system outputs
    for i in range(1, 9):
        DSSCircuit.SetActiveElement(f'PVSystem.PV_{i}')
        pv_output = DSSCircuit.ActiveElement.Powers[0]  # Active power output
        ax.plot(pv_output, label=f'PV_{i}')

    # Customize the plot
    ax.set_title('PV System Outputs')
    ax.set_xlabel('Hour')
    ax.set_ylabel('Active Power (kW)')
    ax.legend()
    plt.grid()
    plt.show()


# In[ ]:


pvplot()


# In[ ]:


def storagesetup():
        # curva de eficiência e curva de despacho do storage (negativo carrega, positivo descarrega)
        # a de despacho é rascunho meu, ajustar quando definir
    DSSText.Command = 'New XYcurve.Eff npts=4 xarray=[.1 .2 .4 1] yarray=[0.86 .9 .93 .97]'
    DSSText.Command = 'New LoadShape.dispatch_shape npts=24 interval=1 mult=[0 0 0 0 0 0 0 0 0 0 -0.3 -0.4 -0.45 -0.45 -0.45 -0.4 -0.15 0.2 0.4 0.6 0.6 0.4 0.2 0]'


# In[ ]:


storagesetup()


# In[ ]:


#exemplo: DSSText.Command = 'New Storage.StoCentral phases=3 bus1=709.1.2.3 kv=4.8 conn=delta kWrated=2464 kWhrated=10000 %stored=20 %reserve=20 effcurve=Eff dispmode=follow daily=dispatch_shape pf=1'
def add_storage(nome, bus, kw, kwh, kv=4.8, phases=3, conn="delta",
            stored=20, reserve=20):
    DSSText.Command = (f"New Storage.{nome} phases={phases} bus1={bus} kv={kv} conn={conn} "f"kWrated={kw} kWhrated={kwh} %stored={stored} %reserve={reserve}""effcurve=Eff dispmode=follow daily=dispatch_shape pf=1")

    # um storage
    add_storage("StoCentral", "709.1.2.3", 2464, 10000)

    # varios, de uma lista
    bess = [
        ("Sto1", "709.1.2.3", 1000, 4000),
        ("Sto2", "734.1.2.3", 1464, 6000),
    ]
    for nome, bus, kw, kwh in bess:
        add_storage(nome, bus, kw, kwh)


# In[ ]:


def storageplot():
    # Create a figure and axis
    fig, ax = plt.subplots(figsize=(7, 4))

    # Plot the storage outputs
    for i in range(1, 3):
        DSSCircuit.SetActiveElement(f'Storage.Sto{i}')
        storage_output = DSSCircuit.ActiveElement.Powers[0]  # Active power output
        ax.plot(storage_output, label=f'Sto{i}')

    # Customize the plot
    ax.set_title('Storage System Outputs')
    ax.set_xlabel('Hour')
    ax.set_ylabel('Active Power (kW)')
    ax.legend()
    plt.grid()
    plt.show()


# In[ ]:


storageplot()


# In[ ]:


def ilhamento(linhailha):  #exemplo: abre a L27 no terminal 1 (liga a 730 na 709)
    DSSText.Command = 'Open Line.str({linhailha}) Term=1'

    # carga (kW) e prioridade de corte, menor prioridade primeiro (ainda a confirmar)
    CARGAS_ILHA = [('S736b',42),('S741c',42),('S732c',42),('S734c',42),('S735c',85),
                ('S733a',85),('S740c',85),('S738a',126),('S737a',140)]

    N_CORTE = 0   # quantas cargas cortar, na ordem da lista (0 = sem corte). Muda e roda de novo a partir do Reset
    for nome, kw in CARGAS_ILHA[:N_CORTE]:
        DSSText.Command = 'Edit Load.' + nome + ' enabled=no'


# In[ ]:


ilhamento('L27')


# In[ ]:


def set_norm_vminmax_pu(pumin, pumax):
    DSSText.Command = f'set normvminpu={pumin}'
    DSSText.Command = f'set normvmaxpu={pumax}'
    print(f'Voltage limits set to {pumin} p.u. and {pumax} p.u.')


# In[ ]:


set_norm_vminmax_pu(0.93, 1.05)


# In[ ]:


def overload():
    # Get the maximum line current (first terminal only, any number of phases)
    for iline, line in enumerate(Linenames):
        DSSCircuit.SetActiveElement('line.%s' % line)
        elem = DSSCircuit.ActiveElement
        ncond = elem.NumConductors      # conductors per terminal
        mags = elem.CurrentsMagAng[0:2*ncond:2]
        Line_Max_Amp[iline, h] = max(mags)

    plot        


# In[ ]:


def undernovervoltage():
    # Get the voltage at all nodes (in p.u.) for each phase
    busVpuA_SC1[h] = DSSCircuit.AllNodeVmagPUByPhase(1)
    busVpuB_SC1[h] = DSSCircuit.AllNodeVmagPUByPhase(2)
    busVpuC_SC1[h] = DSSCircuit.AllNodeVmagPUByPhase(3)
    for i in range(len(busVpuA_SC1[h])):
        if busVpuA_SC1[h][i] < 0.93 or busVpuA_SC1[h][i] > 1.05:
            print(f"Voltage violation at bus {DSSCircuit.AllNodeNamesByPhase(1)[i]}: {busVpuA_SC1[h][i]} p.u.")
    for i in range(len(busVpuB_SC1[h])):
        if busVpuB_SC1[h][i] < 0.93 or busVpuB_SC1[h][i] > 1.05:
            print(f"Voltage violation at bus {DSSCircuit.AllNodeNamesByPhase(2)[i]}: {busVpuB_SC1[h][i]} p.u.")
    for i in range(len(busVpuC_SC1[h])):
        if busVpuC_SC1[h][i] < 0.93 or busVpuC_SC1[h][i] > 1.05:
            print(f"Voltage violation at bus {DSSCircuit.AllNodeNamesByPhase(3)[i]}: {busVpuC_SC1[h][i]} p.u.")




# In[ ]:


undernovervoltage()

