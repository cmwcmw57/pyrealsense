# QS212 레일 모듈 R01 — 수정 가능한 설계 초안

모터 바퀴 1개, 전후 각 2개씩 수직축 측면 가이드 롤러 4개, 양측 축 고정판과 프로파일 프레임입니다.

- `cad/Module_assembly.step`: 전체 조립, Fusion에서 열기
- `cad/Module_no_rail.step`: 레일 제외 조립
- `cad/Module_exploded.step`: 분해 배치
- `drawings/Assembly_views.pdf`: 실제 STEP 형상으로 만든 정면·측면·평면·분해도
- `drawings/Dimensioned_layout.pdf`, `Contact_detail.pdf`: 배치 치수와 접촉부
- `drawings/Machining_drafts.pdf`, `Turned_parts_drafts.pdf`, DXF/좌표 CSV: 가공 초안
- `BOM_consolidated.csv`, `FASTENER_CONNECTIONS.csv`: 부품표·체결표
- `DESIGN_REVIEW_KO.md`: 가정치, 하중, 조립 순서, 보류점
- `reports`: 실제 CAD 읽기/간섭 검사와 질량 예산
- `build_module.py` + `parameters.json`: 실행 검증한 파라메트릭 CadQuery 원본
- `fusion360/README_KO.md`: Fusion 네이티브 생성 스크립트 사용법과 검증 한계

**STL은 전송 용량 제한 및 Thingiverse 403으로 읽지 못했습니다. 사용자 후속 지시에 따라 첨부 레일 PDF의 60K 단면을 대체 기준으로 사용했습니다.** 원본 PDF는 공개 저장소에 재배포하지 않습니다. 입력 모터 STEP은 OEM 정밀 도면이 아닌 추정 참고 모델입니다.

총중량 200kg 조건을 반영했으나 이 초안은 탑승/제작 승인 모델이 아닙니다. 현장 레일, 축 치수, 강도·제동·안티리프트·질량 검증이 필요합니다. 측면 가이드는 수직 들림을 구속하지 않습니다. 곡선·분기기는 범위 밖입니다.

재생성: Python 3에서 `pip install cadquery==2.7.0 numpy matplotlib ezdxf` 후 `python build_module.py`. 도면은 `python make_drawings.py`와 `python add_detail_drawings.py`. FreeCAD 검사는 별도 FreeCAD Python 환경이 필요합니다.
