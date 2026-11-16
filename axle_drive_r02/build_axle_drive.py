"""Axle-drive articulated rail vehicle R02. mm. Parametric CadQuery source.
Motor, bearing and sprocket supplier interfaces marked provisional. No dynamics claim.
"""
from pathlib import Path
import cadquery as cq,math,json,csv
R=Path(__file__).resolve().parent
for d in ['cad','parts','drawings','reports']:(R/d).mkdir(exist_ok=True)
P={'wheelbase':1000,'rail_centers':1500,'wheel_d':300,'wheel_width':90,'wheel_taper':0.05,'flange_d':330,'flange_t':8,'axle_d':40,'axle_length':1800,'bearing_y':620,'guide_station':150,'guide_center_offset':58.06125,'guide_gap':1,'yaw_z':400,'pitch_z':490,'roll_z':575,'frame_z':620,'chain_pitch':12.7,'stage1_small':14,'stage1_large':42,'stage1_links':70,'stage2_small':16,'stage2_large':40,'stage2_links':70,'motor_d':170,'motor_length':160,'motor_shaft_d':20,'motor_voltage':72,'motor_power':2000,'total_mass_for_force':200,'design_speed_kmh':20,'screen_grade_permille':35,'assumed_Crr':0.02,'chain_efficiency_each':0.95,'curve_pose_radius_m':50,'front_roll_pose_deg':2,'front_pitch_pose_deg':1,'rear_pitch_pose_deg':-1}
f=R/'parameters.json'
if not f.exists():f.write_text(json.dumps(P,indent=2))
p=json.loads(f.read_text());L=p['wheelbase'];G=p['rail_centers'];wr=p['wheel_d']/2;parts=[];byname={}
C={"frame":(.2,.5,.7),"wheel":(.3,.33,.36),"shaft":(.6,.63,.67),"guide":(.1,.55,.36),"plate":(.87,.58,.17),"motor":(.15,.17,.2),"chain":(.45,.45,.47),"joint":(.75,.25,.15)}
def add(name,s,group='frame',bogie=None,stage='bogie',note='',mat='steel',qtytype='custom'):
 s=s.clean();assert s.isValid(),name;assert len(s.Solids())==1,(name,len(s.Solids()))
 d=dict(name=name,shape=s,group=group,bogie=bogie,stage=stage,note=note,material=mat,type=qtytype);parts.append(d);byname[name]=s;return s
def box(x,y,z,l,w,h):return cq.Workplane().box(l,w,h).translate((x,y,z+h/2)).val()
def cy(x,y,z,r,length,axis='Y',ri=0):
 plane={'Y':'XZ','X':'YZ','Z':'XY'}[axis];origin=(x,y+length/2,z) if axis=='Y' else ((x-length/2,y,z) if axis=='X' else (x,y,z-length/2));w=cq.Workplane(plane,origin=origin).circle(r)
 if ri:w=w.circle(ri)
 return w.extrude(length).val()
def tube(x,y,z,l,w,h):
 s=box(x,y,z,l,w,h)
 if l>w:return s.cut(box(x,y,z+3,l+2,w-6,h-6))
 return s.cut(box(x,y,z+3,l-6,w+2,h-6))
def plate_holes(x,y,z,l,w,h,holes):
 s=box(x,y,z,l,w,h)
 for hx,hy,d in holes:s=s.cut(cy(hx,hy,z+h/2,d/2,h+2,'Z'))
 return s
def center_distance(n,N,links):
 b=(N-n)**2/(4*math.pi**2);A=links-(n+N)/2;return p['chain_pitch']*(A+math.sqrt(A*A-8*b))/4
