# Gmail Report Source Integration Design

## Goal

`analysts/`에 Gmail 기반 리포트 수집 경로를 추가하되, 기존 Telegram 경로와는 **source 레벨에서 강하게 분리**하고, 정규화된 문서가 된 뒤에만 공통 분석 파이프라인으로 합류하도록 설계한다.

이 설계의 목표는 단순히 Gmail을 "하나 더 붙이는 것"이 아니다. Gmail은 메일 본문 자체가 리포트일 수 있고, 첨부가 여러 개일 수 있으며, ZIP 안에 여러 문서가 다시 들어 있을 수 있다. 따라서 1차 목표는 Gmail의 고유 복잡성을 흡수할 수 있는 **source model / state model / candidate-document schema**를 만드는 것이다.

## Desired Outcome

다음 조건을 만족하는 Gmail 설계를 확정한다.

- Gmail 연결은 `Gmail API + OAuth`를 기준으로 한다.
- Telegram과 Gmail은 ingestion 단계에서 명확히 분리된다.
- Gmail은 `1 email -> N candidate documents` 구조를 허용한다.
- Gmail body는 규칙을 만족할 때만 candidate document가 된다.
- ZIP은 1차에서 `PDF / TXT / HTML`만 제한적으로 해제한다.
- dedupe는 candidate-document 기준으로 동작한다.
- sync 전략은 구조적으로 push-friendly하게 설계하되, 1차 구현은 polling/sync 기반으로 시작한다.
- canonical document로 정규화된 뒤에는 기존 공통 분석 파이프라인에 합류한다.

## Why Gmail Must Not Be Modeled Like Telegram

현재 Telegram 구조는 다음 가정에 잘 맞는다.

- channel 중심 수집
- message_id 중심 상태 관리
- 보통 메시지 하나가 문서 하나 또는 문서 없음으로 귀결
- caption + PDF 정도의 단순 payload

반면 Gmail은 다음과 같은 특성을 갖는다.

- mailbox / query / label 기반 수집
- thread와 message가 별도 개념
- message body 자체가 중요한 리포트일 수 있음
- attachment가 여러 개일 수 있음
- ZIP 안에 다시 복수 문서가 포함될 수 있음
- MIME tree를 따라 payload를 해석해야 함

따라서 Gmail을 기존 Telegram `channel/message/pdf` 구조에 억지로 끼워 넣는 방식은 피해야 한다. Gmail은 **Telegram의 subtype이 아니라 별도 source**로 모델링해야 한다.

## Chosen Direction

추천 구조는 다음과 같다.

### Rule 1 — Source는 강하게 분리

수집 단계에서는 Telegram과 Gmail을 별도 계층으로 둔다.

- `sources/telegram/*`
- `sources/gmail/*`

각 source는 인증, 상태 관리, raw artifact 저장, source-specific sync semantics를 직접 소유한다.

### Rule 2 — 정규화된 문서 이후에만 합류

Gmail message나 Telegram message는 바로 분석 대상으로 들어가지 않는다. 각 source는 자신만의 구조를 정규화하여 **canonical document**를 만든 뒤, 그 문서만 shared analysis layer로 넘긴다.

### Rule 3 — Gmail message와 candidate document를 분리

Gmail에서는 source truth인 email message와 실제 분석 입력인 candidate document를 분리한다.

- source object: Gmail message
- analysis object: candidate document

이 분리를 통해 body, attachments, ZIP entries를 모두 자연스럽게 다룰 수 있다.

## Architecture

### Layer A — Source ingestion layer

#### Telegram

Telegram은 현재 구조를 최대한 유지한다.

- watch / catch-up / live subscription
- channel 중심 상태 관리
- PDF report persistence

#### Gmail

Gmail은 별도 source 계층을 둔다.

역할:

- OAuth 인증
- Gmail API를 통한 sync/poll
- label/query 기반 message 조회
- message metadata 저장
- body / attachments / ZIP entries 추출 준비
- raw Gmail artifact 저장
- Gmail 전용 state persistence

Gmail 계층은 1차에서 **polling/sync 기반**으로 시작한다. 다만 state schema는 나중에 `watch + historyId` 기반 증분 sync를 붙일 수 있도록 설계한다.

### Layer B — Document normalization layer

이 레이어가 Gmail 통합의 핵심이다.

역할:

- message body candidate 판정
- attachment MIME 분류
- ZIP 해제 allowlist 적용
- candidate document 생성
- canonical document 변환

이 레이어에서만 Gmail의 복잡도가 집중되고, 이 뒤부터는 shared pipeline에 공통 입력이 들어간다.

### Layer C — Shared analysis layer

canonical document가 만들어진 뒤에는 기존 공통 파이프라인으로 합류한다.

- extraction
- chunking
- page selection
- summarization
- output writing
- graphify / downstream update

즉 구조는 아래와 같다.

`Telegram source -> canonical document -> shared analysis`
`Gmail source -> candidate documents -> canonical document -> shared analysis`

## Gmail Data Model

## 1. Gmail Message

