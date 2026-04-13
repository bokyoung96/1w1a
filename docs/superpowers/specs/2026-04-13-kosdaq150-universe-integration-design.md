# KOSDAQ150 Universe Integration Design

## Goal

`raw/ksdq`에 들어온 코스닥150 데이터 패밀리를 1w1a의 ingest, load, backtest, reporting, dashboard 실행 흐름에 자연스럽게 통합한다. 사용자는 CLI와 Python API 양쪽에서 `kosdaq150` 유니버스를 1급 개념으로 선택할 수 있어야 하며, 기존 `K200` 중심 실행 경로는 깨지지 않아야 한다.

## Scope

이번 설계는 아래 범위를 다룬다.

- `qw_ksdq_*` dataset id와 catalog 등록
- 유니버스 개념을 표현하는 dataclass/registry 추가
- `run.py`와 `BacktestRunner`에서 유니버스 선택 지원
- `LoadRequest`와 Python API에서 유니버스 선택 지원
- `kosdaq150` 기본 벤치마크를 `qw_BM` 기반 코스닥150으로 설정
- dashboard preset과 저장 run config에 `universe_id` 반영
- 기존 `use_k200` 기반 실행 경로와의 하위 호환 유지

이번 설계는 아래 범위를 의도적으로 제외한다.

- 전략 로직 자체의 변경
- 리포트 템플릿의 대규모 개편
- 복수 유니버스를 동시에 섞는 멀티-유니버스 포트폴리오 엔진

## Current State

현재 코드베이스는 `DatasetId`와 `DataCatalog`를 중심으로 parquet ingest/load를 수행한다. `LoadRequest.universe`와 `MarketData.universe`는 이미 존재해서 전략과 엔진이 불리언 마스크를 소비할 수 있지만, 이 값은 호출자가 직접 `DataFrame`으로 만들어 넣어야 한다.

현재 실행 경로는 사실상 `K200` 플래그 중심이다.

- `RunConfig.use_k200: bool = True`
- `BacktestRunner`가 `qw_k200_yn`을 조건부로 로드
- `market.universe`를 `k200_yn` frame에서 생성

이 구조는 코스닥150 같은 별도 데이터 패밀리를 명시적으로 표현하지 못한다. 또한 dataset 사전과 실행 가능한 유니버스 개념이 분리되어 있지 않아 확장성이 제한된다.

## Data Inventory

`raw/ksdq`에는 코스닥150 전용 데이터 패밀리가 들어 있다.

- `qw_ksdq_adj_c.csv`
- `qw_ksdq_adj_o.csv`
- `qw_ksdq_adj_h.csv`
- `qw_ksdq_adj_l.csv`
- `qw_ksdq_v.csv`
- `qw_ksdq_mkcap.csv`
- `qw_ksdq_mktcap_flt.csv`
- `qw_ksdq_wics_sec_big.csv`
- `qw_ksdq150_yn.csv`

파일 형식은 기존 raw CSV와 유사하다.

- 첫 열은 `Unnamed: 0` 형태의 날짜 열
- 행은 일자
- 열은 종목 코드
- 가격, 시총, 섹터, membership 여부가 각각 별도 파일로 제공됨

따라서 현재 normalize/ingest 파이프라인을 재사용할 수 있다.

## Design Summary

핵심 설계는 두 계층으로 나눈다.

1. 저수준 dataset 계층
`DatasetId`와 `DataCatalog`는 파일 단위 dataset 사전으로 유지한다. 여기에 `qw_ksdq_*` 패밀리를 별도 dataset id로 추가한다.

2. 고수준 universe 계층
새 `UniverseSpec` dataclass와 `UniverseRegistry`가 “어떤 dataset들을 어떤 유니버스로 묶어 실행할지”를 정의한다. `kosdaq150`는 이 계층에서 관리한다.

이 분리를 통해 다음을 만족한다.

- dataset 등록은 파일 중심으로 단순하게 유지
- backtest 실행은 `universe_id`라는 의미 있는 추상화로 제어
- 이후 `kospi200`, `krx300`, 기타 custom universe 추가가 쉬움
- dashboard preset과 CLI 편의 기능은 universe registry를 참조하되 코어 타입에 과도한 책임을 밀어넣지 않음

## Architecture

### Dataset Layer

`DatasetId`에 코스닥150 전용 id를 추가한다.

- `QW_KSDQ_ADJ_C`
- `QW_KSDQ_ADJ_O`
- `QW_KSDQ_ADJ_H`
- `QW_KSDQ_ADJ_L`
- `QW_KSDQ_V`
- `QW_KSDQ_MKCAP`
- `QW_KSDQ_MKTCAP_FLT`
- `QW_KSDQ_WICS_SEC_BIG`
- `QW_KSDQ150_YN`

`DataCatalog.default()`는 위 dataset들을 기존 dataset과 동일한 방식으로 등록한다. 그룹과 의미는 기존 패턴을 따른다.

