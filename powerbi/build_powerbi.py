from pathlib import Path
import json,copy,shutil,re,uuid
import pandas as pd
PROJECT_ROOT=Path(__file__).resolve().parents[1]
ROOT=PROJECT_ROOT.parent
BASE=PROJECT_ROOT/'powerbi'
SNAP=Path(__file__).with_name('templates.json')
if SNAP.exists():
 _snapshot=json.loads(SNAP.read_text());TEMPLATES=_snapshot['visuals'];BASEPAGE=_snapshot['page']
else:
 pages=BASE/'Analytics.Report/definition/pages'
 TEMPLATES={}
 for f in pages.rglob('visual.json'):
  v=json.loads(f.read_text());k={'clusteredBarChart':'chart','textbox':('header' if f.parent.name=='header' else 'footer'),'slicer':'slicer','card':'card','tableEx':'table'}.get(v['visual']['visualType'])
  if k and k not in TEMPLATES:TEMPLATES[k]=v
 if 'table' not in TEMPLATES:
  f=next((ROOT/'Cliente360-Predictive-Insight/powerbi/Analytics.Report/definition/pages').rglob('visual.json'))
  fs=list((ROOT/'Cliente360-Predictive-Insight/powerbi/Analytics.Report/definition/pages').rglob('visual.json'))
  TEMPLATES['table']=next(json.loads(f.read_text()) for f in fs if json.loads(f.read_text())['visual']['visualType']=='tableEx')
 BASEPAGE=json.loads(next(pages.rglob('page.json')).read_text())
 SNAP.write_text(json.dumps({'visuals':TEMPLATES,'page':BASEPAGE},ensure_ascii=False))
