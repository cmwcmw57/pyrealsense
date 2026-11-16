# 차축 구동 설계 R02

**모터선정 + 선회/피치/롤 구조를 배치한 파라메트릭 설계 초안입니다. 제작 승인·주행 검증 완료 모델이 아닙니다.**

1. `cad/AxleDrive_Straight.step`을 Fusion에서 열어 전체 구조를 확인합니다.
2. `cad/AxleDrive_Curve_R50.step`, `AxleDrive_Articulation_DEMO.step`으로 관절 자세를 비교합니다. 레일 접촉을 풀어 얻은 동역학 결과는 아닙니다.
3. `cad/Joint_mechanisms.step`, `Drive_train.step`은 관절/동력 전달부만 분리한 보기입니다.
4. `drawings/Assembly_and_joint_views.pdf`에 실제 모델의 등각·평면·측면·선회·요동·상세 보기가 있습니다.
5. `DESIGN_REVIEW_KO.pdf`에 모터 구매 근거·확인/가정 치수·계산·하중 전달·남은 보류점을 정리했습니다. `BOM_purchase_and_custom.csv`와 `Joint_axes.csv`를 함께 보세요.

**선정안:** 비감속형 QS12070H72V2kW 1개,14→42/16→40 두 단계428체인,총7.5:1,뒤 공통 차축 구동. 앞 공통 차축은 비구동. 양측 가이드는 총16개입니다.

**편집:** STEP은 부품별 B-rep이며 원래 피처 이력/Fusion 조인트 객체가 없습니다. 검증한 파라메트릭 원본은 `build_axle_drive.py`와 `parameters.json`입니다. CadQuery로 재생성합니다. 실제 `.f3d`는 생성하지 않았습니다.

설치: `pip install cadquery==2.7.0 numpy matplotlib playwright`. `python build_axle_drive.py`, `python engineering_checks.py`, `python render_drawings.py` 순서로 실행합니다. FreeCAD검사 스크립트는 FreeCAD Python 환경이 별도로 필요합니다. 상세 분리는 CadQuery로 실행합니다. 보고서PDF 생성에는 Chromium과 Playwright가 사용됐습니다.

변수로 지정한 치수만 파라미터 변경을 지원합니다. 베어링·모터 장착 인터페이스/관절 지지 높이의 일부는 아직 코드상 상수이므로 해당 부분 변경 시 소스도 수정하고 재검사해야 합니다. 큰 변경을 자동 검증한다고 주장하지 않습니다.

좌우 같은RPM을 유지하므로 선회 관절을 넣어도 커브의 좌우 거리차로 인한 미끄럼이 남습니다. 실제 최소반경·구배·수직곡선·캔트와 마찰/모터부하곡선이 필요합니다. 원추 답면만으로 해결됐다고 볼 수 없습니다.