Gmail message는 source object다. 아직 분석 대상 문서는 아니다.

권장 필드:

- `gmail_message_id`
- `gmail_thread_id`
- `history_id`
- `label_ids`
- `from`
- `to`
- `subject`
- `internal_date`
- `snippet`
- `body_plain`
- `body_html`
- `raw_payload_json`
- `sync_status`
- `account_name`
- `query_fingerprint`

이 객체는 Gmail 원본에 대한 충실한 저장소 역할을 한다.

## 2. Gmail Attachment

message에 매달린 attachment metadata를 별도 엔터티로 관리한다.

권장 필드:

- `gmail_message_id`
- `attachment_id`
- `filename`
- `mime_type`
- `size_bytes`
- `sha256`
- `raw_path`
- `is_zip`
- `extraction_status`

## 3. Gmail Candidate Document

실제 downstream analysis의 진입점이다. Gmail message 하나에서 여러 개가 만들어질 수 있다.

지원 candidate kind (1차):

- `email_body`
- `attachment_pdf`
- `attachment_txt`
- `attachment_html`
- `zip_entry_pdf`
- `zip_entry_txt`
- `zip_entry_html`

권장 필드:

- `candidate_id`
- `gmail_message_id`
- `gmail_thread_id`
- `candidate_kind`
- `source_path`
- `title`
- `mime_type`
- `dedupe_key`
- `sha256`
- `promotion_reason`
- `raw_path`
- `normalized_text_path`
- `status`

## One Email -> Many Candidate Documents

이 설계는 `1 email -> N candidate documents`를 기본 모델로 채택한다.

예를 들면:

- body 자체가 structured report면 `email_body` candidate 1개
- PDF 첨부 2개면 `attachment_pdf` 2개
- ZIP 안에 TXT 1개, PDF 3개면 `zip_entry_*` 4개

이 구조는 Gmail에 가장 자연스럽다. 하나의 email을 억지로 하나의 report object로 collapse하지 않는다.

## Body Candidate Promotion Rules

body는 항상 candidate로 만들지 않는다. noise를 줄이기 위해 **rule-based promotion**만 허용한다.

예상 규칙:

- 본문 길이가 최소 기준 이상일 것
- plain text / html stripping 후 충분한 정보량이 남을 것
- 표/헤더/제목 등 structured report 신호가 존재할 것
- attachment-only forwarding이나 짧은 코멘트 메일은 제외할 것

body candidate는 1차에서 heuristic 기반으로 시작하고, 나중에 classifier를 붙일 수 있도록 설계한다.

## ZIP Handling

ZIP은 1차에서 제한적으로만 지원한다.

허용:

- `PDF`
- `TXT`
- `HTML`

제외:

- DOCX
- XLSX
- PPTX
- nested archives 전반
- 미지원 바이너리 포맷

ZIP은 무조건 전부 분석 대상으로 풀지 않는다. allowlist에 해당하는 entry만 candidate document로 승격한다.

## Dedupe Strategy

dedupe는 **candidate document 기준**으로 둔다.

예시 키:

- `body::<gmail_message_id>::<body_hash>`
- `attachment::<gmail_message_id>::<attachment_id>::<sha256>`
- `zip-entry::<gmail_message_id>::<attachment_id>::<entry_path>::<sha256>`

이 기준은 다음 장점이 있다.

- 하나의 email 안 여러 문서를 자연스럽게 분리 가능
- 재전송된 동일 attachment 식별 가능
- ZIP entry 단위 재처리/부분 실패 복구에 유리

1차 기준은 candidate-level dedupe로 두되, 필요하면 후속 확장에서 message-level bookkeeping을 추가할 수 있다.

## Canonical Document Shape

Gmail과 Telegram은 canonical document로 정규화된 뒤에만 공유 파이프라인으로 들어간다.

권장 공통 필드:

- `source`
- `source_message_id`
- `source_thread_id` (optional)
- `source_feed`
- `document_kind`
- `title`
- `published_at` / `received_at`
- `sender_or_origin`
- `mime_type`
- `dedupe_key`
- `raw_path`
- `normalized_text_path`
- `metadata`

이 canonical document만 만들어지면 downstream ingest/summarize는 source-agnostic하게 동작할 수 있다.

## Storage Layout

추천 구조:

```text
analysts/data/
  raw/
    telegram/
      ...
    gmail/
      ...
  processed/
    telegram/
      ...
    gmail/
      ...
  state/
    telegram.sqlite3
    gmail.sqlite3
```

1차에서는 최소한 다음을 분리한다.

- Telegram state DB
- Gmail state DB
- source-specific raw directories
- source-specific processed output directories

이 분리는 운영 장애, 재동기화, source-specific replay에서 큰 장점을 준다.

## Gmail State Model

Gmail state는 Telegram과 분리된 별도 store를 사용한다.

권장 상태:

- `last_full_sync_at`
- `last_poll_sync_at`
- `last_history_id`
- `last_successful_query_fingerprint`
- `oauth_account_id`
- `sync_mode`
- `cursor_status`
- `full_sync_required`

