from pathlib import Path
import json,math,csv
import numpy as np
import cadquery as cq
import matplotlib;matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.backends.backend_pdf import PdfPages
from mpl_toolkits.mplot3d.art3d import Poly3DCollection
import ezdxf
R=Path(__file__).resolve().parent;p=json.loads((R/'parameters.json').read_text());ms=json.loads((R/'model_manifest.json').read_text())
env=dict(p,pi=math.pi,sqrt=math.sqrt,cos=math.cos,sin=math.sin,abs=abs,min=min,max=max)
def V(s):return float(eval(str(s),{'__builtins__':{}},env))
sh=cq.importers.importStep(str(R/'cad/Module_assembly.step')).solids().vals();assert len(sh)==len(ms),(len(sh),len(ms))
colors={'frame':'#357fa4','steel':'#a0a8ae','fabricated':'#d38b28','roller':'#27876a','rubber':'#25282c','bolt':'#555b61','rail':'#8b9094','motor':'#353b42'}
# Tessellate actual exported geometry. Not an AI-generated rendering.
cache=[]
for m,s in zip(ms,sh):
 verts,faces=s.tessellate(1.5,0.35);vv=np.array([[v.x,v.y,v.z] for v in verts]);ff=np.array(faces,dtype=int)
 if len(ff):cache.append((m,vv[ff]))

def scene(name,elev,azim,exploded=False,rail=True):
 fig=plt.figure(figsize=(11.7,8.3));ax=fig.add_subplot(111,projection='3d')
 for m,polys in cache:
  if m['group']=='rail' and not rail:continue
  if m['group']=='bolt' or m['name'].startswith('W_'):continue
  pp=polys+np.array(m['explode']) if exploded else polys
  collection=Poly3DCollection(pp,facecolors=colors[m['group']],edgecolors='none',linewidths=0,rasterized=True)
  ax.add_collection3d(collection)
 ax.set_xlim(-450 if rail else -390,450 if rail else 390);ax.set_ylim(-300 if exploded else -190,300 if exploded else 190);ax.set_zlim(-180 if rail else -100,640 if exploded else 510)
 ax.set_box_aspect((900 if rail else 780,600 if exploded else 380,820 if exploded else 690));ax.view_init(elev=elev,azim=azim);ax.set_proj_type('ortho');ax.set_xlabel('X travel [mm]');ax.set_ylabel('Y transverse [mm]');ax.set_zlabel('Z vertical [mm]')
 fig.suptitle(name+' | QS212 straight rail module R01',fontsize=14)
 fig.text(.02,.02,'DRAFT - NOT FOR FABRICATION RELEASE / Rail60K envelope, site unconfirmed / Tire assumed406.4 x76.2mm',fontsize=9)
 fig.savefig(R/'drawings'/(name+'.png'),dpi=155,bbox_inches='tight');return fig
with PdfPages(R/'drawings/Assembly_views.pdf') as pdf:
 for args in [('01_Isometric',24,-50,False,True),('02_Front_YZ',0,0,False,True),('03_Side_XZ',0,-90,False,True),('04_Top_XY',90,-90,False,True),('05_Exploded',22,-50,True,False)]:
  fig=scene(*args);pdf.savefig(fig);plt.close(fig)
# Clear, dimensioned 2D orthographic layout (selected envelopes, no hidden fastener clutter).
from matplotlib.patches import Rectangle,Circle,Polygon,Arc
Rwheel=p['tire_od']/2;Ycol=p['frame_half_y'];station=p['roller_station'];gap=p['guide_gap'];rr=p['roller_d']/2
slope=p['rail_side_slope'];c=p['roller_crown'];bw=p['roller_width'];zc=p['roller_center_z'];dz=-slope*bw*bw/(8*c);zcnt=zc+dz
rail_at=lambda z:p['rail_head_width']/2-slope*(z+p['rail_side_ref_depth'])
yguide=p['rail_head_width']/2+rr+gap-slope*(zc+p['rail_side_ref_depth'])+slope*slope*bw*bw/(16*c)
def dim(ax,a,b,label,off=(0,0)):
 a=np.array(a)+off;b=np.array(b)+off;ax.annotate('',xy=b,xytext=a,arrowprops=dict(arrowstyle='<->',lw=.8,color='#333'))
 mid=(a+b)/2;ax.text(*mid,label,fontsize=9,ha='center',va='bottom',bbox=dict(facecolor='white',edgecolor='none',pad=1))
