from pathlib import Path
import cadquery as cq,numpy as np,json,math,csv
import matplotlib;matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.backends.backend_pdf import PdfPages
R=Path(__file__).resolve().parent;src=R/'module_source';src=src if src.exists() else Path('/workspace/work/qs212_module_design')
p={'wheelbase_mm':1000,'rail_center_spacing_mm':1500,'gauge_reference_mm':1435,'head_width_mm':65,'frame_width_mm':1808,'frame_length_mm':1700,'frame_bottom_z_mm':490,'frame_section_mm':40,'module_mount_top_z_mm':470,'guide_half_pitch_mm':220,'guide_gap_mm':1,'tire_radius_mm':203.2,'mass_for_traction_kg':200,'speed_kmh':20,'rolling_resistance_assumed':0.02,'rear_normal_fraction_assumed':0.5}
f=R/'chassis_parameters.json'
if not f.exists():f.write_text(json.dumps(p,indent=2))
p=json.loads(f.read_text());L=p['wheelbase_mm'];G=p['rail_center_spacing_mm'];ms=json.loads((src/'model_manifest.json').read_text());sol=cq.importers.importStep(str(src/'cad/Module_assembly.step')).solids().vals();assert len(ms)==len(sol)
assy=cq.Assembly(name='Four_wheel_RIGID_chassis_DRAFT');render=[];checks=[]
colors={'frame':(.2,.5,.68),'fabricated':(.84,.56,.15),'roller':(.1,.52,.35),'rubber':(.08,.09,.1),'steel':(.6,.63,.65),'motor':(.2,.24,.28)}
def add(name,s,color):
 assert s.isValid();assy.add(s,name=name,color=cq.Color(*color));vs,fs=s.tessellate(3,.45);v=np.array([[a.x,a.y,a.z] for a in vs]);render.append((name,v[np.array(fs)],color))
for ix,x in enumerate([-L/2,L/2]):
 for iy,y in enumerate([-G/2,G/2]):
  for m,s in zip(ms,sol):
   if m['group'] in ['rail','bolt'] or m['name'].startswith('W_'):continue
   if ix==1 and m['name'].startswith('M02'):continue
   name=f'{"FRONT_PASSIVE" if ix else "REAR_DRIVE"}_{iy}_{m["name"]}'
   add(name,s.translate((x,y,0)),colors.get(m['group'],(.6,.6,.6)))
  if ix==1:
   # Packaging placeholder only: generic hub OD100, width70; bearing/axle interface not selected.
   hub=cq.Workplane('XZ',origin=(x,y+35,203.2)).circle(50).circle(9).extrude(70).val()
   add(f'FRONT_{iy}_PASSIVE_HUB_INTERFACE_UNRESOLVED',hub,(.7,.72,.75))
def box(name,x,y,z,a,b,c,color=(.2,.5,.68)):
 s=cq.Workplane('XY').box(a,b,c).translate((x,y,z+c/2)).val();add(name,s,color);return s
# Rail cross section inherited from source, extruded along X through chassis.
railenv=dict(json.loads((src/'parameters.json').read_text()),sqrt=math.sqrt,pi=math.pi);railop=ms[0]['adds'][0];pts=[(float(eval(a,{},railenv)),float(eval(b,{},railenv))) for a,b in railop['points']]
for sy in [-1,1]:
 rail=cq.Workplane('YZ',origin=(-1100,sy*G/2,0)).polyline(pts).close().extrude(2200).val();add(f'RAIL_{sy}_60K_REFERENCE',rail,(.6,.62,.64))
# Main rectangular frame, 40x40 hollow envelope. Slot supplier CAD belongs to detailed design.
def beam(name,x,y,z,a,b,c):
 s=cq.Workplane('XY').box(a,b,c).translate((x,y,z+c/2)).val()
 if a>b:s=s.cut(cq.Workplane('XY').box(a+2,b-6,c-6).translate((x,y,z+c/2)).val())
 else:s=s.cut(cq.Workplane('XY').box(a-6,b+2,c-6).translate((x,y,z+c/2)).val())
 add(name,s,(.2,.5,.68))
for y in [-884,884]:beam(f'CHASSIS_LONG_{y}',0,y,490,1700,40,40)
for x in [-830,0,830]:beam(f'CHASSIS_CROSS_{x}',x,0,490,40,1728,40)
# Each module top gets two bridging channels/plates, four M8 access holes per plate.
for x in [-L/2,L/2]:
 for y in [-G/2,G/2]:
  for dx in [-220,220]:
   plate=cq.Workplane('XY').box(80,348,10).translate((x+dx,y,480+5)).val()
   for dy in [-134,134]:
    for hx in [-20,20]:plate=plate.cut(cq.Workplane('XY').center(x+dx+hx,y+dy).circle(4.5).extrude(600).val())
   add(f'MOUNT_PLATE_{x}_{y}_{dx}',plate,(.85,.58,.2))
   for dy in [-134,134]:box(f'SPACER_{x}_{y}_{dx}_{dy}',x+dx,y+dy,470,80,40,10,(.7,.7,.72))
# transverse cross ties at module positions join chassis long members and mounting plates, at z490.
for x in [-L/2-220,-L/2+220,L/2-220,L/2+220]:beam(f'MOUNT_CROSS_{x}',x,0,490,40,1728,40)
assy.save(str(R/'Chassis_Rigid_4Wheel.step'))
(R/'CAD_status.json').write_text(json.dumps({'shape_valid_all':True,'exported_parts':len(render),'front_passive_hub':'packaging placeholder; bearings/axle adapter NOT designed','frame_mount':'M8 hole layout draft; T-nuts/angles/spacer holes and strength NOT released','all_pair_interference':'NOT performed','rail_center_spacing':'1500 provisional; not derived as exact measured gauge conversion'},indent=2))
from mpl_toolkits.mplot3d.art3d import Poly3DCollection
with PdfPages(R/'Chassis_views.pdf') as pdf:
 for title,elev,az in [('Isometric',25,-55),('Top',90,-90),('Side',0,-90),('Front',0,0)]:
  fig=plt.figure(figsize=(12,8));ax=fig.add_subplot(projection='3d')
  for n,v,c in render:ax.add_collection3d(Poly3DCollection(v,facecolors=c,edgecolors='none',rasterized=True))
  ax.set_xlim(-1150,1150);ax.set_ylim(-1050,1050);ax.set_zlim(-180,650);ax.set_box_aspect((2300,2100,830));ax.view_init(elev,az);ax.set_proj_type('ortho');ax.set_xlabel('X mm');ax.set_ylabel('Y mm');ax.set_zlabel('Z mm');fig.suptitle(title+' / RIGID FOUR-WHEEL PACKAGING DRAFT');fig.text(.05,.02,'Rear2 drive / Front2 passive hub placeholder. No suspension or steering. Not fabrication release.');pdf.savefig(fig);fig.savefig(R/(title+'.png'),dpi=130);plt.close(fig)
print('CAD generated',len(render),flush=True)
