"""QS212 straight-rail module -- parametric exterior and fabrication draft.
Run with CadQuery 2.7. Change parameters.json and rerun. All lengths mm.
"""
from pathlib import Path
import cadquery as cq
import math,json,csv,shutil,hashlib
ROOT=Path(__file__).resolve().parent
for d in ['cad','reference','drawings','reports','fusion360','parts']: (ROOT/d).mkdir(exist_ok=True)
DEFAULT={
 'tire_od':406.4,'tire_width':76.2,'motor_case_d':238,'motor_case_width':78,
 'axle_length':270,'mount_outer_span':200.5,'axle_d':16,'axle_af':12,'axle_fit_clearance':0.2,
 'plate_t':10,'plate_width':220,'plate_below':45,'plate_above':125,'keeper_t':10,
 'rail_head_width':65,'rail_head_depth':49,'rail_height':174,'rail_web_width':16.5,'rail_base_width':145,'rail_length':900,
 'rail_side_slope':0.025,'rail_side_ref_depth':40,'roller_crown':0.5,'roller_d':50,'roller_width':28,'roller_station':220,'roller_center_z':-20,'guide_gap':1,'guide_adjust':6,
 'bearing_id':15,'bearing_od':32,'bearing_width':9,'roller_core_d':42,'spacer_outer_d':21,
 'yoke_arm_t':8,'yoke_wall_t':12,'yoke_width':60,'shaft_thread_d':12,'shaft_thread_length':38,
 'profile_size':40,'frame_half_y':134,'frame_length':580,'frame_top_bottom_z':430,'frame_bottom_z':-52,'brace_beam_z':110,
 'motor_post_x':85,'total_mass_kg':200,'max_wheel_fraction':0.4,'dynamic_factor':2,'guide_lateral_force_N':500,'drive_torque_Nm':100
}
pfile=ROOT/'parameters.json'
if not pfile.exists():pfile.write_text(json.dumps(DEFAULT,indent=2))
p=json.loads(pfile.read_text()); env={**p,'pi':math.pi,'sqrt':math.sqrt,'abs':abs,'min':min,'max':max}
def V(v):return float(eval(v,{'__builtins__':{}},env)) if isinstance(v,str) else float(v)
def S(v):return str(v)
def plus(a,b):return f'({a})+({b})'
def neg(a):return f'-({a})'
manifest=[]; shapes={};meta=[]
COL={'frame':(.22,.49,.70),'steel':(.62,.65,.69),'fabricated':(.90,.58,.16),'roller':(.08,.48,.32),'rubber':(.04,.04,.045),'bolt':(.25,.27,.3),'rail':(.52,.54,.56),'motor':(.10,.11,.12),'ref':(.2,.2,.2)}
def primitive(plane,offset,length,profile,**kw):return dict(plane=plane,offset=S(offset),length=S(length),profile=profile,**kw)
def rect(plane,offset,length,u0,v0,u1,v1):return primitive(plane,offset,length,'poly',points=[[S(u0),S(v0)],[S(u1),S(v0)],[S(u1),S(v1)],[S(u0),S(v1)]])
def circ(plane,offset,length,u,v,r,ri=None):return primitive(plane,offset,length,'circle',center=[S(u),S(v)],radius=S(r),**({'inner_radius':S(ri)} if ri is not None else {}))
def box(x0,y0,z0,x1,y1,z1):return rect('XY',z0,f'({z1})-({z0})',x0,y0,x1,y1)
def slot(plane,offset,length,u,v,width,travel):return primitive(plane,offset,length,'slot',center=[S(u),S(v)],width=S(width),travel=S(travel)) # long local V

def solid(op):
 if op['profile'] in ['revolve_z','revolve_y']:
  cx,cy,cz=map(V,op['center3'])
  wp=cq.Workplane('XZ' if op['profile']=='revolve_z' else 'XY',origin=(cx,cy,cz))
  return wp.polyline([(V(a),V(b)) for a,b in op['points']]).close().revolve(360,(0,-1),(0,1)).val()
 plane=op['plane']; off=V(op['offset']); length=V(op['length'])
 origin={'XY':(0,0,off),'YZ':(off,0,0),'XZ':(0,-off,0)}[plane]
 wp=cq.Workplane(plane,origin=origin)
 if op['profile']=='poly':wp=wp.polyline([(V(a),V(b)) for a,b in op['points']]).close()
 elif op['profile']=='circle':
  u,v=map(V,op['center']);wp=wp.center(u,v).circle(V(op['radius']))
  if 'inner_radius' in op:wp=wp.circle(V(op['inner_radius']))
 else:
  u,v=map(V,op['center']);w=V(op['width']);t=V(op['travel'])
  wp=wp.center(u,v).slot2D(w+t,w,angle=90)
 return wp.extrude(length).val()

def part(name,group,adds,cuts=None,category='custom',material='S355 steel',note='',explode=(0,0,0),bom=True):
 shape=solid(adds[0])
 for op in adds[1:]:shape=shape.fuse(solid(op))
 for op in cuts or []:shape=shape.cut(solid(op))
 shape=shape.clean()
 if not shape.isValid():raise ValueError('Invalid '+name)
 if len(shape.Solids())!=1:raise ValueError('Disconnected part '+name+':'+str(len(shape.Solids())))
 shapes[name]=shape
 manifest.append(dict(name=name,group=group,adds=adds,cuts=cuts or [],category=category,material=material,note=note,explode=explode,bom=bom))
 return name