- 가격류: `DatasetGroup.PRICE`
- membership flag: `DatasetGroup.FLAG`
- 섹터: `DatasetGroup.META`

`DataLoader.FRAME_KEYS`에도 코스닥150 전용 semantic key 매핑을 추가한다. 다만 내부 실행은 항상 semantic key를 우선 사용하고, 구체적인 dataset id 선택은 universe layer가 담당한다.

예시:

- `close -> qw_ksdq_adj_c`
- `open -> qw_ksdq_adj_o`
- `high -> qw_ksdq_adj_h`
- `low -> qw_ksdq_adj_l`
- `volume -> qw_ksdq_v`
- `market_cap -> qw_ksdq_mkcap`
- `float_market_cap -> qw_ksdq_mktcap_flt`
- `sector_big -> qw_ksdq_wics_sec_big`
- `universe_membership -> qw_ksdq150_yn`

### Universe Layer

새 dataclass를 도입한다.

```python
@dataclass(frozen=True, slots=True)
class UniverseSpec:
    id: str
    display_name: str
    description: str
    membership_dataset: DatasetId | None
    default_benchmark_code: str
    default_benchmark_name: str
    default_benchmark_dataset: str
    dataset_aliases: Mapping[str, DatasetId]
```

`dataset_aliases`는 실행 의미를 dataset id로 매핑한다.

예시 키:

- `close`
- `open`
- `high`
- `low`
- `volume`
- `market_cap`
- `float_market_cap`
- `sector_big`

`UniverseRegistry`는 최소 책임만 가진다.

- `default()`
- `get(universe_id: str) -> UniverseSpec`
- `has(universe_id: str) -> bool`
- `ids() -> tuple[str, ...]`

초기 등록 universe는 두 개다.

- `legacy_k200`
기존 실행 경로를 의미적으로 표현하는 내부 호환용 universe. membership은 `qw_k200_yn`, benchmark 기본값은 KOSPI200.

- `kosdaq150`
membership은 `qw_ksdq150_yn`, benchmark 기본값은 `qw_BM` 내 `IKQ150`/`KOSDAQ150`, 가격/시총/섹터는 `qw_ksdq_*` 패밀리 사용.

`legacy_k200`는 외부에 강하게 노출하지 않아도 되지만, 구현 내부에서는 명시적 spec로 두는 편이 분기 로직을 단순하게 만든다.

### Responsibility Boundaries

- `DataCatalog`: 파일 단위 dataset 등록
- `UniverseRegistry`: 실행 가능한 universe 정의
- `DataLoader`: 요청된 dataset id를 parquet에서 읽어 semantic frame으로 반환
- `BacktestRunner`: universe를 해석하고 필요한 dataset과 benchmark를 구성
- `dashboard` preset: `universe_id`를 선언적으로 보관

## API Design

### Python API

`LoadRequest`에 다음 필드를 추가한다.

```python
universe_id: str | None = None
```

의미:

- `None`: 호출자가 직접 `universe` DataFrame을 주거나 기존 경로를 사용
- `"kosdaq150"`: registry 기반 universe 선택

`RunConfig`에도 동일하게 추가한다.

```python
universe_id: str | None = None
```

`use_k200`는 즉시 제거하지 않는다. 하위 호환을 위해 유지한다.

해석 규칙:

- `universe_id`가 명시되면 그것이 최우선
- `universe_id`가 없고 `use_k200=True`면 기존 K200 경로 유지
- `universe_id`가 없고 `use_k200=False`면 무필터 전체 경로 유지

### CLI

`run.py` parser에 아래 인자를 추가한다.

```text
--universe <universe_id>
```

동작:

- `--universe kosdaq150` 지원
- 미지정 시 기존 동작 유지
- `--no-k200`는 계속 유지하되 `--universe`가 주어지면 무시하거나 충돌 검증을 수행한다

권장 동작은 명확한 우선순위다.

- `--universe` 지정 시 `use_k200`는 계산 결과에만 반영되고 직접적인 universe 선택에는 관여하지 않음
- `--universe kosdaq150 --no-k200` 같은 조합은 허용하되 실질적으로 `--universe`가 우선

CLI help에는 사용 가능한 universe 목록을 노출한다.

## Backtest Execution Flow

`BacktestRunner.run()`은 universe 해석의 단일 진입점이 된다.

실행 순서:

1. `RunConfig.universe_id`를 해석한다.
2. universe spec이 있으면 전략 요구 dataset과 universe alias dataset을 합친다.
3. 필요한 parquet가 없으면 ingest를 수행한다.
4. `LoadRequest`로 market data를 읽는다.
5. universe membership dataset이 있으면 `market.universe`를 생성한다.
6. 기본 benchmark 정보가 비어 있으면 universe spec의 기본값을 채운다.
7. 전략, policy, engine은 기존처럼 `market.universe`와 `market.frames`만 사용한다.

중요한 점은 전략 계층이 유니버스 종류를 몰라도 된다는 것이다. 전략은 여전히 `market.frames["close"]`, `market.frames["market_cap"]` 같은 semantic frame만 소비한다.