c1=center_distance(p['stage1_small'],p['stage1_large'],p['stage1_links']);c2=center_distance(p['stage2_small'],p['stage2_large'],p['stage2_links']);mx=c1+c2
# All local bogie coordinates have wheel axle at X0,Z150. Rear globalX=-L/2.
for b in ['rear','front']:
 # Common live axle on both bogies; no left/right differential.
 axle=cy(0,0,wr,p['axle_d']/2,p['axle_length'])
 for yy in [-G/2,G/2]:axle=axle.cut(box(0,yy,wr+16,12,80,8))
 if b=='rear':axle=axle.cut(box(0,0,wr+16,12,60,8))
 add(b+'_LIVE_AXLE_KEYSEATS_D40',axle,'shaft',b,note='C45 ground bearing seats. Key12x8 candidate. Shoulders, fits, fatigue and axial retention pending.')
 for sy in [-1,1]:
  y=sy*G/2
  # Simplified conical tread: larger rolling radius inboard. No standard flange profile claimed.
  # Workplane XY revolved around local Y; points are radial X, axial Y.
  pts=[(20,-45),(wr+sy*(-45)*p['wheel_taper'],-45),(wr+sy*45*p['wheel_taper'],45),(20,45)]
  # radius decreases outboard: use negative slope for +Y wheel.
  pts=[(20,-45),(wr-sy*(-45)*p['wheel_taper'],-45),(wr-sy*45*p['wheel_taper'],45),(20,45)]
  wh=cq.Workplane('XY',origin=(0,y,wr)).polyline(pts).close().revolve(360,(0,-1),(0,1)).val()
  fy=y-sy*(45+p['flange_t']/2);fl=cy(0,fy,wr,p['flange_d']/2,p['flange_t'],ri=20)
  # taper radius at inboard end below flange; union joins at boundary.
  wh=wh.fuse(fl);wh=wh.cut(box(0,y,wr+16,12,110,8))
  add(f'{b}_RAILWHEEL_{sy}',wh,'wheel',b,note='Custom wheel blank envelope; 1:20 taper provisional, flange root/angle NOT standard restored. Bore40 key12x8.')
  add(f'{b}_KEY_WHEEL_{sy}',box(0,y,wr+16,12,60,8),'shaft',b,note='DIN6885 12x8 nominal; fits/end clearance pending',qtytype='purchase')
  for side in [-1,1]:add(f'{b}_AXIAL_COLLAR_{sy}_{side}',cy(0,y+side*64,wr,31,16,ri=20),'shaft',b,note='split clamp collar envelope; axial retention rating pending',qtytype='purchase')
  yy=sy*p['bearing_y'];base=wr-49.2
  # UCP208 envelope with real shaft bore and approximate base hole positions.
  bearing=box(0,yy,base,184,54,18).fuse(cy(0,yy,wr,43,50,ri=20)).fuse(box(0,yy,base+15,90,45,25))
  bearing=bearing.cut(cy(0,yy,wr,20,70))
  for xx in [-68.5,68.5]:bearing=bearing.cut(cy(xx,yy,base+9,8.5,30,'Z'))
  add(f'{b}_UCP208_{sy}',bearing,'shaft',b,note='UCP208 envelope, d40, H49.2; supplier mounting dimensions must be confirmed',qtytype='purchase')
  add(f'{b}_BEARING_SHELF_{sy}',plate_holes(0,yy,base-12,220,100,12,[(q,yy,17) for q in [-68.5,68.5]]),'plate',b,note='S355 t12 shelf, 2 M14 bolts through17mm clearance holes')
  for sx in [-1,1]:add(f'{b}_HANGER_{sy}_{sx}',box(sx*102,yy,base,12,100,280-base),'plate',b,note='S355 welded hanger t12; welds and frame bolt tabs pending')
 # Upper bogie rails and crossmembers, clear of wheels and axle hardware.
 for yy in [-500,500]:add(f'{b}_LONG_TUBE_{yy}',tube(220,yy,280,760,40,80),'frame',b,mat='S355 RHS 80x40x3',qtytype='cut_purchase')
 for xx in [0, c2, mx if b=='rear' else 450]:add(f'{b}_CROSS_TUBE_{xx:.2f}',tube(xx,0,360,80,1800,40),'frame',b,mat='S355 RHS 80x40x3',qtytype='cut_purchase')
 # Bearing hangers connect upward to the cross at X0; vertical connector plate behind shelf.
 for sy in [-1,1]:add(f'{b}_HANGER_TOP_CONNECT_{sy}',box(0,sy*p['bearing_y'],280,220,100,80),'plate',b,note='Envelope welded bearing support; lightening/final bolt pattern pending')
 # Four guides per wheel: two faces at front and rear. They belong to yawing bogie.
 for sy in [-1,1]:
  y=sy*G/2
  for dx in [-p['guide_station'],p['guide_station']]:
   for side in [-1,1]:
    yy=y+side*p['guide_center_offset'];tag=f'{b}_GUIDE_{sy}_{dx}_{side}'
    points=[(7.5,-14),(24.5,-14),(25,0),(24.5,14),(7.5,14)]
    roll=cq.Workplane('XZ',origin=(dx,yy,-20)).polyline(points).close().revolve(360,(0,-1),(0,1)).val()
    add(tag,roll,'guide',b,note='Crowned PU50x28 envelope; bearing6002x2 and spindle details inherited as concept only',qtytype='custom')
    add(tag+'_SPINDLE',cy(dx,yy,0,7.5,100,'Z'),'shaft',b,note='smooth D15 spindle envelope, threads/bearing stack pending')
    posty=y+side*134
    add(tag+'_POST',tube(dx,posty,12,40,40,308),'frame',b,mat='S355 RHS40x40x3',qtytype='cut_purchase')
    arm=box(dx,(yy+posty)/2,4,60,abs(posty-yy)+40,8)
    slot=cq.Workplane('XY',origin=(dx,yy,3)).slot2D(25,16,90).extrude(10).val();arm=arm.cut(slot)
    add(tag+'_ADJUST_ARM',arm,'plate',b,note='S355 t8 arm,16x25 Y-slot, clamp/spacers not fully detailed')
 for gy in [-G/2-134,-G/2+134,G/2-134,G/2+134]:add(f'{b}_GUIDE_TOP_TIE_{gy}',tube(0,gy,320,400,40,40),'frame',b,mat='S355 RHS40x40x3',qtytype='cut_purchase')
 # Yaw bearing stack. Both upper/lower plates have bolt circles, centered yaw shaft is retained.
 for z,n in [(400,'LOWER'),(438,'UPPER')]:
  holes=[(65*math.cos(t),65*math.sin(t),9) for t in [i*math.pi/2 for i in range(4)]]
  s=plate_holes(0,0,z,180,180,12,holes).cut(cy(0,0,z+6,20,16,'Z'))
  add(f'{b}_YAW_{n}_PLATE',s,'plate',b,stage='bogie' if n=='LOWER' else 'yaw_carrier',note='M8 bolt-circle radius65 provisional; bearing retaining shoulders pending')
 add(b+'_YAW_THRUST_BEARING_ENVELOPE',cy(0,0,425,55,26,'Z',ri=20),'joint',b,stage='yaw_carrier',note='Paired angular-contact/turntable bearing selection pending; envelope not catalogue item',qtytype='purchase_pending')
 add(b+'_YAW_KINGPIN_D40',cy(0,0,427,20,80,'Z'),'shaft',b,stage='yaw_carrier',note='Kingpin retention and bearing fits pending')
 add(b+'_YAW_CARRIER',box(0,0,450,110,110,18).cut(cy(0,0,459,20,22,'Z')),'plate',b,stage='yaw_carrier')
 # Y-axis pitch trunnion: rotating carrier inside fixed fork.
 add(b+'_PITCH_INNER_LUG',box(0,0,468,70,80,50).cut(cy(0,0,p['pitch_z'],15,100)),'joint',b,stage='yaw_carrier')
 add(b+'_PITCH_PIN_D30',cy(0,0,p['pitch_z'],15,170),'shaft',b,stage='roll_carrier')
 for sy in [-1,1]:
  lug=box(0,sy*65,460,90,20,70).cut(cy(0,sy*65,p['pitch_z'],15,24))
  add(f'{b}_PITCH_FORK_{sy}',lug,'plate',b,stage='roll_carrier',note='Bushed pitch fork. Axial pin retention and bush fit pending')
 add(b+'_PITCH_FORK_TOP',box(0,0,530,120,160,12),'plate',b,stage='roll_carrier')
 if b=='front':
  # Front roll carrier rotates about X. Rear pitch fork instead fixed to chassis.
  add('front_ROLL_MOVING_LUG',box(0,0,542,80,70,60).cut(cy(0,0,p['roll_z'],15,90,'X')),'joint','front',stage='roll_carrier')
  add('front_ROLL_PIN_D30',cy(0,0,p['roll_z'],15,230,'X'),'shaft','front',stage='chassis')
  for xx in [-100,100]:add(f'front_ROLL_OUTER_LUG_{xx}',box(xx,0,545,20,100,75).cut(cy(xx,0,p['roll_z'],15,24,'X')),'plate','front',stage='chassis',note='Fixed chassis lugs; stops/retention pending')
 # visible yaw and roll stops are reserved blocks only.
 for sy in [-1,1]:add(f'{b}_YAW_STOP_RESERVED_{sy}',box(-110,sy*105,410,35,25,30),'joint',b,stage='yaw_carrier',note='Stop envelope. Contact angles and elastomer selection pending')