# Nominal placeholder rail. This is deliberately NOT a named Korean rail section.
w='rail_head_width/2';b='rail_base_width/2';web='rail_web_width/2';hd='rail_head_depth';rh='rail_height'
# KRS60K, appendix3 (PDF page19), nominal dimensions. Arc transitions simplified.
railpts=[]
# R300 crown sampled (top tangent height0), NOT an exact certified contour.
for i in range(13):
 u=f'(-24+4*{i})*rail_head_width/65';railpts.append([u,f'sqrt(300**2-({u})**2)-300'])
railpts += [[f'rail_head_width/2-2','-6'],[f'rail_head_width/2-rail_side_slope*(13-0)','-27'],[f'rail_head_width/2','-40'],[f'rail_head_width/2-2','-41.9'],['rail_web_width/2+8','-49'],['rail_web_width/2','-65'],['rail_web_width/2','-132'],['rail_web_width/2+8','-143.9'],['rail_base_width/2','-162'],['rail_base_width/2','-rail_height'],['-rail_base_width/2','-rail_height'],['-rail_base_width/2','-162'],['-rail_web_width/2-8','-143.9'],['-rail_web_width/2','-132'],['-rail_web_width/2','-65'],['-rail_web_width/2-8','-49'],['-rail_head_width/2+2','-41.9'],['-rail_head_width/2','-40'],['-rail_head_width/2+rail_side_slope*13','-27'],['-rail_head_width/2+2','-6']]
# The tapered side used for contact runs -13..-40, exact slope1:40.
railpts=railpts[:14]+[[f'rail_head_width/2-rail_side_slope*27','-13']]+railpts[14:]
railpts.insert(-1,['-rail_head_width/2+rail_side_slope*27','-13'])
part('R00_Rail_KRS60K_ENVELOPE_SITE_UNCONFIRMED','rail',[primitive('YZ','-rail_length/2','rail_length','poly',points=railpts)],category='reference',material='KRS TR0001-15(R) appendix3 60K nominal envelope; transition radii approximate',explode=(0,0,-150),bom=False)
# Parametric external motor representation, replaces neither OEM STEP nor vendor certification.
tire_points=[['127*tire_od/406.4', '-27*tire_width/76.2'], ['139*tire_od/406.4', '-34*tire_width/76.2'], ['165*tire_od/406.4', '-38.1*tire_width/76.2'], ['188*tire_od/406.4', '-34*tire_width/76.2'], ['201*tire_od/406.4', '-23*tire_width/76.2'], ['203.2*tire_od/406.4', '0*tire_width/76.2'], ['201*tire_od/406.4', '23*tire_width/76.2'], ['188*tire_od/406.4', '34*tire_width/76.2'], ['165*tire_od/406.4', '38.1*tire_width/76.2'], ['139*tire_od/406.4', '34*tire_width/76.2'], ['127*tire_od/406.4', '27*tire_width/76.2'], ['127*tire_od/406.4', '20*tire_width/76.2'], ['145*tire_od/406.4', '25*tire_width/76.2'], ['165*tire_od/406.4', '28*tire_width/76.2'], ['184*tire_od/406.4', '24*tire_width/76.2'], ['192*tire_od/406.4', '15*tire_width/76.2'], ['194*tire_od/406.4', '0*tire_width/76.2'], ['192*tire_od/406.4', '-15*tire_width/76.2'], ['184*tire_od/406.4', '-24*tire_width/76.2'], ['165*tire_od/406.4', '-28*tire_width/76.2'], ['145*tire_od/406.4', '-25*tire_width/76.2'], ['127*tire_od/406.4', '-20*tire_width/76.2']]
part('M01_Rotating_tire_ASSUMED','rubber',[dict(plane='XY',offset='0',length='0',profile='revolve_y',center3=['0','0','tire_od/2'],points=tire_points)],category='purchase',material='rubber3.00-10 ASSUMED',note='Section approximates uploaded STEP; actual tire OD,width and load rating TBD.',explode=(0,-200,0))
# Above annulus cylinder has flat sidewalls; detailed CAD exports substitute the input tire.
part('M02_Rotating_motor_envelope','motor',[circ('XZ','-motor_case_width/2','motor_case_width','0','tire_od/2','motor_case_d/2'),circ('XZ','-36.5','73','0','tire_od/2','139.5','116')],category='purchase',material='QS212 1200W input reference',note='Motor only; no holes or attachments added to housing.',explode=(0,160,0))
# Axle has flats at Z +/- AF/2 on outer parts, reference only, not to be fabricated.
axadds=[circ('XZ','-axle_length/2','axle_length','0','tire_od/2','axle_d/2')]
axcuts=[]
for side in [-1,1]:
 lo='64' if side>0 else '-axle_length/2';hi='axle_length/2' if side>0 else '-64'
 axcuts += [box('-15',lo,'tire_od/2+axle_af/2','15',hi,'tire_od/2+20'),box('-15',lo,'tire_od/2-20','15',hi,'tire_od/2-axle_af/2')]
