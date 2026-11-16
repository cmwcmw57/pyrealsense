from pathlib import Path
import sys,json
sys.path.append('/usr/lib/freecad/lib')
import FreeCAD,Part
R=Path(__file__).resolve().parent
results=[]
for filename in ['Module_assembly.step','Module_exploded.step']:
 shape=Part.read(str(R/'cad'/filename))
 result={'file':filename,'freecad_version':'.'.join(FreeCAD.Version()[:3]),'null':shape.isNull(),'valid':shape.isValid(),'solid_count':len(shape.Solids)}
 results.append(result);print(result,flush=True)
(R/'reports/FreeCAD_read_validation.json').write_text(json.dumps(results,indent=2))