# Rear-only drive: two stages 14:42 and16:40, all shafts parallelY, all on yawing bogie.
def sprocket(name,x,y,N,bore,bogie='rear'):
 rp=p['chain_pitch']/(2*math.sin(math.pi/N));pts=[]
 for i in range(N*4):
  ang=2*math.pi*i/(N*4);rad=rp+(2 if i%4 in [1,2] else -3);pts.append((rad*math.cos(ang),rad*math.sin(ang)))
 s=cq.Workplane('XZ',origin=(x,y+3.5,wr)).polyline(pts).close().extrude(7).val().cut(cy(x,y,wr,bore/2,12))
 add(name,s,'chain',bogie,note=f'428 N={N}, nominal teeth visualization only, not cutter profile. Supplier hub/keyway pending',qtytype='purchase')
 return rp
r14=sprocket('MOTOR_428_14T',mx,250,p['stage1_small'],20);r42=sprocket('JACK_428_42T',c2,250,p['stage1_large'],30);r16=sprocket('JACK_428_16T',c2,0,p['stage2_small'],30);r40=sprocket('AXLE_428_40T',0,0,p['stage2_large'],40)
add('JACKSHAFT_D30',cy(c2,125,wr,15,370),'shaft','rear',note='C45 stepped/keyed jackshaft, shoulders/keyways not finalized')
for yy in [-35,285]:
 base=wr-42.9
 body=box(c2,yy,base,165,48,16).fuse(cy(c2,yy,wr,35,40,ri=15)).fuse(box(c2,yy,base+12,70,40,20)).cut(cy(c2,yy,wr,15,60))
 for xx in [-60.5,60.5]:body=body.cut(cy(c2+xx,yy,base+8,8.5,22,'Z'))
 add(f'JACK_BEARING_{yy}',body,'shaft','rear',note='UCP206 d30 envelope, H42.9 provisional; dimensions and rating supplier confirmation required',qtytype='purchase')
 add(f'JACK_SHELF_{yy}',plate_holes(c2,yy,base-12,200,48,12,[(c2+xx,yy,17) for xx in [-60.5,60.5]]),'plate','rear')
 for xx in [-94,94]:add(f'JACK_DROP_SUPPORT_{yy}_{xx}',box(c2+xx,yy,base,12,48,280-base),'plate','rear',note='Welded hanger and upper connection to bogie crossbeam')