part('M03_Fixed_axle_INPUT_REFERENCE','steel',axadds,axcuts,category='reference',material='OEM axle unknown steel',note='D16 AF12 L270 are input-model dimensions, MUST measure OEM.',explode=(0,0,0),bom=False)
# Generic slotted 4040 section: envelope/slot fit study only, not exact supplier section.
def profile(name,axis,start,length,c1,c2):
 # plane offsets aligned with local coordinates. Four external slots are modeled.
 adds=[rect(axis,start,length,f'({c1})-profile_size/2',f'({c2})-profile_size/2',f'({c1})+profile_size/2',f'({c2})+profile_size/2')]
 cuts=[circ(axis,f'({start})-0.1',f'({length})+0.2',c1,c2,'3.4')]
 # T-slot root transitions leave diagonal webs connected; envelope, not supplier section.
 for side in [-1,1]:
  for rot in range(2):
   coords=[(-9,15.2),(-9,12),(-5,8),(5,8),(9,12),(9,15.2)]
   pts=[]
   for uu,vv in coords:
    aa,bb=(uu,side*vv) if rot==0 else (side*vv,uu)
    pts.append([f'({c1})+({aa})',f'({c2})+({bb})'])
   cuts.append(primitive(axis,f'({start})-0.1',f'({length})+0.2','poly',points=pts))
 part(name,'frame',adds,cuts,category='purchase',material='HFS8-4040 family; 10mm slot, section envelope',note='Supplier full section CAD and allowable connection loads required.',explode=(0,0,90))
for sy in [-1,1]:
 Y=f'({sy})*frame_half_y'
 profile(f'F01_Long_beam_{sy}','YZ','-frame_length/2','frame_length',Y,'frame_top_bottom_z+profile_size/2')
 for sx in [-1,1]:
  for kind,pos in [('motor','motor_post_x'),('guide','roller_station')]:
   X=f'({sx})*({pos})'
   postbottom='brace_beam_z' if kind=='motor' else 'frame_bottom_z'
   profile(f'F02_Post_{kind}_{sx}_{sy}','XY',postbottom,f'frame_top_bottom_z-({postbottom})',X,Y)
for sx in [-1,1]:
 profile(f'F03_Cross_beam_{sx}','XZ','-frame_half_y+profile_size/2','2*frame_half_y-profile_size',f'({sx})*(frame_length/2-profile_size/2)','frame_top_bottom_z+profile_size/2')
# Axle plates and removable inboard torque keepers. Outboard nuts remain accessible.
for sy in [-1,1]:
 outer=f'({sy})*mount_outer_span/2'
 ymax='mount_outer_span/2' if sy>0 else '-mount_outer_span/2+plate_t'
 ymin=f'({ymax})-plate_t'
 adds=[rect('XZ',neg(ymax),'plate_t','-plate_width/2','tire_od/2-plate_below','plate_width/2','tire_od/2+plate_above')]
 # Open-bottom slot, upper flat stops axle rotation; removable keeper closes lower flat.
 cuts=[rect('XZ',f'-({ymax})-1','plate_t+2','-(axle_d+axle_fit_clearance)/2','tire_od/2-plate_below-1','(axle_d+axle_fit_clearance)/2','tire_od/2+(axle_af+axle_fit_clearance)/2')]
 for sx in [-1,1]:
  for zz in ['tire_od/2-20','tire_od/2+40','tire_od/2+100']:
   cuts.append(circ('XZ',f'-({ymax})-1','plate_t+2',f'({sx})*motor_post_x',zz,'4.5'))
  cuts.append(circ('XZ',f'-({ymax})-1','plate_t+2',f'({sx})*20','tire_od/2-18','4.5'))
 name=f'A01_Axle_plate_{sy}'
 part(name,'fabricated',adds,cuts,note='Laser outer contour; CNC slot and flats; S355 10mm. Notch tolerance final per measured axle.',explode=(0,sy*110,0))
 # Inboard keeper no extra axial stack under the M16 nut.
 kymax='mount_outer_span/2-plate_t' if sy>0 else '-mount_outer_span/2+plate_t+keeper_t'
 kcuts=[circ('XZ',f'-({kymax})-1','keeper_t+2',f'({s})*20','tire_od/2-18','3.4') for s in [-1,1]]
 part(f'A02_Torque_keeper_{sy}','fabricated',[rect('XZ',neg(kymax),'keeper_t','-30','tire_od/2-30','30','tire_od/2-(axle_af+axle_fit_clearance)/2')],kcuts,note='2x M8 tapped; lower axle flat restraint, bolt from outboard face. Machine upper face.',explode=(0,sy*140,-45))
 # OEM M16 washer and nut positions set to plate outer face; thread detail omitted.
 wymax='mount_outer_span/2+3' if sy>0 else '-mount_outer_span/2'
 part(f'A03_M16_washer_{sy}','steel',[circ('XZ',neg(wymax),'3','0','tire_od/2','16','8.2')],category='purchase',material='OEM M16 hardened washer',explode=(0,sy*190,0))
 nymax='mount_outer_span/2+16' if sy>0 else '-mount_outer_span/2-3'
 poly=[[f'13.856*cos({i}*pi/3)',f'tire_od/2+13.856*sin({i}*pi/3)'] for i in range(6)]
 # cos/sin expressions are also supported by Fusion script.
 env.update(cos=math.cos,sin=math.sin)
 part(f'A04_M16_axle_nut_{sy}','steel',[primitive('XZ',neg(nymax),'13','poly',points=poly)],[circ('XZ',f'-({nymax})-1','15','0','tire_od/2','8')],category='purchase',material='OEM M16x1.5 nut; confirm thread',explode=(0,sy*220,0))
