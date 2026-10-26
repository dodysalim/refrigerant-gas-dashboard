from pathlib import Path
import json,copy
W,H=1123,794
MS='https://developer.microsoft.com/json-schemas/fabric/item/report/definition/visualContainerMobileState/2.4.0/schema.json'
def write(p,d):p.write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
def apply(root):
 changed=[]
 for pf in (root/'Analytics.Report/definition/pages').glob('*/page.json'):
  page=json.loads(pf.read_text());ow,oh=page['width'],page['height'];page.update(width=W,height=H,displayOption='ActualSize');write(pf,page);changed.append(pf)
  visuals=[]
  for f in (pf.parent/'visuals').glob('*/visual.json'):
   v=json.loads(f.read_text());p=v['position'];typ=v['visual']['visualType'];name=v['name'];o=v['visual'].setdefault('objects',{})
   if (ow,oh)!=(W,H):
    p.update(x=round(p['x']*W/ow),width=round(p['width']*W/ow),y=round(p['y']*H/oh),height=round(p['height']*H/oh))
   if typ=='card':
    o['labels'][0]['properties']['fontSize']['expr']['Literal']['Value']='16D' if pf.parent.name=='ciclo' else '21D'
   if typ=='textbox':
    for para in o.get('general',[{}])[0].get('properties',{}).get('paragraphs',[]):
     for run in para.get('textRuns',[]):run['textStyle']['fontSize']='17pt' if name=='header' else '9pt'
   assert p['x']>=0 and p['y']>=0 and p['x']+p['width']<=W and p['y']+p['height']<=H,(f,p)
   write(f,v);changed.append(f);visuals.append((f,v))
  ordered=sorted(visuals,key=lambda fv:(0 if fv[1]['name']=='header' else 4 if fv[1]['name']=='footer' else 1 if fv[1]['visual']['visualType']=='slicer' else 2 if fv[1]['visual']['visualType']=='card' else 3,fv[1]['position']['y'],fv[1]['position']['x']))
  y=0
  for i,(f,v) in enumerate(ordered):
   typ=v['visual']['visualType'];name=v['name'];height=100 if typ=='card' else 76 if typ=='slicer' else 360 if typ=='tableEx' else 320
   if typ=='textbox':height=110 if name=='header' else 140
   mobile={'$schema':MS,'position':{'x':0,'y':y,'z':i,'width':323,'height':height,'tabOrder':i}}
   if typ=='textbox':
    mobile['objects']=copy.deepcopy(v['visual']['objects'])
    for para in mobile['objects'].get('general',[{}])[0].get('properties',{}).get('paragraphs',[]):
     for run in para.get('textRuns',[]):run['textStyle']['fontSize']='16pt' if name=='header' else '10pt'
   if typ=='card':
    mobile['objects']={'labels':copy.deepcopy(v['visual']['objects']['labels'])};mobile['objects']['labels'][0]['properties']['fontSize']['expr']['Literal']['Value']='22D'
   write(f.parent/'mobile.json',mobile);changed.append(f.parent/'mobile.json');y+=height+10
  assert y<10000,(pf,y)
  for i,(_,a) in enumerate(visuals):
   for _,b in visuals[i+1:]:
    p,q=a['position'],b['position'];assert not (p['x']<q['x']+q['width'] and q['x']<p['x']+p['width'] and p['y']<q['y']+q['height'] and q['y']<p['y']+p['height']),(pf,a['name'],b['name'])
 return changed
if __name__=='__main__':
 apply(Path(__file__).resolve().parent)
 print('A4 1123 x 794, 100%, mobile layout regenerated.')