with PdfPages(R/'drawings/Dimensioned_layout.pdf') as pdf:
 fig,axs=plt.subplots(1,3,figsize=(16.5,8.3))
 a=axs[0];a.set_title('Front / YZ (X=0 and guide station overlay)')
 a.add_patch(Rectangle((-p['tire_width']/2,0),p['tire_width'],p['tire_od'],fill=False,lw=1.8));a.add_patch(Rectangle((-135,Rwheel-8),270,16,fill=False))
 for sy in [-1,1]:
  a.add_patch(Rectangle((sy*Ycol-20,-52),40,482,color=colors['frame'],alpha=.5));a.add_patch(Rectangle((sy*yguide-rr,-34),2*rr,28,fill=False,edgecolor=colors['roller'],lw=2))
 a.add_patch(Rectangle((-154,430),308,40,fill=False));dim(a,(-135,405),(135,405),'axle270');dim(a,(-100.25,135),(100.25,135),'plate outer200.5')
 a.set_xlim(-210,210);a.set_ylim(-180,500)
 a=axs[1];a.set_title('Side / XZ')
 a.add_patch(Circle((0,Rwheel),Rwheel,fill=False,lw=1.8));a.add_patch(Rectangle((-290,430),580,40,fill=False,edgecolor=colors['frame'],lw=2))
 for x in [-station,station]:a.add_patch(Rectangle((x-20,-52),40,482,color=colors['frame'],alpha=.3));a.add_patch(Rectangle((x-25,-34),50,28,color=colors['roller'],alpha=.6))
 for x in [-85,85]:a.add_patch(Rectangle((x-20,p['brace_beam_z']),40,430-p['brace_beam_z'],fill=False,edgecolor=colors['frame']))
 
 for sx in [-1,1]:a.add_patch(Rectangle((105 if sx>0 else -200,p['brace_beam_z']),95,40,fill=False,edgecolor=colors['frame'],lw=2))
 dim(a,(-station,40),(station,40),'guide pitch440');dim(a,(-290,495),(290,495),'frame580');a.set_xlim(-340,340);a.set_ylim(-180,530)
 a=axs[2];a.set_title('Top / XY')
 a.add_patch(Rectangle((-Rwheel,-p['tire_width']/2),2*Rwheel,p['tire_width'],fill=False,lw=1.8))
 for sy in [-1,1]:
  a.add_patch(Rectangle((-290,sy*Ycol-20),580,40,fill=False,edgecolor=colors['frame'],lw=2))
  for x in [-station,station]:a.add_patch(Circle((x,sy*yguide),rr,fill=False,edgecolor=colors['roller'],lw=2))
 a.add_patch(Rectangle((-450,-32.5),900,65,fill=False,edgecolor='grey'));dim(a,(-station,-190),(station,-190),'front/rear440');a.set_xlim(-450,450);a.set_ylim(-220,220)
 for a in axs:a.set_aspect('equal');a.grid(alpha=.15);a.set_xlabel('mm')
 fig.suptitle('DIMENSIONED LAYOUT / all interface values provisional except cited rail nominal sizes');fig.tight_layout();pdf.savefig(fig);fig.savefig(R/'drawings/06_Dimensioned_layout.png',dpi=160);plt.close(fig)