# Full fastener shapes (threads omitted); plate clearance and T-slot positions explicit.
def bolt(name,plane,offset,grip,u,v,d=8,head_d=13,head_h=8):
 # head at origin side, shank projects +normal
 sgn=1 if V(grip)>0 else -1
 part(name,'bolt',[circ(plane,offset,grip,u,v,S(d/2)),circ(plane,f'({offset})-({sgn})*({head_h})',sgn*head_h,u,v,S(head_d/2))],category='purchase',material=f'ISO4762 M{d}, class8.8; unthreaded envelope',note='Length including grip indicated in fastener schedule.',bom=False)
def washer(name,plane,offset,length,u,v,dout,din):
 part(name,'steel',[circ(plane,offset,length,u,v,S(dout/2),S(din/2))],category='purchase',material='hardened steel washer',bom=False)
# Axle plate to profile: 13.75mm spacers nominal, parametric with span/profile.
for sy in [-1,1]:
 # each bolt axis points outward from wheel into inner T-slot
 plane='XZ'; start='-mount_outer_span/2' if sy>0 else 'mount_outer_span/2' # use orientation through full shape then mirror generated negative-Y geometry for + side
 for sx in [-1,1]:
  for iz,z in enumerate(['tire_od/2-20','tire_od/2+40','tire_od/2+100']):
   x=f'({sx})*motor_post_x'; gap='frame_half_y-profile_size/2-mount_outer_span/2'
   ymax='frame_half_y-profile_size/2' if sy>0 else '-mount_outer_span/2'
   part(f'A05_Spacer_{sy}_{sx}_{iz}','steel',[circ('XZ',neg(ymax),gap,x,z,'10','4.5')],category='custom',material='S355 spacer tube OD20 ID9',note='Nominal length13.75; grind to equal length.',bom=False)
   # Bolt from inboard toward outboard. PositiveY side mirrored after generic geometry.
   off='mount_outer_span/2-plate_t-1.6' if sy<0 else '-mount_outer_span/2+plate_t+1.6'
   bolt(f'B01_Plate_M8x35_{sy}_{sx}_{iz}','XZ',off,('35' if sy<0 else '-35'),x,z)
   # model T nut behind inner slot face, (not detailed supplier clip)
   y0='frame_half_y-profile_size/2+5' if sy>0 else '-frame_half_y+profile_size/2-11'
   part(f'B02_Plate_Tnut_M8_{sy}_{sx}_{iz}','bolt',[box(f'({x})-8.5',y0,f'({z})-5',f'({x})+8.5',f'({y0})+6',f'({z})+5')],[circ('XZ',f'-({y0})-7','8',x,z,'3.4')],category='purchase',material='HFS8 series M8 T nut envelope',bom=False)
 # keeper bolts from plate outboard towards centre: generic head placement separately handled in schedule.
 for sx in [-1,1]:
  # for sy>0 normal -Y correct; left bolt normal+Y cannot expressed without flipping; place head as separate semantic envelope.
  off='-mount_outer_span/2-1.6' if sy>0 else 'mount_outer_span/2+1.6'
  bolt(f'B03_Keeper_M8x20_{sy}_{sx}','XZ',off,('20' if sy>0 else '-20'),f'({sx})*20','tire_od/2-18')
