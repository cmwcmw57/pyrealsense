# Fusion 360 편집 방법

가장 확실한 열기: cad/Module_assembly.step을 Fusion에서 업로드/열기. 부품별 B-rep로 편집할 수 있지만 STEP에는 피처 이력이 없습니다.

네이티브 파라메트릭 생성: Utilities → Scripts and Add-ins → Scripts에서 QS212_Rail_Module 폴더를 추가한 뒤 실행합니다. 스크립트 옆 JSON 2개를 유지하세요. 생성 후 .f3d로 저장합니다. 기본적으로 표준 체결품 일부는 생략하여 생성 시간을 줄입니다.

이 생성기는 Python 구문 검사만 완료했으며 실제 Fusion API 실행은 검증하지 못했습니다. 따라서 검증된 .f3d 파일을 제공한다고 주장하지 않습니다. 실패 시 cad의 STEP을 사용하세요. 검증된 파라메트릭 원본은 build_module.py와 parameters.json이며 CadQuery에서 실행했습니다. 큰 치수 변경/슬롯 방향 변경은 재생성이 필요합니다.
