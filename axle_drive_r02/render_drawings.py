from pathlib import Path
import json,math,numpy as np
import matplotlib;matplotlib.use('Agg')
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d.art3d import Poly3DCollection
from matplotlib.backends.backend_pdf import PdfPages
R=Path(__file__).resolve().parent;p=json.loads((R/'parameters.json').read_text());meshes=json.loads((R/'render_mesh.json').read_text());poses=json.loads((R/'poses.json').read_text())
colors={'frame':'#357fa4','wheel':'#454c52','shaft':'#a5abb1','guide':'#27876a','plate':'#d38b28','motor':'#25292c','chain':'#6b6c6d','joint':'#c24b28'}
def rot(v,axis,angle,center):
 t=math.radians(angle);c=math.cos(t);s=math.sin(t)
 m={'X':[[1,0,0],[0,c,-s],[0,s,c]],'Y':[[c,0,s],[0,1,0],[-s,0,c]],'Z':[[c,-s,0],[s,c,0],[0,0,1]]}[axis];return (v-np.array(center))@np.array(m).T+np.array(center)
def verts(d,pose):
 v=np.array(d['vertices']);b=d['bogie'];stage=d['stage']
 if b:
  if stage=='bogie':v=rot(v,'Z',pose.get(b+'_yaw',0),(0,0,p['yaw_z']))
  if stage in ['bogie','yaw_carrier']:v=rot(v,'Y',pose.get(b+'_pitch',0),(0,0,p['pitch_z']))
  if b=='front' and stage in ['bogie','yaw_carrier','roll_carrier']:v=rot(v,'X',pose.get('front_roll',0),(0,0,p['roll_z']))
  v+=np.array([-p['wheelbase']/2 if b=='rear' else p['wheelbase']/2,0,0])
 return v
views=[('01_Assembly','Straight',23,-55,None),('02_Top','Straight',90,-90,None),('03_Side_drive','Straight',0,-90,None),('04_Curve_R50','Curve_R50',90,-90,None),('05_Pitch_roll_DEMO','Articulation_DEMO',18,-55,None),('06_Drive_close','Straight',15,-70,'drive'),('07_Joints_close','Straight',15,-55,'joint')]
with PdfPages(R/'drawings/Assembly_and_joint_views.pdf') as pdf:
 for name,pose,elev,az,zoom in views:
  fig=plt.figure(figsize=(12,8));ax=fig.add_subplot(projection='3d')
  for d in meshes:
   if zoom and d['bogie']=='front':continue
   if zoom=='drive' and not (d['group'] in ['motor','chain'] or 'JACKSHAFT' in d['name'] or 'JACK_BEARING' in d['name'] or 'LIVE_AXLE' in d['name'] or 'OUTPUT_SHAFT' in d['name']):continue
   if zoom=='joint' and not any(t in d['name'] for t in ['YAW_','PITCH_','ROLL_']):continue
   vv=verts(d,poses[pose]);polys=vv[np.array(d['faces'],dtype=int)]
   if len(polys)>2500:polys=polys[::max(1,len(polys)//2500)]
   ax.add_collection3d(Poly3DCollection(polys,facecolors=colors[d['group']],edgecolors='none',rasterized=True))
  if zoom=='drive':lims=((-700,180),(-100,550),(0,430))
  elif zoom=='joint':lims=((-700,-300),(-240,240),(350,700))
  else:lims=((-1100,1150),(-1050,1050),(-100,760))
  ax.set_xlim(*lims[0]);ax.set_ylim(*lims[1]);ax.set_zlim(*lims[2]);ax.set_box_aspect(tuple(b-a for a,b in lims));ax.view_init(elev,az);ax.set_proj_type('ortho');ax.set_xlabel('X mm');ax.set_ylabel('Y mm');ax.set_zlabel('Z mm');fig.suptitle(name+' / AXLE DRIVE R02'+(' / SELECTED PARTS ONLY' if zoom else ''));fig.text(.03,.02,'DRAFT: chain, bearing and motor interfaces simplified. Posed joints are NOT track-contact/dynamic validation.',fontsize=9);pdf.savefig(fig);fig.savefig(R/'drawings'/(name+'.png'),dpi=140);plt.close(fig);print(name,flush=True)
