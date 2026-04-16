# Telegram Report Pipeline Image Design

## Goal

텔레그램 리포트 파이프라인을 한 장의 이미지로 쉽게 설명한다. 이미지는 텔레그램/지메일에서 들어온 리포트를 수집하고, 이를 처리한 뒤, sector/macro agent가 요약·분석하고, 마지막으로 summary와 insight를 내보내는 end-to-end 흐름을 3초 안에 이해할 수 있도록 보여줘야 한다.

## Usage Context

이 이미지는 소셜/채팅 공유용으로 사용한다. 따라서 문서형 상세 아키텍처보다는 빠른 이해, 깔끔한 시선 흐름, 낮은 정보 밀도가 더 중요하다.

## Approved Constraints

- 톤: 발표용 인포그래픽 + 시스템 아키텍처 다이어그램의 하이브리드
- 언어: 영어
- 포커스: ingestion부터 analysis까지 균형 있게 보여주는 end-to-end flow
- 비율: 1:1 square
- 아이콘: Telegram/Gmail 로고를 직접 쓰지 않고 generic chat/mail icon으로 순화
- 밀도: 너무 기술 문서처럼 복잡하지 않게, 한눈에 이해 가능해야 함

## Design Direction

추천안으로 선택된 방향은 **hybrid hero pipeline**이다.

구성 원칙은 다음과 같다.

1. 왼쪽에서 데이터 소스가 들어오고,
2. 중앙에서 report pipeline이 핵심 허브로 작동하며,
3. 오른쪽에서 sector/macro agent가 분석을 수행하고,
4. 하단 또는 마지막 노드에서 summaries와 insights가 정리되는 흐름으로 설계한다.

이 방식은 linear pipeline보다 시각적으로 덜 밋밋하고, layered system diagram보다 소셜 공유용 이미지에 더 적합하다.

## Layout

### Left: Sources

두 개의 시작 노드를 둔다.

- `Chat Reports`
- `Email Reports`

각 노드는 다음 원칙을 따른다.

- chat bubble / envelope 같은 generic icon 사용
- 브랜드 연상은 가능하되 실제 로고처럼 보이지 않게 단순화
- 입력점이라는 인식이 즉시 되도록 중앙 허브를 향한 화살표 배치

### Center: Collection and Processing Hub

중앙은 파이프라인의 핵심이다. 아래 단계를 2~4개의 연결 블록으로 단순화해 표현한다.

- `Report Collection`
- `Raw Reports / PDFs`
- `Parsing & Extraction`
- `Chunking & Key Page Selection`

중앙 허브는 다음 인상을 줘야 한다.

- 리포트를 그냥 저장만 하는 것이 아니라, 분석 가능한 형태로 준비하는 구간
- 문서를 parse하고, 핵심 페이지를 고르고, 분석 입력을 정리하는 준비 단계
- 이미지 전체에서 가장 시각적 무게가 큰 영역

### Right: Analyst Lanes

오른쪽에는 두 개의 agent lane을 병렬로 둔다.

- `Sector Agent`
- `Macro Agent`

표현 원칙:

- 사람 아이콘보다 AI/analysis node에 가까운 추상적 agent 카드 또는 node 사용
- 중앙 허브에서 각각 입력을 받는 구조를 명확히 표시
- 두 agent가 서로 다른 관점으로 같은 report set을 해석한다는 느낌 유지

### Bottom / Final Output

마지막 결과는 간단하고 명확하게 보여준다.

- `Summaries`
- `Insights / Signals`

출력은 agent 결과가 합쳐져 사용자에게 전달되는 마지막 단계로 보이게 한다. 필요하면 작은 보조 카피로 다음 흐름을 넣는다.

- `Collect → Extract → Analyze → Deliver`

## Information Hierarchy

정보 우선순위는 아래 순서를 따른다.

1. source input
2. report processing hub
3. sector/macro analysis
4. summaries and insights

즉, 사용자가 이미지를 봤을 때 가장 먼저 “어디서 들어와서”, 그다음 “중간에서 어떻게 준비되고”, 마지막으로 “누가 분석하고 무엇이 나오는지”를 이해해야 한다.

## Visual Language

### Style

- clean, modern, presentation-friendly infographic
- architecture diagram의 구조감은 유지하되 문서형 복잡도는 피함
- 카드/노드/연결선 기반 구성

### Palette

차분한 AI/research 느낌을 위해 다음 계열을 사용한다.

- blue
- slate
- teal

권장 처리:

- source는 밝고 단순하게
- processing hub는 가장 강조된 채도/명도 대비로 배치
- sector/macro lane은 같은 계열의 변형 색으로 구분
- output은 정리된 결과 느낌이 나도록 안정적인 tone 사용

### Density and Readability

- 모바일 메신저 미리보기에서도 읽혀야 하므로 텍스트는 짧게 유지
- 각 노드는 1~4단어 수준으로 제한
- 한 이미지 안에 설명 문장보다 구조와 방향성이 먼저 읽히게 설계

## On-image Copy

필수 텍스트는 아래 범위 안에서 사용한다.

- `Chat Reports`
- `Email Reports`
- `Report Collection`
- `Raw Reports / PDFs`
- `Parsing & Extraction`
- `Chunking & Key Page Selection`
- `Sector Agent`
- `Macro Agent`
- `Summaries`
- `Insights / Signals`

선택적 보조 카피:

- `Collect → Extract → Analyze → Deliver`

텍스트는 반드시 짧고 선명해야 하며, 브랜드 설명이나 긴 문장형 캡션은 넣지 않는다.

## Composition Guidance

- 전체 시선 흐름은 좌상단/좌측에서 시작해 우측과 하단 출력으로 자연스럽게 이동해야 한다.
- 중앙 허브가 가장 큰 덩어리로 보이게 하여 파이프라인의 핵심이 “processing before analysis”라는 점을 강조한다.
- sector/macro agent는 병렬 노드로 배치해 서로 다른 분석 관점을 암시한다.
- 결과 영역은 clutter 없이 마무리되어, 이미지 전체가 “pipeline complete”처럼 느껴져야 한다.

## What This Image Must Communicate

이 이미지는 아래 메시지를 정확히 전달해야 한다.

- Reports come in from chat and email.
- The system collects and prepares them as raw PDFs/reports.
- The pipeline extracts text and selects key pages/chunks.
- Sector and macro agents analyze the prepared inputs.
- The user receives concise summaries and actionable insights.

## What To Avoid

- 실제 Telegram/Gmail 브랜드 로고처럼 보이는 요소
- 데이터베이스, 벡터DB, OCR, graph, wiki 등 부가 시스템을 과하게 넣어 복잡하게 만드는 것
- 지나치게 엔지니어링 문서 같은 복잡한 레이어 표현
- 텍스트가 많아져서 소셜 이미지가 아닌 설명 슬라이드처럼 보이는 구성
- agent 영역이 processing hub보다 더 커져서 전체 파이프라인보다 agent 소개 이미지처럼 보이는 것

## Implementation Note

구현 단계에서는 이 spec을 기준으로 square 1:1 비율의 단일 이미지 시안을 생성한다. 결과물은 social/chat share용 preview-first asset이어야 하며, 첫 시안의 평가 기준은 다음과 같다.

- 3초 안에 전체 흐름이 이해되는가
- 텍스트 없이도 대략적인 pipeline 구조가 읽히는가
- 영어 라벨이 과하지 않고 잘 정리되어 있는가
- generic icon 처리로 브랜드 이슈 없이 source 의미가 전달되는가
