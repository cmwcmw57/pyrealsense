from pathlib import Path
import sys,json,csv
sys.path.append('/usr/lib/freecad/lib')
import FreeCAD,Part
R=Path(__file__).resolve().parent;names=[r['name'] for r in csv.DictReader((R/'BOM_parts.csv').open())];results=[];collisions=[]
for file in sorted((R/'cad').glob('AxleDrive_*.step')):
 s=Part.read(str(file));ss=s.Solids;assert s.isValid();assert len(ss)==len(names),(len(ss),len(names));d=dict(zip(names,ss));nchecks=0
 pairs=[]
 for n in names:
  if '_RAILWHEEL_' in n:
   b,sy=n.split('_RAILWHEEL_')
   for other in names:
    if other.startswith(f'{b}_GUIDE_{sy}_'):pairs.append((n,other))
 for prefix in ['rear','front']:
  for suf in ['-1','1']:pairs.append((prefix+'_PITCH_INNER_LUG',prefix+'_PITCH_FORK_'+suf))
  pairs.append((prefix+'_PITCH_INNER_LUG',prefix+'_PITCH_FORK_TOP'))
 for chain in ['CHAIN_STAGE1_70LINK_ENVELOPE','CHAIN_STAGE2_70LINK_ENVELOPE']:
  for n in names:
   if n.startswith(('MOTOR_SUPPORT','JACK_DROP_SUPPORT','rear_LONG_TUBE','rear_CROSS_TUBE')) or n=='QS120_70H_72V_2KW_ENVELOPE':pairs.append((chain,n))
 for a,b in pairs:
  nchecks+=1;sa,sb=d[a],d[b];ba,bb=sa.BoundBox,sb.BoundBox
  if ba.XMax<bb.XMin or bb.XMax<ba.XMin or ba.YMax<bb.YMin or bb.YMax<ba.YMin or ba.ZMax<bb.ZMin or bb.ZMax<ba.ZMin:continue
  vol=sa.common(sb).Volume
  if vol>1e-4:collisions.append({'pose':file.name,'a':a,'b':b,'overlap_mm3':round(vol,5)})
 results.append({'file':file.name,'FreeCAD_version':'.'.join(FreeCAD.Version()[:3]),'valid':s.isValid(),'solids':len(ss),'selected_pair_checks':nchecks,'note':'Reference-envelope pair checks only; no rail or full bolt/tolerance/dynamic analysis'})
(R/'reports/Reopen_and_selected_clearance.json').write_text(json.dumps({'files':results,'overlaps':collisions},indent=2));print(json.dumps({'files':results,'overlaps':collisions},indent=2))