1차는 polling 기반이지만, state에는 `historyId`를 저장하여 차후 partial sync나 watch 전환이 가능하도록 한다.

## Sync Strategy

1차 구현 전략은 다음과 같다.

- 구조는 **push-friendly**하게 설계
- 실제 실행은 **polling / sync-once 기반**으로 시작

이유:

- OAuth / Gmail payload / candidate-document schema 정립이 먼저다
- Pub/Sub + watch + expiration 갱신은 후속 확장으로 미루는 것이 안전하다
- partial sync / full sync fallback semantics를 먼저 안정화해야 한다

따라서 1차는:

- `messages.list`
- `messages.get`
- local state cursor
- optional `historyId` persistence

중심으로 구현한다.

## CLI / Runner Shape

Telegram과 Gmail은 같은 앱 안에 있지만, 운영 surface는 분리한다.

### Telegram side

기존 흐름 유지 또는 telegram namespace 정리:

- `watch-telegram-until`
- `sync-telegram-once`

### Gmail side

신규 권장 surface:

- `gmail-auth-login`
- `gmail-sync-once`
- `gmail-sync-recent --limit N`
- `gmail-summarize-latest`
- `gmail-summarize-recent --limit N`

1차에서는 Gmail `watch`보다 `sync` 중심으로 둔다.

## Config Shape

Telegram과 Gmail 설정은 분리한다.

예상 구조:

```json
{
  "telegram": { ... },
  "gmail": {
    "account_name": "reports-primary",
    "oauth_client_secret_path": "...",
    "oauth_token_path": "...",
    "label_filters": ["Label_Reports"],
    "query": "newer_than:14d",
    "body_candidate_rules": {
      "min_chars": 800,
      "require_structure": true
    },
    "allowed_attachment_types": ["application/pdf", "text/plain", "text/html"],
    "zip_allow_extensions": [".pdf", ".txt", ".html"],
    "poll_interval_seconds": 300
  }
}
```

핵심은 Gmail-specific semantics를 Telegram config에 섞지 않는 것이다.

## First Release Scope

1차 구현에 포함할 것:

- Gmail API + OAuth 인증 경로
- Gmail source 계층 신설
- Gmail message / attachment / candidate-document schema
- body candidate promotion rules
- attachment `PDF / TXT / HTML` 지원
- ZIP allowlist extraction
- candidate-level dedupe
- canonical document 정규화
- 공통 summarize 경로로 최소 1개 이상 end-to-end 성공

1차에서 제외할 것:

- Gmail Pub/Sub watch
- 광범위 포맷 지원 (DOCX/XLSX/PPTX 등)
- complex thread merge
- advanced ranking / importance models
- production-grade multi-account orchestration

## Acceptance Direction

이 설계가 구현되었다고 판단하려면 최소한 다음을 만족해야 한다.

1. Gmail API OAuth 인증이 된다.
2. query/label 범위에서 메일을 sync할 수 있다.
3. 하나의 email에서 여러 candidate documents를 생성할 수 있다.
4. body는 규칙 만족 시에만 candidate로 생성된다.
5. `PDF / TXT / HTML` attachment가 candidate가 된다.
6. ZIP은 allowlist 확장만 수행한다.
7. dedupe는 candidate-document 기준으로 동작한다.
8. canonical document가 shared summarize path에 들어간다.
9. Gmail latest/recent summarize 명령이 최소 1회 성공한다.
10. 기존 Telegram 경로는 깨지지 않는다.

## Integration Stance on OpenClaw / gog / MCP

OpenClaw `gog`나 MCP류 연결은 탐색적 bootstrap에는 쓸 수 있다. 하지만 이 설계에서는 그들을 **운영 schema의 주인**으로 두지 않는다.

이유:

- Gmail의 핵심 복잡도는 connection보다 schema에 있다.
- `historyId`, `threadId`, labels, MIME tree, candidate-document 분리는 analysts 내부가 직접 소유해야 한다.
- OpenClaw는 이후 stable CLI surface를 호출하는 외부 orchestrator로 두는 편이 더 안전하다.

즉 설계 원칙은 다음과 같다.

> Gmail connector는 바꿔 끼울 수 있게 두고, source state와 schema ownership은 `analysts/` 안에 둔다.

## Risks

- body promotion rule이 너무 느슨하면 noise가 많아질 수 있다.
- candidate-only dedupe는 후속 운영에서 message-level bookkeeping 필요성을 다시 부를 수 있다.
- ZIP allowlist만으로는 실제 broker file 다양성을 모두 커버하지 못할 수 있다.
- Gmail sync는 초기에 query/label scoping이 약하면 처리량이 빨리 커질 수 있다.

## Recommendation

1차 구현은 Gmail을 Telegram과 별도 source로 도입하고, **message → candidate documents → canonical document → shared analysis** 흐름을 만드는 데 집중한다.

이 설계는 Gmail의 복잡성을 정면으로 다루면서도, 기존 analysts 파이프라인을 불필요하게 다시 쓰지 않도록 해준다.