# Guide stations, roller-bearing-shaft stack, slotted removable top plate and jack screw.
for sx in [-1,1]:
 X=f'({sx})*roller_station'
 for sy in [-1,1]:
  tag=f'{sx}_{sy}'; Y=f'({sy})*(rail_head_width/2+roller_d/2+guide_gap-rail_side_slope*(roller_center_z+rail_side_ref_depth)+rail_side_slope**2*roller_width**2/(16*roller_crown))'
  wall_abs='frame_half_y-profile_size/2'; wall_mid=f'({sy})*(({wall_abs})-yoke_wall_t/2)'
  walllo=f'({wall_mid})-yoke_wall_t/2';wallhi=f'({wall_mid})+yoke_wall_t/2'
  armlo=f'({Y})-17' if sy>0 else f'-({wall_abs})';armhi=wall_abs if sy>0 else f'({Y})+17'
  # Roller tire at -34..-6, core fits 6002 with central shoulder.
  rpts=[[f'roller_d/2-roller_crown*(-1+{i}/8)**2',f'roller_width/2*(-1+{i}/8)'] for i in range(17)]+[['roller_core_d/2','roller_width/2'],['roller_core_d/2','-roller_width/2']]
  part('G01_PU_roller_'+tag,'roller',[dict(plane='XZ',offset='0',length='0',profile='revolve_z',center3=[X,Y,'roller_center_z'],points=rpts)],category='custom',material='bonded polyurethane ShoreA90; qualified roller supplier',note='OD50 W28 default. Purchase substitute only after dimensions/load/speed verified.',explode=(sx*70,sy*60,-40))
  corecuts=[circ('XY','roller_center_z-roller_width/2-1','bearing_width+1',X,Y,'bearing_od/2'),circ('XY','roller_center_z+roller_width/2-bearing_width','bearing_width+1',X,Y,'bearing_od/2')]
  part('G02_roller_core_'+tag,'steel',[circ('XY','roller_center_z-roller_width/2','roller_width',X,Y,'roller_core_d/2','12')],corecuts,note='6061-T6 core; OD42; 2x D32 bearing seats, center shoulder ID24. Seat/retention fit must be set with bearing supplier.',explode=(sx*70,sy*60,-40))
  for k,z in enumerate(['roller_center_z-roller_width/2','roller_center_z+roller_width/2-bearing_width']):
   part(f'G03_6002DDU_{tag}_{k}','steel',[circ('XY',z,'bearing_width',X,Y,'bearing_od/2','bearing_id/2')],category='purchase',material='NSK6002DDU 15x32x9',explode=(sx*70,sy*60,60 if k else -100))
  part('G04_Inner_spacer_'+tag,'steel',[circ('XY','roller_center_z-roller_width/2+bearing_width','roller_width-2*bearing_width',X,Y,'spacer_outer_d/2','(bearing_id+0.2)/2')],material='C45 ground spacer',note='Length equal distance between bearing inner faces. No axial preload on outer races.',explode=(sx*70,sy*60,-40))
  for k,z in enumerate(['roller_center_z-roller_width/2-10','roller_center_z+roller_width/2']):
   part(f'G05_End_spacer_{tag}_{k}','steel',[circ('XY',z,'10',X,Y,'spacer_outer_d/2','(bearing_id+0.2)/2')],material='C45 ground spacer',bom=False)
  # shaft smooth between arm inner faces -44..4, reduced M12 ends.
  zbot='roller_center_z-roller_width/2-10';ztop='roller_center_z+roller_width/2+10'
  part('G06_Spindle_'+tag,'steel',[circ('XY',zbot,'roller_width+20',X,Y,'bearing_id/2'),circ('XY',f'({zbot})-shaft_thread_length','shaft_thread_length',X,Y,'shaft_thread_d/2'),circ('XY',ztop,'shaft_thread_length',X,Y,'shaft_thread_d/2')],material='C45 normalized; D15 bearing seat; M12x1.75 ends',note='Double shear with reduced thread sections; no threads under bearing inner rings. Thread runout/fillet per fabrication draft.',explode=(sx*70,sy*60,130))
  # fixed lower weldment, vertical wall and lower horizontal arm
  lowerz=f'({zbot})-yoke_arm_t'
  walladds=[box(f'({X})-yoke_width/2',walllo,lowerz,f'({X})+yoke_width/2',wallhi,ztop),box(f'({X})-yoke_width/2',armlo,lowerz,f'({X})+yoke_width/2',armhi,zbot)]
  cuts=[slot('XY',f'({lowerz})-1','yoke_arm_t+2',X,Y,'13','2*guide_adjust')]
  for xx in [0]:
   for zz in [-40,-24,-8]: cuts.append(circ('XZ',f'-({wallhi})-1','yoke_wall_t+2',f'({X})+({xx})',S(zz),'4.5'))
  # top wall M6 taps are vertical, two screws; slots allow lateral adjustment only at roller shaft.
  for xx in [-20,20]:cuts.append(circ('XY',f'({ztop})-14','15',f'({X})+({xx})',wall_mid,'2.5'))
  part('G07_Lower_yoke_weldment_'+tag,'fabricated',walladds,cuts,note='S355 wall12 + arm8; continuous 4mm fillet weld both sides accessible; stress-relieve/finish machine; top M6 tapped.',explode=(sx*120,sy*70,-60))
  topcuts=[slot('XY',f'({ztop})-1','yoke_arm_t+2',X,Y,'13','2*guide_adjust')]
  for xx in [-20,20]:topcuts.append(circ('XY',f'({ztop})-1','yoke_arm_t+2',f'({X})+({xx})',wall_mid,'3.3'))
  # M8 jack lug on removable upper arm, acts on sliding upper carrier.
  topadds=[box(f'({X})-yoke_width/2',armlo,ztop,f'({X})+yoke_width/2',armhi,f'({ztop})+yoke_arm_t'),box(f'({X})-8',walllo,f'({ztop})+yoke_arm_t',f'({X})+8',wallhi,f'({ztop})+yoke_arm_t+24')]
  topcuts.append(circ('XZ',f'-({wallhi})-1','yoke_wall_t+2',X,f'({ztop})+yoke_arm_t+6','3.4'))
  part('G08_Removable_top_arm_'+tag,'fabricated',topadds,topcuts,note='S355 arm8 + jack lug; 2x M6x25 into lower wall; shaft slot13x25; M8 horizontal jack thread.',explode=(sx*100,sy*70,100))
  # Clamp plates act as broad washers across the slots.
  for k,z in enumerate([f'({lowerz})-12',f'({ztop})+yoke_arm_t']):
   part(f'G09_Sliding_clamp_{tag}_{k}','steel',[box(f'({X})-20',f'({Y})-20',z,f'({X})+20',f'({Y})+20',f'({z})+12')],[circ('XY',f'({z})-1','14',X,Y,'6.5')],material='S355 clamp40x40x12',explode=(sx*70,sy*60,-120 if k==0 else 130))
  # Nuts and washers close the inner-ring/spacer/yoke load path; shaft ends simplified.
  for k,z in enumerate([f'({lowerz})-12-2.5-10',f'({ztop})+yoke_arm_t+12+2.5']):
   pts=[[f'({X})+10.392*cos({i}*pi/3)',f'({Y})+10.392*sin({i}*pi/3)'] for i in range(6)]
   part(f'G10_M12_nut_{tag}_{k}','bolt',[primitive('XY',z,'10','poly',points=pts)],[circ('XY',f'({z})-1','12',X,Y,'6')],category='purchase',material='M12 locknut, prevailing torque',bom=False)
  # yoke-profile four M8x25; each passes wall only and engages T nut on tower inward face.
  for xx in [0]:
   for zz in [-40,-24,-8]:
    off=f'-({wall_abs})+yoke_wall_t+1.6' if sy>0 else f'({wall_abs})-yoke_wall_t-1.6'
    bolt(f'B04_Yoke_M8x25_{tag}_{xx}_{zz}','XZ',off,('-25' if sy>0 else '25'),f'({X})+({xx})',S(zz))
  for xx in [-20,20]: bolt(f'B05_Top_M6x25_{tag}_{xx}','XY',f'({ztop})+yoke_arm_t+1.6','-25',f'({X})+({xx})',wall_mid,d=6,head_d=10,head_h=6)
  # Jack screw indication, final adjustment on both supports checked with square.
  off=f'-({wall_abs})-4' if sy>0 else f'({wall_abs})+4'
  bolt('B06_Jack_M8x40_'+tag,'XZ',off,('40' if sy>0 else '-40'),X,f'({ztop})+yoke_arm_t+6')
