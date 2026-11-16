from pathlib import Path
import sys,json
sys.path.append('/usr/lib/freecad/lib')
import FreeCAD,Part
r=Path(__file__).resolve().parent;s=Part.read(str(r/'Chassis_Rigid_4Wheel.step'));out={'application':'FreeCAD','version':'.'.join(FreeCAD.Version()[:3]),'valid':s.isValid(),'solids':len(s.Solids),'bounds_mm':[s.BoundBox.XLength,s.BoundBox.YLength,s.BoundBox.ZLength],'note':'Reopen and topology check only, not assembly interference or dynamics'}
(r/'CAD_reopen_validation.json').write_text(json.dumps(out,indent=2));print(out);assert out['valid']