# Continuous chain swept belt envelope follows pitch-circle tangents. No individual chain pins.
def chain(name,x1,x2,y,r1,r2):
 # Convex hull tangent with smooth sampled arcs; r2 at x2 larger for each stage.
 Cdist=x2-x1;alpha=math.acos((r1-r2)/Cdist);pts=[]
 for i in range(41):
  t=alpha+(2*math.pi-2*alpha)*i/40;pts.append((x1+r1*math.cos(t),wr+r1*math.sin(t)))
 for i in range(41):
  t=-alpha+2*alpha*i/40;pts.append((x2+r2*math.cos(t),wr+r2*math.sin(t)))
 # Thin plates between outer and inner similar outlines: envelope, not exact roller link geometry.
 outer=cq.Workplane('XZ',origin=(0,y+5,0)).polyline(pts).close().extrude(10).val()
 # Simple thin chain strap via perimeter faces using outward polygon scaling around midpoint.
 cx=(x1+x2)/2;inner=[(cx+(x-cx)*.985,wr+(z-wr)*.92) for x,z in pts]
 innerSolid=cq.Workplane('XZ',origin=(0,y+6,0)).polyline(inner).close().extrude(12).val()
 s=outer.cut(innerSolid)
 add(name,s,'chain','rear',note='Chain swept ENVELOPE only; tangent pitch geometry approximate, no tooth engagement or dynamic tension check',qtytype='purchase')