# Catalogue angle envelopes at each upright and cross-beam end. Drill positions are provisional vendor envelope.
for sy in [-1,1]:
 for sx in [-1,1]:
  for kind,pos in [('motor','motor_post_x'),('guide','roller_station')]:
   X=f'({sx})*({pos})';Y=f'({sy})*frame_half_y';tag=f'{kind}_{sx}_{sy}'
   adds=[box(f'({X})+20',f'({Y})-18','frame_top_bottom_z-40',f'({X})+25',f'({Y})+18','frame_top_bottom_z'),box(f'({X})+20',f'({Y})-18','frame_top_bottom_z-5',f'({X})+60',f'({Y})+18','frame_top_bottom_z')]
   cuts=[circ('YZ',f'({X})+19','7',Y,'frame_top_bottom_z-20','4.5'),circ('XY','frame_top_bottom_z-6','7',f'({X})+40',Y,'4.5')]
   part('F04_Angle_envelope_'+tag,'steel',adds,cuts,category='purchase',material='HBLFSN8 family 40-series angle; envelope only',note='Replace with supplier CAD before ordering hole-sensitive parts.',explode=(0,sy*50,60))
# Guide mounting T-nuts and washers, actual slot centres X=station.
for sx in [-1,1]:
 X=f'({sx})*roller_station'
 for sy in [-1,1]:
  for zz in [-40,-24,-8]:
   y0='frame_half_y-profile_size/2+5' if sy>0 else '-frame_half_y+profile_size/2-11'
   part(f'B07_Guide_Tnut_{sx}_{sy}_{zz}','bolt',[box(f'({X})-8.5',y0,f'{zz}-5',f'({X})+8.5',f'({y0})+6',f'{zz}+5')],[circ('XZ',f'-({y0})-7','8',X,str(zz),'3.4')],category='purchase',material='HFS8 M8 Tnut envelope',bom=False)
# Four top splice straps, 2x M8 each, across coplanar top slots.
for sx in [-1,1]:
 for sy in [-1,1]:
  X=f'({sx})*(frame_length/2-profile_size/2)';Y=f'({sy})*(frame_half_y-20)';Z='frame_top_bottom_z+profile_size'
  cuts=[circ('XY',f'({Z})-1','8',X,f'({Y})+({s})*20','4.5') for s in [-1,1]]
  part(f'F05_Top_splice_{sx}_{sy}','fabricated',[box(f'({X})-20',f'({Y})-40',Z,f'({X})+20',f'({Y})+40',f'({Z})+6')],cuts,note='S35540x80x6; 2xD9 on40 pitch; top faces of crossbeam and longbeam.',explode=(0,0,130))
  for k in [-1,1]:
   bolt(f'B08_Splice_M8x20_{sx}_{sy}_{k}','XY',f'({Z})+7.6','-20',X,f'({Y})+({k})*20')
# Each top column angle:2M8x16, thread into matching HFS8 T-nut.
for sy in [-1,1]:
 for sx in [-1,1]:
  for kind,pos in [('motor','motor_post_x'),('guide','roller_station')]:
   X=f'({sx})*({pos})';Y=f'({sy})*frame_half_y'
   bolt(f'B09_Angle_side_{kind}_{sx}_{sy}','YZ',f'({X})+26.6','-16',Y,'frame_top_bottom_z-20')
   bolt(f'B10_Angle_bottom_{kind}_{sx}_{sy}','XY','frame_top_bottom_z-6.6','16',f'({X})+40',Y)
