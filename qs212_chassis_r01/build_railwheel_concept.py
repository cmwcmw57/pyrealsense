from pathlib import Path
import cadquery as cq,json,math
r=Path(__file__).resolve().parent;a=cq.Assembly(name='FLANGED_WHEELS_WITH_16_BILATERAL_GUIDES_CONCEPT');count=0
params={'wheelbase_mm':1000,'rail_centers_mm':1500,'wheel_tread_d_mm':300,'wheel_tread_width_mm':90,'flange_d_mm':330,'flange_thickness_mm':8,'guide_station_mm':150,'guide_od_mm':50,'guide_width_mm':28,'guide_y_offset_mm':58.06125,'status':'Concept only. No certified wheel profile or complete bolted structure. Separate rail-wheel drive required.'}
(r/'railwheel_concept_parameters.json').write_text(json.dumps(params,indent=2))
def add(n,s,c):
 global count
 assert s.isValid();a.add(s,name=n,color=cq.Color(*c));count+=1
steel=(.55,.58,.6);green=(.1,.55,.35);blue=(.2,.5,.7)
def box(n,x,y,z,l,w,h):add(n,cq.Workplane().box(l,w,h).translate((x,y,z)).val(),blue)
for x in [-500,500]:
 # Independent stub axles, not a rigid common drive axle.
 box(f'BOGIE_CROSS_{x}',x,0,350,80,1808,40)
 add(f'YAW_PIVOT_ENVELOPE_{x}',cq.Workplane('XY').center(x,0).circle(65).circle(20).extrude(35).translate((0,0,370)).val(),steel)
 for sy in [-1,1]:
  y=sy*750
  tread=cq.Workplane('XZ',origin=(x,y+45,150)).circle(150).circle(20).extrude(90).val()
  flange=cq.Workplane('XZ',origin=(x,y-45 if sy==1 else y+53,150)).circle(165).circle(20).extrude(8).val()
  add(f'RAILWHEEL_{x}_{sy}_PROFILE_UNCONFIRMED',tread.fuse(flange),steel)
  add(f'STUB_AXLE_{x}_{sy}',cq.Workplane('XZ',origin=(x,y+110,150)).circle(20).extrude(220).val(),steel)
  for dy in [-110,110]:box(f'BEARING_ENVELOPE_{x}_{sy}_{dy}',x,y+dy,150,90,35,90);box(f'WHEEL_SUPPORT_{x}_{sy}_{dy}',x,y+dy,270,40,40,160)
  for dx in [-150,150]:
   for side in [-1,1]:
    yy=y+side*params['guide_y_offset_mm'];xx=x+dx
    roll=cq.Workplane('XY',origin=(xx,yy,-34)).circle(25).circle(7.5).extrude(28).val();add(f'GUIDE_{x}_{sy}_{dx}_{side}',roll,green)
    add(f'GUIDE_SPINDLE_{x}_{sy}_{dx}_{side}',cq.Workplane('XY',origin=(xx,yy,-45)).circle(7.5).extrude(110).val(),steel)
    box(f'GUIDE_POST_{x}_{sy}_{dx}_{side}',xx,y+side*134,200,40,40,300)
    box(f'GUIDE_ARM_{x}_{sy}_{dx}_{side}',xx,(yy+y+side*134)/2,55,60,abs(y+side*134-yy)+40,10)
# main chassis envelope above turning interfaces; pivot bearing selection not done.
for yy in [-600,600]:box(f'CHASSIS_{yy}',0,yy,425,1600,40,40)
for xx in [-500,500]:box(f'CHASSIS_TRANSVERSE_{xx}',xx,0,425,80,1240,40)
a.save(str(r/'Railwheel_16Guides_CONCEPT.step'));print('Railwheel concept solids',count)