# use small left, large right orientation by reflecting coordinates where needed.
chain('CHAIN_STAGE1_70LINK_ENVELOPE',-mx,-c2,250,r14,r42)
# Mirror stage1 geometry to actual positive X locations.
parts[-1]['shape']=parts[-1]['shape'].mirror('YZ');byname[parts[-1]['name']]=parts[-1]['shape']
chain('CHAIN_STAGE2_70LINK_ENVELOPE',-c2,0,0,r16,r40)
parts[-1]['shape']=parts[-1]['shape'].mirror('YZ');byname[parts[-1]['name']]=parts[-1]['shape']
# Motor envelope: selected OEM QS12070H non-geared. Mounting interfaces still unconfirmed.
add('QS120_70H_72V_2KW_ENVELOPE',cy(mx,365,wr,p['motor_d']/2,p['motor_length']).fuse(box(mx,295,52,90,30,23)).fuse(box(mx,435,52,90,30,23)),'motor','rear',note='Selected direct-output QS12070H; motor casing and foot-adaptor geometry placeholder, not OEM CAD; foot hole pattern provisional',qtytype='purchase')
add('MOTOR_OUTPUT_SHAFT_INTERFACE_PENDING',cy(mx,267,wr,p['motor_shaft_d']/2,40),'shaft','rear',note='Shaft interface placeholder; factory spline/key/retainer must be ordered together')
add('MOTOR_ADJUST_PLATE',plate_holes(mx,365,wr-110,240,220,12,[(mx+sx*30,365+sy*70,9) for sx in [-1,1] for sy in [-1,1]]),'plate','rear',note='Blank base plate with provisional frame holes; OEM motor tabs/slots pending')
for sy in [-1,1]:add(f'MOTOR_SUPPORT_RISER_{sy}',box(mx,365+sy*95,wr-98,220,12,280-(wr-98)),'plate','rear',note='Welded drop frame; motor foot adaptor and chain tension slots pending')
# Chassis beams at Z550. Rear fork upperplate connects chassis through crossmember at rear.
for yy in [-500,500]:add(f'CHASSIS_LONG_{yy}',tube(0,yy,p['frame_z'],1800,40,80),'frame',stage='chassis',mat='S355 RHS80x40x3',qtytype='cut_purchase')
for xx in [-L/2,L/2-100,L/2+100,-850,850]:add(f'CHASSIS_CROSS_{xx}',tube(xx,0,p['frame_z'],80,1040,40),'frame',stage='chassis',mat='S355 RHS80x40x3',qtytype='cut_purchase')
for sy in [-1,1]:add(f'rear_FORK_CHASSIS_RISER_{sy}',box(0,sy*65,542,80,30,p['frame_z']-542),'plate','rear',stage='chassis',note='Rear roll fixed through two chassis risers')
# brake rotor on axle and reserved caliper on bogie; friction brake still unselected.
for b in ['rear','front']:
 add(b+'_BRAKE_DISC_200_ENVELOPE',cy(0,-250,wr,100,4,ri=20),'chain',b,note='Disk/hub interface needs selection. Not certified braking hardware.',qtytype='purchase_pending')
 add(b+'_CALIPER_RESERVED',box(85,-250,wr-30,55,55,60),'joint',b,note='Caliper keep-out, excluded from physical interference checks',qtytype='reserved_space')
