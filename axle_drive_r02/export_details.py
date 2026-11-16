from pathlib import Path
import cadquery as cq,csv
r=Path(__file__).resolve().parent;ns=[a['name'] for a in csv.DictReader((r/'BOM_parts.csv').open())];ss=cq.importers.importStep(str(r/'cad/AxleDrive_Straight.step')).solids().vals();assert len(ss)==len(ns)
for label,select in [('Joint_mechanisms',lambda n:any(t in n for t in ['YAW_','PITCH_','ROLL_'])),('Drive_train',lambda n:n.startswith(('MOTOR_','QS120_','JACK_','JACKSHAFT_','AXLE_428','CHAIN_')) or n=='rear_LIVE_AXLE_KEYSEATS_D40')]:
 a=cq.Assembly(name=label)
 for n,s in zip(ns,ss):
  if select(n):a.add(s,name=n)
 a.save(str(r/'cad'/(label+'.step')));print(label,flush=True)
