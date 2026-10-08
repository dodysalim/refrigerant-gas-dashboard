from build_powerbi import *
from build_powerbi import PROJECT_ROOT
import sys, ast, numpy as np
from sklearn.model_selection import train_test_split
from scipy.stats import ks_2samp, chi2_contingency

def krio():
 repo='refrigerant-gas-dashboard';r=Report(repo,'KrioMetrics','55 gases · curvas del motor original · estimaciones conceptuales, no tablas certificadas')
 p=PROJECT_ROOT/'data/processed';g=pd.read_csv(p/'dim_refrigerant.csv');temp=pd.read_csv(p/'dim_temperature.csv');state=pd.read_csv(p/'dim_state.csv');facts=pd.read_csv(p/'fact_pressure_temperature.csv')
 names={'ashrae_name':'Refrigerante','compound_type':'Compuesto','safety_group':'Seguridad','gwp':'GWP','odp':'ODP','status':'Estado','boiling_point_c':'Ebullicion_C','critical_temp_c':'Critica_C','critical_pressure_bar':'Critica_bar','true_replacement':'Sustituto','primary_oil':'Aceite','description':'Descripcion','pros':'Ventajas','cons':'Precauciones'}
 gases=g[list(names)].rename(columns=names);r.table('Gases',gases,metrics('Gases',[('Gases','COUNTROWS(Gases)'),('GWP','AVERAGE(Gases[GWP])'),('ODP','AVERAGE(Gases[ODP])'),('SinODP','CALCULATE(COUNTROWS(Gases), Gases[ODP]=0)')]))
 sys.path.insert(0,str(PROJECT_ROOT));from src.presentation.dashboard.pt_solver import solve_pt_interpolated
 curves=[];cycles=[]
 for _,gas in g.iterrows():
  for t in range(-50,71):
   for s in ['Bubble','Dew']:curves.append([gas.ashrae_name,t,s,solve_pt_interpolated(gas,t,s)])
  for e in range(-50,11,5):
   for c in range(20,71,5):
    lo=solve_pt_interpolated(gas,e);hi=solve_pt_interpolated(gas,c);cycles.append([gas.ashrae_name,e,c,lo,hi,hi/lo,max(0,lo-1.01325),max(0,hi-1.01325)])
 r.table('Curvas',pd.DataFrame(curves,columns=['Refrigerante','Temperatura_C','Fase','Presion_bar']),metrics('Curvas',[('Presion','AVERAGE(Curvas[Presion_bar])')]))
 r.table('Ciclos',pd.DataFrame(cycles,columns=['Refrigerante','Evaporacion_C','Condensacion_C','Baja_bar','Alta_bar','Relacion','Succion_barg','Descarga_barg']),metrics('Ciclos',[(n,f'IF(COUNTROWS(Ciclos)=1, MAX(Ciclos[{c}]), BLANK())') for n,c in [('Baja','Baja_bar'),('Alta','Alta_bar'),('Compresion','Relacion'),('Succion','Succion_barg')]]))
 f=facts.merge(g[['refrigerant_key','ashrae_name']],on='refrigerant_key').merge(temp,on='temperature_key').merge(state,on='state_key');r.table('Almacen',f[['ashrae_name','temperature_c','state_name','pressure_bar','pressure_psi']].rename(columns={'ashrae_name':'Refrigerante'}))
 for t in ['Curvas','Ciclos','Almacen']:r.relation(t,'Refrigerante','Gases','Refrigerante')
 fil=[('Gases','Refrigerante'),('Gases','Compuesto'),('Gases','Seguridad')]
 r.page('control','01 · Dashboard de control',fil);r.cards('Gases',list(r.measures['Gases']));r.chart('Gases','Refrigerante','KPI_GWP','Impacto climático · GWP',30,270);r.chart('Gases','Seguridad','KPI_Gases','Distribución por seguridad',650,270,kind='donut');r.chart('Gases','Refrigerante','KPI_ODP','Agotamiento de ozono · ODP',30,560);r.chart('Gases','Compuesto','KPI_Gases','Familias de refrigerantes',650,560)
 r.page('calculadora','02 · Calculadora P-T',[('Gases','Refrigerante'),('Curvas','Temperatura_C'),('Curvas','Fase')],note='Selecciona un gas y temperatura. Presión absoluta estimada con el mismo motor de Streamlit; no usar para dimensionamiento.')
 r.chart('Curvas','Temperatura_C','KPI_Presion','Curvas P-T · burbuja y rocío',30,160,1220,370,kind='line',legend='Fase');r.tablevisual('Curvas',['Refrigerante','Temperatura_C','Fase','Presion_bar'],'Valores de trabajo',30,550,600,280);r.tablevisual('Gases',['Refrigerante','Aceite','Sustituto','Precauciones'],'Ficha técnica y compatibilidad',650,550,600,280)
 r.page('comparador','03 · Comparador termodinámico',fil,note='Selecciona hasta tres gases para comparar las curvas; fase burbuja/rocío en la página Calculadora P-T.')
 r.chart('Curvas','Temperatura_C','KPI_Presion','Comparativa de presión · misma temperatura',30,160,1220,370,kind='line',legend='Refrigerante');r.tablevisual('Gases',['Refrigerante','Compuesto','Seguridad','GWP','ODP','Sustituto'],'Alternativas y propiedades',30,550,1220,280)
 r.page('ciclo','04 · Ciclo de refrigeración',[('Gases','Refrigerante'),('Ciclos','Evaporacion_C'),('Ciclos','Condensacion_C')],note='Escenarios cada 5 °C. Selecciona un único gas y par de temperaturas para mostrar KPIs. La entalpía del original es conceptual.')
 r.cards('Ciclos',list(r.measures['Ciclos']));r.tablevisual('Ciclos',list(r.tables['Ciclos'].columns),'Presiones y relación de compresión · escenarios del motor original',30,280,1220,330);r.tablevisual('Gases',['Refrigerante','Sustituto','Precauciones'],'Sustituto y precauciones',30,640,1220,190)
 r.page('almacen','05 · Almacén SQL relacional',[('Gases','Refrigerante'),('Almacen','state_name'),('Almacen','temperature_c')]);r.tablevisual('Almacen',list(r.tables['Almacen']),'Tabla de hechos P-T',30,160,1220,390);r.tablevisual('Gases',['Refrigerante','Descripcion','Ventajas','Precauciones'],'Dimensión de refrigerantes',30,570,1220,260)
 return r.finish('| Streamlit | Power BI |\n|---|---|\n| Dashboard de Control | Control con GWP, ODP, familia y seguridad |\n| Calculadora P-T | Curvas y tabla exportadas con el mismo `solve_pt_interpolated` |\n| Comparador | Curvas multigas y fichas |\n| Ciclo de Refrigeración | Escenarios discretos cada 5 °C, presiones y relación; no entalpía física |\n| Almacén SQL | Tablas filtrables; consultas/escrituras siguen en Streamlit |')
if __name__=='__main__':
    print(krio())