# Pose transforms preserve chain and axle alignment by moving whole bogie together.
def transform(s,d,pose):
 b=d['bogie'];stage=d['stage']
 if b:
  if stage=='bogie':s=s.rotate((0,0,p['yaw_z']),(0,0,p['yaw_z']+1),pose.get(b+'_yaw',0))
  if stage in ['bogie','yaw_carrier']:s=s.rotate((0,0,p['pitch_z']),(0,1,p['pitch_z']),pose.get(b+'_pitch',0))
  if b=='front' and stage in ['bogie','yaw_carrier','roll_carrier']:s=s.rotate((0,0,p['roll_z']),(1,0,p['roll_z']),pose.get('front_roll',0))
  return s.translate(((-L/2 if b=='rear' else L/2),0,0))
 return s
poses={'Straight':{},'Curve_R50':{'rear_yaw':-math.degrees(math.asin(L/2000/p['curve_pose_radius_m'])),'front_yaw':math.degrees(math.asin(L/2000/p['curve_pose_radius_m']))},'Articulation_DEMO':{'rear_pitch':p['rear_pitch_pose_deg'],'front_pitch':p['front_pitch_pose_deg'],'front_roll':p['front_roll_pose_deg']}}
(R/'poses.json').write_text(json.dumps(poses,indent=2))
for label,pose in poses.items():
 a=cq.Assembly(name='AXLE_DRIVE_R02_'+label)
 for d in parts:a.add(transform(d['shape'],d,pose),name=d['name'],color=cq.Color(*C[d['group']]))
 a.save(str(R/'cad'/('AxleDrive_'+label+'.step')));print('Exported',label,len(parts),flush=True)
# Lightweight rendering mesh export avoids repeatedly tessellating detailed geometry.
import numpy as np
meshes=[]
for d in parts:
 v,f=d['shape'].tessellate(3,.45);vv=np.array([[a.x,a.y,a.z] for a in v]);ff=np.array(f,dtype=int)
 meshes.append({'name':d['name'],'vertices':vv.tolist(),'faces':ff.tolist(),'group':d['group'],'bogie':d['bogie'],'stage':d['stage']})
(R/'render_mesh.json').write_text(json.dumps(meshes))
# selected custom components for fabrication development, not release drawings.
for d in parts:
 if any(q in d['name'] for q in ['LIVE_AXLE','RAILWHEEL','MOTOR_ADJUST_PLATE','YAW_LOWER_PLATE','PITCH_FORK','ROLL_OUTER']):cq.exporters.export(d['shape'],str(R/'parts'/(d['name']+'.step')))
with (R/'BOM_parts.csv').open('w',newline='') as f:
 w=csv.writer(f);w.writerow(['name','quantity','type','material','group','bogie','joint_stage','note'])
 for d in parts:w.writerow([d['name'],1,d['type'],d['material'],d['group'],d['bogie'],d['stage'],d['note']])
(R/'reports/Build_validation.json').write_text(json.dumps({'all_parts_valid':True,'each_part_one_solid':True,'parts':len(parts),'guide_rollers':sum('_GUIDE_' in d['name'] and '_GUIDE_TOP_' not in d['name'] and not any(d['name'].endswith(s) for s in ['SPINDLE','POST','ADJUST_ARM']) for d in parts),'chain_centers_mm':[c1,c2],'chain_ratio':p['stage1_large']/p['stage1_small']*p['stage2_large']/p['stage2_small'],'mesh_is_reference_not_fusion_history':True},indent=2))
print('Done',flush=True)