# Low bridging beams shorten the flexible guide-post cantilever.
for sy in [-1,1]:
 Y=f'({sy})*frame_half_y'
 for sx in [-1,1]:
  xlo='motor_post_x+profile_size/2' if sx>0 else '-roller_station+profile_size/2'
  profile(f'F06_Low_bridge_{sx}_{sy}','YZ',xlo,'roller_station-motor_post_x-profile_size',Y,'brace_beam_z+profile_size/2')
  for endpoint,pos,lo,hi,holes in [('motor','motor_post_x','motor_post_x-20','motor_post_x+75',['motor_post_x+35','motor_post_x+55']),('guide','roller_station','roller_station-75','roller_station+20',['roller_station-55','roller_station-35'])]:
   x0=f'({sx})*({lo if sx>0 else hi})';x1=f'({sx})*({hi if sx>0 else lo})'
   yhi='frame_half_y+profile_size/2+6' if sy>0 else '-frame_half_y-profile_size/2'
   points=[(f'({sx})*({h})','brace_beam_z+20','beam') for h in holes]+[(f'({sx})*({pos})','brace_beam_z+45','post'),(f'({sx})*({pos})','brace_beam_z+65','post')]
   cuts=[circ('XZ',f'-({yhi})-1','8',x,z,'4.5') for x,z,kind in points]
   part(f'F07_Low_gusset_{endpoint}_{sx}_{sy}','fabricated',[rect('XZ',neg(yhi),'6',x0,'brace_beam_z',x1,'brace_beam_z+80')],cuts,note='S3556mm low bridge joint plate;4M8 to actual outer T-slot centre lines.',explode=(0,sy*80,20))
   for i,(x,z,kind) in enumerate(points):
    off='-frame_half_y-profile_size/2-9.6' if sy>0 else 'frame_half_y+profile_size/2+9.6'
    bolt(f'B11_Brace_{endpoint}_{sx}_{sy}_{i}','XZ',off,('20' if sy>0 else '-20'),x,z)
    washer(f'WS_Brace_shim_{endpoint}_{sx}_{sy}_{i}','XZ',f'({off})+({1 if sy>0 else -1})*1.6',('2' if sy>0 else '-2'),x,z,16,8.4)
    yl='frame_half_y+profile_size/2-11' if sy>0 else '-frame_half_y-profile_size/2+5'
    dx,dz=(8.5,5) if kind=='beam' else (5,8.5)
    part(f'TNB_Brace_{endpoint}_{sx}_{sy}_{i}','bolt',[box(f'({x})-{dx}',yl,f'({z})-{dz}',f'({x})+{dx}',f'({yl})+6',f'({z})+{dz}')],[circ('XZ',f'-({yl})-7','8',x,z,'3.4')],category='purchase',material='HFS8M8Tnut envelope; exact supplier CAD needed',bom=False)
# Hardened washers at the entry face of every modeled socket cap screw, except the jack.
for item in list(manifest):
 if not item['name'].startswith(('B01','B03','B04','B05','B08','B09','B10','B11')):continue
 op=item['adds'][0];d=2*V(op['radius']);sgn=1 if V(op['length'])>0 else -1
 u,v=op['center'];wth=1.6
 washer('W_'+item['name'],op['plane'],op['offset'],S(sgn*wth),u,v,16 if d==8 else 12,8.4 if d==8 else 6.4)
 # extra T-nuts for top splice and angles
 if item['name'].startswith(('B08','B09','B10')):
  if item['name'].startswith('B09'):
   a=f"({op['offset']})-17.6";start=a
   adds=[rect('YZ',start,'6',f'({u})-5',f'({v})-8.5',f'({u})+5',f'({v})+8.5')]
   cuts=[circ('YZ',f'({start})-1','8',u,v,'3.4')]
  else:
   start='frame_top_bottom_z+profile_size-11' if item['name'].startswith('B08') else 'frame_top_bottom_z+3'
   adds=[rect('XY',start,'6',f'({u})-8.5',f'({v})-5',f'({u})+8.5',f'({v})+5')]
   cuts=[circ('XY',f'({start})-1','8',u,v,'3.4')]
  part('TN_'+item['name'],'bolt',adds,cuts,category='purchase',material='HFS8 series M8 Tnut envelope',bom=False)
for sx in [-1,1]:
 for sy in [-1,1]:
  X=f'({sx})*roller_station';Y=f'({sy})*(rail_head_width/2+roller_d/2+guide_gap-rail_side_slope*(roller_center_z+rail_side_ref_depth)+rail_side_slope**2*roller_width**2/(16*roller_crown))'
  for k,z in enumerate(['roller_center_z-roller_width/2-10-yoke_arm_t-12-2.5','roller_center_z+roller_width/2+10+yoke_arm_t+12']):
   washer(f'W12_Spindle_{sx}_{sy}_{k}','XY',z,'2.5',X,Y,24,13)
# Compact brake and cable RESERVED envelopes are not solids in final CAD; report and drawings only.
# Create independent machining STEP files and a generic expression manifest used by Fusion.
for m in manifest:
 if m['category']=='custom' and m['name'].startswith(('A01','A02','G02','G04','G06','G07','G08','G09')):
  cq.exporters.export(shapes[m['name']],str(ROOT/'parts'/(m['name']+'.step')))