이를 위해 runner 또는 별도 resolver가 universe spec의 alias를 실제 load 대상 dataset id로 풀고, 로더가 반환한 frame key가 semantic key 기준으로 일관되게 유지되어야 한다.

## Benchmark Behavior

`kosdaq150`의 기본 benchmark는 코스닥150이다.

전제:

- 실제 benchmark 시계열은 `qw_BM`에 들어 있다.

설계 원칙:

- universe는 `default_benchmark_code`, `default_benchmark_name`, `default_benchmark_dataset`를 제안한다.
- 사용자가 `RunConfig.benchmark_code`, `benchmark_name`, `benchmark_dataset`을 직접 주면 그 값을 우선한다.
- 저장된 run config는 최종 해석된 benchmark 정보를 그대로 기록한다.

따라서 리포팅 계층은 큰 구조 변경 없이 기존 `BenchmarkConfig`를 그대로 사용할 수 있다.

## Dashboard Integration

dashboard preset 레이어는 universe를 소유하지 않고 참조만 한다.

변경점:

- `dashboard/strategies.py`의 global config 또는 preset에 `universe_id` 필드 추가
- launch signature 생성 시 `universe_id`를 포함
- default benchmark가 preset에 명시되지 않은 경우 universe 기본값을 사용

이 구조는 코어 dataclass와 dashboard 편의 설정을 분리한다. `UniverseSpec`가 전략 preset까지 직접 소유하지 않기 때문에, 코어 backtesting 타입과 UI 실행 기본값이 과도하게 결합되지 않는다.

## Error Handling

다음 오류는 명시적으로 실패시킨다.

- 알 수 없는 `universe_id`
- universe가 요구하는 dataset parquet/raw 파일 누락
- universe 기본 benchmark code가 `qw_BM`에 존재하지 않음
- universe alias에서 필수 semantic key가 빠짐

에러 메시지는 반드시 어떤 universe, 어떤 dataset, 어떤 benchmark 값이 문제인지 포함해야 한다.

묵시적 fallback은 피한다. 예를 들어 `kosdaq150` benchmark를 찾지 못했을 때 조용히 KOSPI200으로 대체하지 않는다.

## Backward Compatibility

기존 사용자를 깨지 않기 위해 다음 규칙을 유지한다.

- `RunConfig`에서 `universe_id`를 주지 않으면 기존 경로 유지
- `use_k200=True` 기본값 유지
- 기존 테스트와 CLI 예시는 수정 없이 동작해야 함

즉 기본 경험은 그대로 두고, `kosdaq150`를 쓰려는 사용자만 명시적으로 새로운 레이어를 사용한다.

## Testing Strategy

테스트는 다음 레벨로 추가한다.

### Catalog

- `qw_ksdq_*` dataset id가 enum에 등록되는지
- `DataCatalog.default()`에 올바른 spec이 들어가는지
- 그룹, dtype, validity, fill 속성이 기존 패턴과 일치하는지

### Universe Registry

- `kosdaq150` spec 조회 가능 여부
- membership dataset, close/open/market_cap/sector alias 확인
- 기본 benchmark 값이 코스닥150로 설정되는지
- 알 수 없는 universe 조회 시 예외 발생 여부

### Loader And Runner

- `RunConfig(universe_id="kosdaq150")`에서 `qw_ksdq_adj_c` 등 코스닥150 데이터가 선택되는지
- membership mask가 `market.universe`로 반영되는지
- 전략 결과에서 universe 밖 종목이 제외되는지
- `universe_id` 없이 실행 시 기존 `qw_k200_yn` 동작이 유지되는지

### CLI

- `--universe kosdaq150` parsing
- config 직렬화 결과에 `universe_id` 저장
- `--universe`와 기존 `--no-k200` 조합 처리

### Dashboard

- preset에 `universe_id`를 넣었을 때 launch config에 반영되는지
- run signature 비교에 `universe_id`가 포함되는지

## Implementation Notes

구현 시 다음 순서를 권장한다.

1. dataset id/catalog 등록
2. universe dataclass/registry 추가
3. runner가 universe 기반 dataset resolution을 사용하도록 변경
4. CLI와 dashboard preset 연결
5. 리포트/저장 config 검증
6. 호환 테스트와 새 universe 테스트 보강

이 순서면 코어 데이터 경로부터 안정화한 뒤 상위 레이어를 연결할 수 있다.

## Success Criteria

완료 기준은 아래와 같다.

- `raw/ksdq` 데이터가 기존 ingest 파이프를 통해 parquet로 변환된다
- Python API에서 `universe_id="kosdaq150"`를 지정해 백테스트를 실행할 수 있다
- CLI에서 `--universe kosdaq150`로 실행할 수 있다
- universe 밖 종목은 signal/weights/engine tradable 경로에서 제외된다
- 기본 benchmark는 코스닥150로 채워지지만 사용자가 override할 수 있다
- 기존 K200 기반 실행 및 테스트는 그대로 유지된다
