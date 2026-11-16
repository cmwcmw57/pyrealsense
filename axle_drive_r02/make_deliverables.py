from pathlib import Path
import csv,json,html,re,py_compile
from playwright.sync_api import sync_playwright
R=Path(__file__).resolve().parent
items=[['M01','purchase','QS12070H non-geared 72V2kW Hall motor',1,'OEM output/mount drawing and14T428 interface approval required'],['E01','purchase','Matched EM100-4SP controller',1,'Exact firmware/Hall angle/CAN command/reverse rating pending'],['D01','purchase','42814T motor sprocket',1,'Order matched OEM shaft;420/428 not interchangeable'],['D02','purchase','42842T sprocket bored/keyed D30',1,'Hub/locking design pending'],['D03','purchase','42816T sprocket bored/keyed D30',1,'Hub/locking design pending'],['D04','purchase','42840T axle sprocket bored/keyed D40',1,'Taper bush or keyed hub locking pending'],['D05','purchase','428 roller chain70links',2,'Exact length/tensioner/guard pending'],['A01','custom','C45D40 live axle L1800',2,'Fits/shoulders/key12x8/retention/fatigue pending'],['A02','custom','C45D30 jackshaft L370',1,'Key8x7 candidate; fit/retention pending'],['W01','custom','RailwheelD300 tread90 flangeD330x8',4,'PROVISIONAL cone1:20; certified profile/material pending'],['B01','purchase','UCP20840mm pillow block',4,'Boundary dimensions verified; load and axial fixation pending'],['B02','purchase','UCP20630mm pillow block',2,'Check chosen supplier CAD'],['G01','custom','Crowned PU guide50x28',16,'Load/speed/heat and6002x2 support to finalize'],['G02','purchase','6002 sealed15x32x9 guide bearings',32,'BOM allowance; not fully modeled'],['G03','custom','D15 smooth spindle with threaded ends',16,'Threads/end nuts/spacers not fully modeled'],['J01','purchase_pending','Yaw bearing/housing assembly D40 interface',2,'Envelope only; moment capacity/race clamping must be selected'],['J02','custom','Pitch pin D30, bushes, retained fork assembly',2,'Axial retention and stops pending'],['J03','custom','Front roll pin D30, bushes, retained fork',1,'Rear roll fixed; stops/damping pending'],['F01','cut_purchase','RHS80x40x3 and40x40x3',1,'Per model cut lengths; weld detail pending'],['P01','custom','S355 plate components',1,'Per-part STEP/BOM; no released fabrication tolerances'],['BR01','purchase_pending','Mechanical disc brake on each axle',2,'CAD200mm keep-out only; stopping/parking ratings unselected'],['H01','purchase','M14 bearing mounting bolts/nuts/washers',12,'8main+4jack; exact lengths, grade and torque pending'],['H02','purchase_pending','Joint bolts/bushes/spacers/retaining nuts',1,'Complete hardware schedule not designed']]
with (R/'BOM_purchase_and_custom.csv').open('w',newline='') as f:w=csv.writer(f);w.writerow(['id','category','description','qty','status']);w.writerows(items)
with (R/'Joint_axes.csv').open('w',newline='') as f:
 w=csv.writer(f);w.writerow(['joint','axis','global_center_mm','allowed_body_relation','status'])
 for x,b in [(-500,'rear'),(500,'front')]:
  w.writerow([b+'_yaw','Z',f'{x},0,400','whole bogie to pitch carrier','bearing housing not finalized'])
  w.writerow([b+'_pitch','Y',f'{x},0,490','yaw carrier to fork','pin retention/bush fit pending'])
 w.writerow(['front_roll','X','500,0,575','front pitch fork to chassis','pin retention/stops pending'])