# Contact section: crown + tapered60K head, nominal gap and touching state.
fig,(ax,ap)=plt.subplots(1,2,figsize=(11.7,8.3))
zz=np.linspace(-34,-6,181);rad=rr-c*((zz-zc)/(bw/2))**2
railpts=[[V(a),V(b)] for a,b in ms[0]['adds'][0]['points']]
ax.add_patch(Polygon(railpts,color=colors['rail'],alpha=.45))
for sy in [-1,1]:
 ax.fill_betweenx(zz,sy*yguide-rad,sy*yguide+rad,color=colors['roller'],alpha=.22)
 ax.plot(sy*(yguide-rad),zz,color=colors['roller'],lw=1.5)
 ax.plot(sy*(yguide-gap-rad),zz,'--',color='#aa4d22',lw=1.2)
 ax.plot([sy*yguide]*2,[-45,15],':',color='grey')
 ax.scatter([sy*rail_at(zcnt)],[zcnt],color='red',s=18)
ax.annotate('Nominal gap1.0mm\nOne-sided contact after1.0mm shift',xy=(rail_at(zcnt)+.5,zcnt),xytext=(3,12),arrowprops=dict(arrowstyle='->'),fontsize=10)
ax.set_xlim(-100,100);ax.set_ylim(-60,30);ax.set_aspect('equal');ax.set_title('Guide section at X=+/-220 / YZ');ax.set_xlabel('Y mm');ax.set_ylabel('Z mm');ax.grid(alpha=.15)
# Tight contact enlargement on right side, enough to show1mm physically.
ax2=ap
ax2.plot([rail_at(z) for z in zz],zz,lw=2,color=colors['rail'],label='60K side1:40')
ax2.plot(yguide-rad,zz,lw=2,color=colors['roller'],label='Unloaded crowned roller')
ax2.plot(yguide-gap-rad,zz,'--',color='#aa4d22',label='Shifted1mm: touching')
ax2.scatter([rail_at(zcnt)],[zcnt],color='red');dim(ax2,(rail_at(zcnt),zcnt),(rail_at(zcnt)+gap,zcnt),'1.0')
ax2.set_xlim(30.5,34);ax2.set_ylim(-33,-9);ax2.set_title('Right-side contact magnified\nwidth axis enlarged independently');ax2.set_xlabel('Y mm');ax2.set_ylabel('Z mm');ax2.grid(alpha=.2);ax2.legend(fontsize=8)
fig.suptitle('SIDE GUIDANCE ONLY - NO VERTICAL ANTI-LIFT RESTRAINT');fig.text(.03,.03,'Contact height approximately Z=-24.9mm. Real PU deflection, rail wear and exact radii must be checked.',fontsize=9)
fig.savefig(R/'drawings/07_Contact_detail.png',dpi=180,bbox_inches='tight');fig.savefig(R/'drawings/Contact_detail.pdf',bbox_inches='tight');plt.close(fig)
# Machining draft 2D outlines from exact model manifest, local plane coordinates; DXF mm.
selected=['A01_Axle_plate_1','A02_Torque_keeper_1','G07_Lower_yoke_weldment_1_1','G08_Removable_top_arm_1_1','G09_Sliding_clamp_1_1_1','F05_Top_splice_1_1']
with PdfPages(R/'drawings/Machining_drafts.pdf') as pdf:
 for name in selected:
  m=next(m for m in ms if m['name']==name)
  plane='XZ' if name.startswith(('A01','A02','G07')) else 'XY'
  # G07 is side wall view. Horizontal lower arm is separate weldment detail noted.
  fig,ax=plt.subplots(figsize=(11.7,8.3));doc=ezdxf.new('R2010');doc.units=4;space=doc.modelspace()
  for cut,ops in [(False,m['adds']),(True,m['cuts'])]:
   for op in ops:
    if op['plane']!=plane:continue
    color='#bc4228' if cut else '#222'
    if op['profile']=='poly':
     pts=[(V(a),V(b)) for a,b in op['points']];ax.add_patch(Polygon(pts,fill=False,edgecolor=color,lw=1.1));space.add_lwpolyline(pts,close=True,dxfattribs={'layer':'CUT' if cut else 'OUTLINE'})
    elif op['profile']=='circle':
     u,v=map(V,op['center']);r=V(op['radius']);ax.add_patch(Circle((u,v),r,fill=False,edgecolor=color));space.add_circle((u,v),r,dxfattribs={'layer':'HOLES'})
     ax.text(u+r+1,v,f'D{2*r:g}',fontsize=7)
    elif op['profile']=='slot':
     u,v=map(V,op['center']);w=V(op['width']);t=V(op['travel']);rrr=w/2
     pts=[]
     for a in np.linspace(0,math.pi,25):pts.append((u+rrr*math.cos(a),v+t/2+rrr*math.sin(a)))
     for a in np.linspace(math.pi,2*math.pi,25):pts.append((u+rrr*math.cos(a),v-t/2+rrr*math.sin(a)))
     ax.add_patch(Polygon(pts,fill=False,edgecolor=color));space.add_lwpolyline(pts,close=True,dxfattribs={'layer':'SLOTS'});ax.text(u+w,v,f'{w:g} x {w+t:g} slot Y',fontsize=8)
  ax.autoscale();ax.margins(.22);ax.set_aspect('equal');ax.grid(alpha=.2);ax.set_xlabel('local u / mm');ax.set_ylabel('local v / mm')
  fig.suptitle(name+' / '+plane+' / DRAFT - NOT RELEASED')
  fig.text(.05,.05,m['note'],fontsize=9,wrap=True);fig.text(.05,.025,'Coordinates are assembly datum mm. Thread holes shown at tap-drill diameter. Final fits/tolerances/weld details require review.',fontsize=8)
  pdf.savefig(fig);fig.savefig(R/'drawings'/(name+'.png'),dpi=150,bbox_inches='tight');plt.close(fig)
  space.add_text(name+' DRAFT NOT FOR RELEASE',dxfattribs={'height':4,'insert':(0,-80)})
  doc.saveas(R/'drawings'/(name+'.dxf'))