(ROOT/'model_manifest.json').write_text(json.dumps(manifest,indent=2))
# Export solid-valid assembly and exploded assembly, named components.
assy=cq.Assembly(name='QS212_StraightRail_Module_DRAFT_R01'); exploded=cq.Assembly(name='QS212_Module_Exploded_DRAFT')
for m in manifest:
 name=m['name'];sh=shapes[name];co=cq.Color(*COL[m['group']])
 assy.add(sh,name=name,color=co)
 if m['group']!='rail': exploded.add(sh,name=name,color=co,loc=cq.Location(cq.Vector(*m['explode'])))
assy.export(str(ROOT/'cad/Module_assembly.step'));exploded.export(str(ROOT/'cad/Module_exploded.step'))
# Detailed input wheel assembly kept as reference, aligned to X travel/Y axle/Z vertical.
refsrc=ROOT/'reference/QS212_1200W_tire_reference.step'
if not refsrc.exists():shutil.copy2('/workspace/attachments/1710cb33-e08d-4adb-af26-0b95ada63bd3/QS212_1200W_tire_reference.step',refsrc)
ref=cq.importers.importStep(str(refsrc))
assert ref.val().isValid()
refsh=ref.val().rotate((0,0,0),(0,0,1),90).translate((0,0,p['tire_od']/2))
cq.exporters.export(refsh,str(ROOT/'cad/Input_wheel_aligned_REFERENCE_ONLY.step'))
(ROOT/'reports/component_bounds.json').write_text(json.dumps([{**{k:m[k] for k in ['name','category','group','material']},'bbox':[shapes[m['name']].BoundingBox().xmin,shapes[m['name']].BoundingBox().ymin,shapes[m['name']].BoundingBox().zmin,shapes[m['name']].BoundingBox().xmax,shapes[m['name']].BoundingBox().ymax,shapes[m['name']].BoundingBox().zmax],'volume_mm3':shapes[m['name']].Volume()} for m in manifest],indent=2))
# Actual CAD collision checks excluding documented intended assembly interfaces.
results=[]
def chk(a,b,kind='clearance'):
 try:
  inter=shapes[a].intersect(shapes[b]);vol=inter.Volume();dist=shapes[a].distance(shapes[b]);ok=vol<1e-4
  results.append(dict(a=a,b=b,type=kind,intersection_mm3=round(vol,6),distance_mm=round(dist,4),pass_no_overlap=ok))
 except Exception as e:results.append(dict(a=a,b=b,error=str(e)))
for m in manifest:
 n=m['name']
 if n.startswith(('G01','G02','G07','G08','G09','F02','F06','F07','A01','A02')):chk('M01_Rotating_tire_ASSUMED',n)
 if n.startswith(('G01','G07','G08','G09','F02','F06','F07','A01','A02')):chk('R00_Rail_KRS60K_ENVELOPE_SITE_UNCONFIRMED',n)
 if n.startswith('G06'):chk(n,'R00_Rail_KRS60K_ENVELOPE_SITE_UNCONFIRMED')
# Wheel-tire own detailed imported model used for true clearance to proposed fixed structure, excluding axle supports.
refsols=ref.solids().vals();source_tire=max(refsols,key=lambda s:s.BoundingBox().ylen)
detailed_tire=source_tire.rotate((0,0,0),(0,0,1),90).translate((0,0,p['tire_od']/2))
for m in manifest:
 if m['name'].startswith(('G07','G08','F01','F02','F03','F06','F07','A01','A02')):
  sh=shapes[m['name']]; iv=detailed_tire.intersect(sh).Volume()
  results.append(dict(a='Imported_tire_REFERENCE',b=m['name'],intersection_mm3=round(iv,6),distance_mm=round(detailed_tire.distance(sh),4),pass_no_overlap=iv<1e-4))
(ROOT/'reports/interference_checks.json').write_text(json.dumps(results,indent=2))
# STEP roundtrip check.
rt=cq.importers.importStep(str(ROOT/'cad/Module_assembly.step'))
report={'shape_valid':rt.val().isValid(),'part_count':len(manifest),'reimported_solids':len(rt.solids().vals()),'interference_checks':len(results),'overlaps':[r for r in results if r.get('pass_no_overlap') is False], 'source_step_sha256':hashlib.sha256(refsrc.read_bytes()).hexdigest(),'STL_status':'NOT_READ:32MiB transfer limit and Thingiverse403; user supplied rail PDF as fallback','rail_source':'KRS TR0001-15(R) appendix3 60K, site rail unconfirmed; fillets approximate'}
(ROOT/'reports/validation.json').write_text(json.dumps(report,indent=2));print(json.dumps(report,indent=2))
# Machine-readable bill of materials, per physical component, plus separate standardized fastener schedule.
with (ROOT/'BOM_parts.csv').open('w',newline='') as f:
 wr=csv.writer(f);wr.writerow(['part_name','category','material_or_purchase_family','quantity','note'])
 for m in manifest:
  if m['bom']:wr.writerow([m['name'],m['category'],m['material'],1,m['note']])
# Persist source geometry for orthographic & technical views without huge STEP import.
cq.exporters.export(cq.Compound.makeCompound([s for n,s in shapes.items() if not n.startswith('R00')]),str(ROOT/'cad/Module_no_rail.step'))
print('Done',ROOT)
