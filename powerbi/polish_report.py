from pathlib import Path
import json,re,copy
roots=[Path(__file__).resolve().parent]
changed={}
if all(json.loads(f.read_text()).get('height')==1040 for root in roots for f in (root/'Analytics.Report/definition/pages').rglob('page.json')):
 print('La presentación ya está ajustada.');raise SystemExit(0)
for root in roots:
 fs=[]
 for f in (root/'Analytics.Report/definition/pages').rglob('*.json'):
  if f.name=='page.json' and json.loads(f.read_text()).get('height')==1040: continue
  v=json.loads(f.read_text())
  if f.name=='page.json':v['height']=1040
  elif f.name=='visual.json':
   p=v['position'];typ=v['visual']['visualType'];o=v['visual'].setdefault('objects',{})
   if v['name']=='header':p.update(y=12,height=60)
   elif v['name']=='footer':p.update(y=990,height=42)
   elif typ=='slicer':p.update(y=88,height=76)
   else:p.update(y=round(180+(p['y']-160)*1.16),height=round(p['height']*1.16))
   if typ=='card':
    o['labels']=[{'properties':{'fontSize':{'expr':{'Literal':{'Value':'24D'}}},'labelDisplayUnits':{'expr':{'Literal':{'Value':'1D'}}},'labelPrecision':{'expr':{'Literal':{'Value':'2D'}}}}}]
    o['categoryLabels']=[{'properties':{'show':{'expr':{'Literal':{'Value':'false'}}}}}]
   if typ=='slicer':
    col=v['visual']['query']['queryState']['Values']['projections'][0]['nativeQueryRef']
    o['header']=[{'properties':{'show':{'expr':{'Literal':{'Value':'true'}}},'text':{'expr':{'Literal':{'Value':"'"+col.replace('_',' ')+"'"}}}}}]
    cont=v['visual'].get('visualContainerObjects',{})
    if 'title' in cont:cont['title'][0]['properties']['show']['expr']['Literal']['Value']='false'
   if typ=='tableEx':
    o['grid']=[{'properties':{'rowPadding':{'expr':{'Literal':{'Value':'6D'}}}}}]
   if typ=='textbox':
    for para in o.get('general',[{}])[0].get('properties',{}).get('paragraphs',[]):
     for run in para.get('textRuns',[]):run['textStyle']['fontSize']='19pt' if v['name']=='header' else '10pt'
   assert p['x']+p['width']<=1280 and p['y']+p['height']<=1040,(f,p)
  f.write_text(json.dumps(v,ensure_ascii=False,indent=2)+'\n');fs.append(f)
 # Explicit unavailable status replaces blanks in cards only, preserving numeric measures and charts.
 defs=root/'Analytics.SemanticModel/definition/tables'
 for f in defs.glob('*.tmdl'):
  s=f.read_text()
  if root.parent.name=='refrigerant-gas-dashboard' and f.stem=='Ciclos':
   for name,col in [('Baja','Baja_bar'),('Alta','Alta_bar'),('Compresion','Relacion'),('Succion','Succion_barg')]:
    s=re.sub(r'(\tmeasure KPI_'+name+r' = )[^\n]+',lambda m:m.group(1)+f'IF(COUNTROWS(Ciclos)=1, FORMAT(MAX(Ciclos[{col}]), "0.00"), "Selecciona escenario")',s)
   f.write_text(s);fs.append(f)
  if root.parent.name in ['FleetLogix-Master','Proyecto-No-Country','S02-26-E45-Data_Science_EquineLead']:
   # Card-specific text measures; charts keep numeric measures. Missing data is not zero.
   cards=[]
   for vf in (root/'Analytics.Report/definition/pages').rglob('visual.json'):
    v=json.loads(vf.read_text())
    if v['visual']['visualType']=='card':
     pr=v['visual']['query']['queryState']['Values']['projections'][0];m=pr['field']['Measure']
     if m['Expression']['SourceRef']['Entity']==f.stem:
      name=m['Property'];cards.append(name);m['Property']=name+'_Estado';pr['queryRef']=f.stem+'.'+name+'_Estado';pr['nativeQueryRef']='Estado de datos';vf.write_text(json.dumps(v,ensure_ascii=False,indent=2)+'\n')
   for name in set(cards):
    s=s.replace('\tpartition ',f'\tmeasure {name}_Estado = IF(COUNTROWS({f.stem})=0, "Datos pendientes", FORMAT([{name}], "#,0.00"))\n\t\tformatString: General\n\n\tpartition ',1)
   if cards:f.write_text(s);fs.append(f)
 readme=root/'README.md';readme.write_text(readme.read_text()+'\n## Presentación y selección\n\nLienzo ampliado a 1280×1040, tarjetas sin abreviación automática, filtros con su propio encabezado y tablas con más espacio. El ciclo muestra «Selecciona escenario» hasta elegir un único gas, temperatura de evaporación y condensación. Los proyectos sin datos muestran «Datos pendientes»; no se sustituyen datos desconocidos por ceros.\n');fs.append(readme)
 changed[root.parent.name]=[{'path':str(f.relative_to(root.parent)),'mode':'100644','type':'blob','content':f.read_text()} for f in fs]
print('Presentación actualizada')
