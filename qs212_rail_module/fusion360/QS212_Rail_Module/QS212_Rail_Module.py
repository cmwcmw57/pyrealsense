"""Fusion360 native parametric builder. Run in Fusion > Utilities > Scripts and Add-ins.
Place this script and .manifest in the same folder. No external Python packages.
Creates native components, dimensioned sketches, extrusions and revolutions.
Changing user parameters drives supported dimensions. Large changes may need rerun.
Not executed in Fusion in the cloud; API runtime validation must be done locally.
"""
import adsk.core,adsk.fusion,traceback,json,math,re
from pathlib import Path

def run(context):
 app=adsk.core.Application.get();ui=app.userInterface
 try:
  base=Path(__file__).resolve().parent
  params=json.loads((base/'parameters.json').read_text());manifest=json.loads((base/'model_manifest.json').read_text())
  doc=app.documents.add(adsk.core.DocumentTypes.FusionDesignDocumentType)
  design=adsk.fusion.Design.cast(app.activeProduct);design.designType=adsk.fusion.DesignTypes.ParametricDesignType
  root=design.rootComponent;root.name='QS212_StraightRail_Module_DRAFT_R01'
  unitless={'rail_side_slope','total_mass_kg','max_wheel_fraction','dynamic_factor','guide_lateral_force_N','drive_torque_Nm'}
  for name,value in params.items():
   units='' if name in unitless else 'mm'
   design.userParameters.add(name,adsk.core.ValueInput.createByString(str(value)+(' mm' if units else '')),units,'INPUT MODEL / ASSUMPTION; see design report')
  env=dict(params,pi=math.pi,sqrt=math.sqrt,abs=abs,min=min,max=max,cos=math.cos,sin=math.sin)
  def num(e):return float(eval(str(e),{'__builtins__':{}},env))
  def expr(e):
   e=str(e)
   # Cosmetic hexagonal profiles: freeze angle evaluation, dimensions remain editable sketch dimensions.
   if 'cos(' in e or 'sin(' in e or 'sqrt(' in e:return str(num(e))+' mm'
   if not any(re.search(r'\b'+re.escape(k)+r'\b',e) for k in params):return str(num(e))+' mm'
   return e.replace('**','^')
  def val(e):return adsk.core.ValueInput.createByString(expr(e))
  def P(u,v):return adsk.core.Point3D.create(num(u)/10,num(v)/10,0)
  def anchor(sk,point,ex,ey):
   # Orthogonal construction chain provides signed coordinate constraints.
   x=num(ex);y=num(ey); origin=sk.originPoint;cur=origin
   if abs(x)>1e-8:
    ln=sk.sketchCurves.sketchLines.addByTwoPoints(cur,adsk.core.Point3D.create(x/10,0,0));ln.isConstruction=True
    sk.geometricConstraints.addHorizontal(ln)
    dm=sk.sketchDimensions.addDistanceDimension(ln.startSketchPoint,ln.endSketchPoint,adsk.fusion.DimensionOrientations.AlignedDimensionOrientation,adsk.core.Point3D.create(x/20,-.5,0))
    dm.parameter.expression=expr(ex if x>0 else '-('+str(ex)+')');cur=ln.endSketchPoint
   if abs(y)>1e-8:
    ln=sk.sketchCurves.sketchLines.addByTwoPoints(cur,point);ln.isConstruction=True
    sk.geometricConstraints.addVertical(ln)
    dm=sk.sketchDimensions.addDistanceDimension(ln.startSketchPoint,ln.endSketchPoint,adsk.fusion.DimensionOrientations.AlignedDimensionOrientation,adsk.core.Point3D.create(x/10+.5,y/20,0))
    dm.parameter.expression=expr(ey if y>0 else '-('+str(ey)+')')
   else:
    sk.geometricConstraints.addCoincident(cur,point)
  def build_profile(comp,op,idx):
   rev=op['profile'].startswith('revolve')
   plane=op['plane'];off=op['offset']
   if rev:
    cx,cy,cz=op['center3'];plane='XZ' if op['profile']=='revolve_z' else 'XY';off='-('+cy+')' if plane=='XZ' else cz
   origin={'XY':comp.xYConstructionPlane,'XZ':comp.xZConstructionPlane,'YZ':comp.yZConstructionPlane}[plane]
   if abs(num(off))<1e-8:cp=origin
   else:
    pi=comp.constructionPlanes.createInput();pi.setByOffset(origin,val(off));cp=comp.constructionPlanes.add(pi)
   sk=comp.sketches.add(cp);sk.name='Profile_'+str(idx)
   sk.isComputeDeferred=True
   if op['profile']=='circle':
    u,v=op['center'];circle=sk.sketchCurves.sketchCircles.addByCenterRadius(P(u,v),num(op['radius'])/10)
    anchor(sk,circle.centerSketchPoint,u,v)
    dim=sk.sketchDimensions.addDiameterDimension(circle,adsk.core.Point3D.create((num(u)+num(op['radius']))/10,num(v)/10+.3,0));dim.parameter.expression='2*('+expr(op['radius'])+')'
    if 'inner_radius' in op:
     c=sk.sketchCurves.sketchCircles.addByCenterRadius(circle.centerSketchPoint.geometry,num(op['inner_radius'])/10)
     sk.geometricConstraints.addConcentric(circle,c)
     dim=sk.sketchDimensions.addDiameterDimension(c,adsk.core.Point3D.create(num(u)/10,num(v)/10-.3,0));dim.parameter.expression='2*('+expr(op['inner_radius'])+')'
   elif op['profile']=='slot':
    # Slot as two semicircles and parallel lines; profile dimensions are driven by input parameters.
    u,v=op['center'];w=op['width'];t=op['travel'];r=num(w)/20;h=num(t)/20;uu=num(u)/10;vv=num(v)/10
    arcs=sk.sketchCurves.sketchArcs
    top=arcs.addByCenterStartSweep(adsk.core.Point3D.create(uu,vv+h,0),adsk.core.Point3D.create(uu+r,vv+h,0),math.pi)
    bot=arcs.addByCenterStartSweep(adsk.core.Point3D.create(uu,vv-h,0),adsk.core.Point3D.create(uu-r,vv-h,0),math.pi)
    sk.sketchCurves.sketchLines.addByTwoPoints(top.endSketchPoint,bot.startSketchPoint)
    sk.sketchCurves.sketchLines.addByTwoPoints(bot.endSketchPoint,top.startSketchPoint)
    # Fix slot entities to the current generated values. Slot width/travel update by rerunning builder.
    for curve in [top,bot]:curve.isFixed=True
   else:
    points=op['points']
    if rev:
     points=[[f'({cx})+({a})',f'({cz})+({b})'] if plane=='XZ' else [f'({cx})+({a})',f'({cy})+({b})'] for a,b in points]
    lines=[]
    for j in range(len(points)):
     a=lines[-1].endSketchPoint if lines else P(*points[j]);b=lines[0].startSketchPoint if j==len(points)-1 else P(*points[(j+1)%len(points)])
     lines.append(sk.sketchCurves.sketchLines.addByTwoPoints(a,b))
    for j,line in enumerate(lines):anchor(sk,line.startSketchPoint,*points[j])
   axis=None
   if rev:
    # Revolution around vertical in local sketch: global Z for guide; global Y for tire.
    ux=cx
    vy=cz if plane=='XZ' else cy
    axis=sk.sketchCurves.sketchLines.addByTwoPoints(P(ux,f'({vy})-50'),P(ux,f'({vy})+50'));axis.isConstruction=True
    anchor(sk,axis.startSketchPoint,ux,f'({vy})-50');anchor(sk,axis.endSketchPoint,ux,f'({vy})+50')
   sk.isComputeDeferred=False
   profiles=adsk.core.ObjectCollection.create()
   # Annulus uses the profile with maximum loop count; disc interior must not be extruded.
   candidates=[sk.profiles.item(i) for i in range(sk.profiles.count)]
   if not candidates:raise RuntimeError('No closed profile: '+comp.name+' '+str(idx))
   if op['profile']=='circle' and 'inner_radius' in op:
    candidates=[max(candidates,key=lambda p:p.profileLoops.count)]
   for pr in candidates:profiles.add(pr)
   return sk,profiles,axis
  include_fasteners=False # Set True to build the standard fastener envelope components too.
  total=0
  for item in manifest:
   if not include_fasteners and (item['group']=='bolt' or item['name'].startswith('W_')):continue
   occ=root.occurrences.addNewComponent(adsk.core.Matrix3D.create());comp=occ.component;comp.name=item['name']
   for index,(op,cut) in enumerate([(o,False) for o in item['adds']]+[(o,True) for o in item['cuts']]):
    sk,profiles,axis=build_profile(comp,op,index)
    operation=adsk.fusion.FeatureOperations.CutFeatureOperation if cut else (adsk.fusion.FeatureOperations.JoinFeatureOperation if comp.bRepBodies.count else adsk.fusion.FeatureOperations.NewBodyFeatureOperation)
    if axis:
     inp=comp.features.revolveFeatures.createInput(profiles,axis,operation);inp.setAngleExtent(False,adsk.core.ValueInput.createByString('360 deg'));feat=comp.features.revolveFeatures.add(inp)
    else:
     inp=comp.features.extrudeFeatures.createInput(profiles,operation)
     # Negative distances deliberately indicate opposite normal for mounting bolts.
     distance=op['length'];sgn=adsk.fusion.ExtentDirections.PositiveExtentDirection if num(distance)>0 else adsk.fusion.ExtentDirections.NegativeExtentDirection
     de=adsk.fusion.DistanceExtentDefinition.create(val(distance if num(distance)>0 else '-('+distance+')'))
     inp.setOneSideExtent(de,sgn);feat=comp.features.extrudeFeatures.add(inp)
    feat.name=('Cut_' if cut else 'Add_')+str(index);sk.isVisible=False
   total+=1
   if total%5==0:adsk.doEvents()
  app.activeViewport.fit()
  ui.messageBox('QS212 module draft created. Save as .f3d in Fusion. Parameters: Modify > Change Parameters. Slotted profiles and cosmetic hex geometry use generated dimensions; rerun after changing slot parameters. See README for unverified assumptions. Native Fusion execution has not been verified in the cloud.')
 except:
  ui.messageBox('QS212 builder failed. STEP remains available.\n'+traceback.format_exc())