(R/'README_KO.md').write_text('''# 차축 구동 설계 R02\n\n**모터선정 + 선회/피치/롤 구조를 배치한 파라메트릭 설계 초안입니다. 제작 승인·주행 검증 완료 모델이 아닙니다.**\n\n1. `cad/AxleDrive_Straight.step`을 Fusion에서 열어 전체 구조를 확인합니다.\n2. `cad/AxleDrive_Curve_R50.step`, `AxleDrive_Articulation_DEMO.step`으로 관절 자세를 비교합니다. 레일 접촉을 풀어 얻은 동역학 결과는 아닙니다.\n3. `cad/Joint_mechanisms.step`, `Drive_train.step`은 관절/동력 전달부만 분리한 보기입니다.\n4. `drawings/Assembly_and_joint_views.pdf`에 실제 모델의 등각·평면·측면·선회·요동·상세 보기가 있습니다.\n5. `DESIGN_REVIEW_KO.pdf`에 모터 구매 근거·확인/가정 치수·계산·하중 전달·남은 보류점을 정리했습니다. `BOM_purchase_and_custom.csv`와 `Joint_axes.csv`를 함께 보세요.\n\n**선정안:** 비감속형 QS12070H72V2kW 1개,14→42/16→40 두 단계428체인,총7.5:1,뒤 공통 차축 구동. 앞 공통 차축은 비구동. 양측 가이드는 총16개입니다.\n\n**편집:** STEP은 부품별 B-rep이며 원래 피처 이력/Fusion 조인트 객체가 없습니다. 검증한 파라메트릭 원본은 `build_axle_drive.py`와 `parameters.json`입니다. CadQuery로 재생성합니다. 실제 `.f3d`는 생성하지 않았습니다.\n\n설치: `pip install cadquery==2.7.0 numpy matplotlib playwright`. `python build_axle_drive.py`, `python engineering_checks.py`, `python render_drawings.py` 순서로 실행합니다. FreeCAD검사/상세 분리 스크립트는 FreeCAD Python 환경이 별도로 필요합니다. 보고서PDF 생성에는 Chromium과 Playwright가 사용됐습니다.\n\n변수로 지정한 치수만 파라미터 변경을 지원합니다. 베어링·모터 장착 인터페이스/관절 지지 높이의 일부는 아직 코드상 상수이므로 해당 부분 변경 시 소스도 수정하고 재검사해야 합니다. 큰 변경을 자동 검증한다고 주장하지 않습니다.\n\n좌우 같은RPM을 유지하므로 선회 관절을 넣어도 커브의 좌우 거리차로 인한 미끄럼이 남습니다. 실제 최소반경·구배·수직곡선·캔트와 마찰/모터부하곡선이 필요합니다. 원추 답면만으로 해결됐다고 볼 수 없습니다.\n''')
(R/'requirements.txt').write_text('cadquery==2.7.0\nnumpy\nmatplotlib\nplaywright\n')
# lightweight Markdown-to-HTML, preserving tables and source URLs.
def inline(s):
 s=html.escape(s);s=re.sub(r'\*\*(.*?)\*\*',r'<b>\1</b>',s);s=re.sub(r'`([^`]+)`',r'<code>\1</code>',s)
 s=re.sub(r'(https://[^\s<]+)',r'<a href="\1">\1</a>',s);return s
lines=(R/'DESIGN_REVIEW_KO.md').read_text().splitlines();out=[];intable=False
for s in lines:
 if s.startswith('|'):
  if re.match(r'^\|[\s:|\-]+$',s):continue
  if not intable:out.append('<table>');intable=True
  out.append('<tr>'+''.join('<td>'+inline(t.strip())+'</td>' for t in s.strip('|').split('|'))+'</tr>');continue
 if intable:out.append('</table>');intable=False
 if s.startswith('#'):n=min(4,len(s)-len(s.lstrip('#')));out.append(f'<h{n}>'+inline(s.lstrip('#').strip())+f'</h{n}>')
 elif s:out.append('<p>'+inline(s)+'</p>')
if intable:out.append('</table>')
body='<html><meta charset="utf-8"><style>body{font-family:"Noto Sans CJK KR",sans-serif;font-size:9pt;line-height:1.6}h1{font-size:19pt}h2{font-size:13pt;page-break-after:avoid}p{overflow-wrap:anywhere}table{border-collapse:collapse;width:100%;font-size:8pt}td{border:1px solid #aaa;padding:4px}tr{break-inside:avoid}a{word-break:break-all} @page{size:A4;margin:16mm}</style>'+''.join(out)+'</html>'
(R/'DESIGN_REVIEW_KO.html').write_text(body)
with sync_playwright() as pw:
 b=pw.chromium.launch(executable_path='/usr/bin/chromium',headless=True,args=['--no-sandbox']);pg=b.new_page();pg.set_content(body);pg.pdf(path=str(R/'DESIGN_REVIEW_KO.pdf'),format='A4',print_background=True);b.close()
for f in R.glob('*.py'):py_compile.compile(str(f),doraise=True)
print('Reports, BOM, joint axes and syntax checks complete')