# Exact coordinates and hole types, not only pictures.
with (R/'drawings/Machining_coordinates.csv').open('w',newline='') as f:
 w=csv.writer(f);w.writerow(['part','feature','plane','u_mm','v_mm','diameter_mm','slot_total_length_mm','note'])
 for m in ms:
  if not m['name'].startswith(('A01','A02','G02','G07','G08','G09','F05')):continue
  for i,o in enumerate(m['cuts']):
   if o['profile']=='circle':w.writerow([m['name'],i,o['plane'],V(o['center'][0]),V(o['center'][1]),2*V(o['radius']),'','tap or clearance: see note'])
   elif o['profile']=='slot':w.writerow([m['name'],i,o['plane'],V(o['center'][0]),V(o['center'][1]),V(o['width']),V(o['width'])+V(o['travel']),'slot along local V'])
# Geometric mass envelope: actual extrusion supplier mass, real motor catalogue mass separate.
length=2*.580+4*(430-p['brace_beam_z'])/1000+4*.482+2*.228+4*.095
mass_profile=length*1.73
mass_custom=0
for m,s in zip(ms,sh):
 if m['category'].startswith('custom'):
  dens=.0000027 if ('6061' in m['material'] or m['name'].startswith('G02')) else (.0000012 if m['group']=='roller' else .00000785)
  mass_custom+=s.Volume()*dens
mass={'profile_length_m':round(length,3),'profile_catalogue_density_kg_m_assumed':1.73,'profile_mass_kg':round(mass_profile,2),'custom_parts_volume_mass_kg':round(mass_custom,2),'motor_mass_kg_from_user_spec':13.21,'tire_mass_kg_assumed':2.5,'bearings_fasteners_allowance_kg':2.5}
mass['module_estimate_kg']=round(mass_profile+mass_custom+13.21+2.5+2.5,2)
mass['four_modules_estimate_kg']=round(mass['module_estimate_kg']*4,2)
mass['remaining_of_200kg_before_chassis_battery_people']=round(200-mass['four_modules_estimate_kg'],2)
(R/'reports/Mass_budget.json').write_text(json.dumps(mass,indent=2))
print('Drawings, mesh renders, PDF, DXF and mass budget complete.',mass)