def write(p,obj):
 p.parent.mkdir(parents=True,exist_ok=True);p.write_text(json.dumps(obj,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
def field(t,c,measure=False):return {('Measure' if measure else 'Column'):{'Expression':{'SourceRef':{'Entity':t}},'Property':c}}
def projection(t,c,m=False):return {'field':field(t,c,m),'queryRef':t+'.'+c,'nativeQueryRef':c,'displayName':c,'active':True}
class Report:
 def __init__(self,repo,title,status):
  self.repo=repo;self.title=title;self.status=status;self.root=BASE;self.pages=[];self.tables={};self.measures={};self.relationships=[]
  if not self.root.exists():
   shutil.copytree(BASE,self.root,ignore=shutil.ignore_patterns('data','pages','.pbi','*.tmdl','README.md'))
  self.old={str(p.relative_to(self.root)) for p in self.root.rglob('*') if p.is_file()}
  shutil.rmtree(self.root/'Analytics.Report/definition/pages',ignore_errors=True)
  shutil.rmtree(self.root/'Analytics.SemanticModel/definition/tables',ignore_errors=True)
  shutil.rmtree(self.root/'data',ignore_errors=True)
 def table(self,name,df,measures=None):
  df=df.copy();df.columns=[str(c) for c in df.columns];self.tables[name]=df;self.measures[name]=measures or {}
  (self.root/'data').mkdir(exist_ok=True);df.to_csv(self.root/'data'/f'{name}.csv',index=False,encoding='utf-8',float_format='%.10g')
 def relation(self,fromtable,fromcolumn,totable,tocolumn):self.relationships.append((fromtable,fromcolumn,totable,tocolumn))
 def page(self,name,label,filters=(),note=None):
  self.pages.append(name);self.pg=self.root/'Analytics.Report/definition/pages'/name;self.idx=0
  p=copy.deepcopy(BASEPAGE);p['name']=name;p['displayName']=label;p['width']=1280;p['height']=900;write(self.pg/'page.json',p)
  self.text('header',self.title+' | '+label,30,12,1220,48)
  self.text('footer',note or self.status,30,850,1220,40)
  for i,(t,c) in enumerate(filters):self.visual('slicer',f'f{i}',30+310*i,78,300,65,{'Values':{'projections':[projection(t,c)]}})
 def text(self,kind,text,x,y,w,h):
  v=copy.deepcopy(TEMPLATES[kind]);v['visual']['objects']['general'][0]['properties']['paragraphs'][0]['textRuns'][0]['value']=text;self.emit(v,kind,x,y,w,h)
 def emit(self,v,name,x,y,w,h):
  self.idx+=1;v['name']=name;v['position']={'x':x,'y':y,'z':self.idx,'height':h,'width':w,'tabOrder':self.idx};write(self.pg/'visuals'/name/'visual.json',v)
 def visual(self,kind,name,x,y,w,h,query,title=None,vtype=None):
  v=copy.deepcopy(TEMPLATES[kind]);vv=v['visual'];vv['query']={'queryState':query};vv.pop('syncGroup',None)
  if vtype:vv['visualType']=vtype
  if 'visualContainerObjects' not in vv:vv['visualContainerObjects']=copy.deepcopy(TEMPLATES['chart']['visual']['visualContainerObjects'])
  if title:vv['visualContainerObjects']['title'][0]['properties']['text']['expr']['Literal']['Value']="'"+title.replace("'","''")+"'"
  self.emit(v,name,x,y,w,h)
 def chart(self,t,c,m,title,x,y,w=600,h=280,kind='bar',legend=None):
  q={'Category':{'projections':[projection(t,c)]},'Y':{'projections':[projection(t,m,True)]}}
  if legend:q['Series']={'projections':[projection(t,legend)]}
  self.visual('chart','chart'+str(self.idx),x,y,w,h,q,title,{'bar':'clusteredBarChart','column':'clusteredColumnChart','line':'lineChart','donut':'donutChart'}[kind])
 def tablevisual(self,t,cols,title,x=30,y=160,w=1220,h=640):self.visual('table','table'+str(self.idx),x,y,w,h,{'Values':{'projections':[projection(t,c,c in self.measures[t]) for c in cols]}},title)
 def cards(self,t,metrics):
  for i,m in enumerate(metrics):self.visual('card','kpi'+str(i),30+i*310,160,300,90,{'Values':{'projections':[projection(t,m,True)]}},m.replace('KPI_',''))
 def finish(self,parity):
  definition=self.root/'Analytics.SemanticModel/definition';definition.mkdir(parents=True,exist_ok=True)
  for t,df in self.tables.items():
   out=[f'table {t}',''];types=[]
   for c in df:
    typ='double' if pd.api.types.is_numeric_dtype(df[c]) else 'string';mtyp='type number' if typ=='double' else 'type text';types.append('{"'+c+'", '+mtyp+'}')
    out += [f"\tcolumn '{c}'",f'\t\tdataType: {typ}','\t\tsummarizeBy: none',f'\t\tsourceColumn: {c}','']
   for m,(expr,fmt) in self.measures[t].items():out += [f'\tmeasure {m} = {expr}',f'\t\tformatString: {fmt}','\t\tdisplayFolder: Indicadores','']
   out += [f'\tpartition {t} = m','\t\tmode: import','\t\tsource =','\t\t\t\tlet',f'\t\t\t\t    Source = Csv.Document(File.Contents(DataFolder & "{t}.csv"), [Delimiter=",", Encoding=65001, QuoteStyle=QuoteStyle.Csv]),','\t\t\t\t    Headers = Table.PromoteHeaders(Source, [PromoteAllScalars=true]),','\t\t\t\t    Typed = Table.TransformColumnTypes(Headers, {'+', '.join(types)+'}, "en-US")','\t\t\t\tin','\t\t\t\t    Typed','']
   p=definition/'tables'/f'{t}.tmdl';p.parent.mkdir(exist_ok=True);p.write_text('\n'.join(out),encoding='utf-8')
  (definition/'model.tmdl').write_text('model Model\n\tculture: es-ES\n\tdefaultPowerBIDataSourceVersion: powerBI_V3\n\tsourceQueryCulture: en-US\n\n'+''.join(f'ref table {t}\n' for t in self.tables)+'ref expression DataFolder\n',encoding='utf-8')
  if not (definition/'database.tmdl').exists():(definition/'database.tmdl').write_text('database\n\tcompatibilityLevel: 1600\n',encoding='utf-8')
  (definition/'relationships.tmdl').write_text('\n'.join(f'relationship {uuid.uuid5(uuid.NAMESPACE_DNS,self.repo+"|"+"|".join(r))}\n\tfromColumn: {r[0]}.\'{r[1]}\'\n\ttoColumn: {r[2]}.\'{r[3]}\'\n' for r in self.relationships),encoding='utf-8')
  (definition/'expressions.tmdl').write_text('expression DataFolder = "C:\\Dody-PowerBI\\'+self.repo+'\\powerbi\\data\\" meta [IsParameterQuery=true, Type="Text", IsParameterQueryRequired=true]\n\tkind: m\n',encoding='utf-8')
  write(self.root/'Analytics.Report/definition/pages/pages.json',{'$schema':'https://developer.microsoft.com/json-schemas/fabric/item/report/definition/pagesMetadata/1.0.0/schema.json','pageOrder':self.pages,'activePageName':self.pages[0]})
  # configure_data.py is kept beside this module
  readme=f'# {self.title} — Power BI\n\n{self.status}\n\n## Abrir\n\n1. Descarga el repositorio completo.\n2. Ejecuta `python powerbi/configure_data.py`. Alternativamente, en Transformar datos → Administrar parámetros cambia `DataFolder` a la carpeta `powerbi/data/` con separador final.\n3. Abre `powerbi/Analytics.pbip` en Power BI Desktop y pulsa Actualizar.\n\n## Estructura y correspondencia\n\n'+parity+'\n\nLas páginas conservan el análisis del proyecto original. Los controles de entrenamiento, conexión, escritura SQL e inferencia en vivo siguen en Python/Streamlit. El informe consume resultados exportados; no reemplaza esos servicios. Los CSV conservan su grano, y las medidas evitan sumar porcentajes o promedios.\n'
  (self.root/'README.md').write_text(readme,encoding='utf-8')
  summary={'repo':self.repo,'pages':len(self.pages),'visuals':len(list((self.root/'Analytics.Report/definition/pages').rglob('visual.json'))),'tables':{t:len(d) for t,d in self.tables.items()},'status':self.status}
  write(self.root/'validation.json',summary);return summary

def metrics(t,names):return {f'KPI_{n}':(e,'#,0.00') for n,e in names}
