# Blog Reorganisation — Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Clean up all blog URLs (remove dates, migrate /misc/ to /tech-stack/), restructure Python and Tech Stack tabs, create Phase 2 capstone page, and add D3.js graph homepage.

**Architecture:** Bulk front matter edits across 42 post files, tab page rewrites for Python and Tech Stack, internal cross-link updates in 5 posts and 1 capstone page, a new Phase 2 capstone collection page, and a new index.html with inline D3.js force-directed graph generated from Liquid-templated JSON.

**Tech Stack:** Jekyll (Chirpy theme), D3.js v7 (CDN), Liquid templates

---

## File Structure

```
docs/
├── _posts/                          # 42 files: permalink front matter updates
├── _tabs/
│   ├── misc.md                      # Permalink /misc/ → /tech-stack/, restructure sections
│   ├── python.md                    # Remove AWS/Docker/explainer sections, update links
│   └── quant-lab.md                 # Add Phase 2 capstone section + explainer links
├── _quant_lab/
│   ├── stock-risk-scanner.html      # Update internal cross-links
│   └── aws-credit-risk.html         # NEW: Phase 2 capstone page
└── index.html                       # NEW: D3.js graph homepage
```

---

### Task 1: Update Python exercise post permalinks (7 files)

**Files:**
- Modify: `docs/_posts/2026-04-01-pytest-tdd-for-financial-python.html`
- Modify: `docs/_posts/2026-04-02-pydantic-models-for-trading-data.html`
- Modify: `docs/_posts/2026-04-02-fastapi-your-first-financial-api.html`
- Modify: `docs/_posts/2026-04-02-async-python-for-market-data.html`
- Modify: `docs/_posts/2026-04-02-yfinance-fetching-market-data.html`
- Modify: `docs/_posts/2026-04-02-claude-api-ai-risk-analysis.html`
- Modify: `docs/_posts/2026-04-02-postgresql-sqlalchemy-async.html`

- [ ] **Step 1: Update each file's permalink in front matter**

In each file, change the `permalink:` line:

| File | Old | New |
|------|-----|-----|
| 2026-04-01-pytest-tdd-for-financial-python.html | `permalink: /2026/04/01/pytest-tdd-financial-python/` | `permalink: "/python/pytest-tdd-financial-python/"` |
| 2026-04-02-pydantic-models-for-trading-data.html | `permalink: /2026/04/02/pydantic-models-trading-data/` | `permalink: "/python/pydantic-models-trading-data/"` |
| 2026-04-02-fastapi-your-first-financial-api.html | `permalink: /2026/04/02/fastapi-your-first-financial-api/` | `permalink: "/python/fastapi-your-first-financial-api/"` |
| 2026-04-02-async-python-for-market-data.html | `permalink: /2026/04/02/async-python-for-market-data/` | `permalink: "/python/async-python-for-market-data/"` |
| 2026-04-02-yfinance-fetching-market-data.html | `permalink: /2026/04/02/yfinance-fetching-market-data/` | `permalink: "/python/yfinance-fetching-market-data/"` |
| 2026-04-02-claude-api-ai-risk-analysis.html | `permalink: /2026/04/02/claude-api-ai-risk-analysis/` | `permalink: "/python/claude-api-ai-risk-analysis/"` |
| 2026-04-02-postgresql-sqlalchemy-async.html | `permalink: /2026/04/02/postgresql-sqlalchemy-async/` | `permalink: "/python/postgresql-sqlalchemy-async/"` |

- [ ] **Step 2: Fix cross-link in FastAPI exercise post**

In `2026-04-02-fastapi-your-first-financial-api.html`, change:
```
href="/FinBytes/2026/04/02/pydantic-models-trading-data/"
```
to:
```
href="/FinBytes/python/pydantic-models-trading-data/"
```

- [ ] **Step 3: Commit**

```bash
cd c:/codebase/finbytes_git
git add docs/_posts/2026-04-01-pytest-tdd-for-financial-python.html \
        docs/_posts/2026-04-02-pydantic-models-for-trading-data.html \
        docs/_posts/2026-04-02-fastapi-your-first-financial-api.html \
        docs/_posts/2026-04-02-async-python-for-market-data.html \
        docs/_posts/2026-04-02-yfinance-fetching-market-data.html \
        docs/_posts/2026-04-02-claude-api-ai-risk-analysis.html \
        docs/_posts/2026-04-02-postgresql-sqlalchemy-async.html
git commit -m "refactor: migrate Python exercise permalinks to /python/ prefix"
```

---

### Task 2: Update Tech Stack exercise post permalinks (13 files)

**Files:**
- Modify: `docs/_posts/2026-04-02-docker-for-python-services.html`
- Modify: `docs/_posts/2026-04-04-aws-fundamentals-treasury-data.html`
- Modify: `docs/_posts/2026-04-05-s3-par-curve-ingestion.html`
- Modify: `docs/_posts/2026-04-06-rds-postgresql-yield-schema.html`
- Modify: `docs/_posts/2026-04-07-lambda-spot-curve-bootstrapping.html`
- Modify: `docs/_posts/2026-04-08-cicd-forward-rate-curve.html`
- Modify: `docs/_posts/2026-04-09-terraform-nelson-siegel.html`
- Modify: `docs/_posts/2026-04-10-sqs-sns-credit-spreads.html`
- Modify: `docs/_posts/2026-04-11-websockets-realtime-spreads.html`
- Modify: `docs/_posts/2026-04-12-elasticache-bond-caching.html`
- Modify: `docs/_posts/2026-04-13-terraform-advanced-default-probs.html`
- Modify: `docs/_posts/2026-04-14-cloudwatch-oas-zspreads.html`
- Modify: `docs/_posts/2026-04-15-integration-testing-credit-var.html`

- [ ] **Step 1: Update each file's permalink in front matter**

| File | Old | New |
|------|-----|-----|
| 2026-04-02-docker-for-python-services.html | `/2026/04/02/docker-for-python-services/` | `"/tech-stack/docker-for-python-services/"` |
| 2026-04-04-aws-fundamentals-treasury-data.html | `/2026/04/04/aws-fundamentals-treasury-data/` | `"/tech-stack/aws-fundamentals-treasury-data/"` |
| 2026-04-05-s3-par-curve-ingestion.html | `/2026/04/05/s3-par-curve-ingestion/` | `"/tech-stack/s3-par-curve-ingestion/"` |
| 2026-04-06-rds-postgresql-yield-schema.html | `/2026/04/06/rds-postgresql-yield-schema/` | `"/tech-stack/rds-postgresql-yield-schema/"` |
| 2026-04-07-lambda-spot-curve-bootstrapping.html | `/2026/04/07/lambda-spot-curve-bootstrapping/` | `"/tech-stack/lambda-spot-curve-bootstrapping/"` |
| 2026-04-08-cicd-forward-rate-curve.html | `/2026/04/08/cicd-forward-rate-curve/` | `"/tech-stack/cicd-forward-rate-curve/"` |
| 2026-04-09-terraform-nelson-siegel.html | `/2026/04/09/terraform-nelson-siegel/` | `"/tech-stack/terraform-nelson-siegel/"` |
| 2026-04-10-sqs-sns-credit-spreads.html | `/2026/04/10/sqs-sns-credit-spreads/` | `"/tech-stack/sqs-sns-credit-spreads/"` |
| 2026-04-11-websockets-realtime-spreads.html | `/2026/04/11/websockets-realtime-spreads/` | `"/tech-stack/websockets-realtime-spreads/"` |
| 2026-04-12-elasticache-bond-caching.html | `/2026/04/12/elasticache-bond-caching/` | `"/tech-stack/elasticache-bond-caching/"` |
| 2026-04-13-terraform-advanced-default-probs.html | `/2026/04/13/terraform-advanced-default-probs/` | `"/tech-stack/terraform-advanced-default-probs/"` |
| 2026-04-14-cloudwatch-oas-zspreads.html | `/2026/04/14/cloudwatch-oas-zspreads/` | `"/tech-stack/cloudwatch-oas-zspreads/"` |
| 2026-04-15-integration-testing-credit-var.html | `/2026/04/15/integration-testing-credit-var/` | `"/tech-stack/integration-testing-credit-var/"` |

- [ ] **Step 2: Fix cross-links in exercise posts that link to each other**

In `2026-04-05-s3-par-curve-ingestion.html`, change:
```
href="/2026/04/04/aws-fundamentals-treasury-data/"
```
to:
```
href="{{ "/tech-stack/aws-fundamentals-treasury-data/" | relative_url }}"
```

In `2026-04-06-rds-postgresql-yield-schema.html`, change:
```
href="/2026/04/05/s3-par-curve-ingestion/"
```
to:
```
href="{{ "/tech-stack/s3-par-curve-ingestion/" | relative_url }}"
```

In `2026-04-07-lambda-spot-curve-bootstrapping.html`, change:
```
href="/2026/04/06/rds-postgresql-yield-schema/"
```
to:
```
href="{{ "/tech-stack/rds-postgresql-yield-schema/" | relative_url }}"
```

In `2026-04-08-cicd-forward-rate-curve.html`, change:
```
href="/2026/04/07/lambda-spot-curve-bootstrapping/"
```
to:
```
href="{{ "/tech-stack/lambda-spot-curve-bootstrapping/" | relative_url }}"
```

- [ ] **Step 3: Commit**

```bash
cd c:/codebase/finbytes_git
git add docs/_posts/2026-04-02-docker-for-python-services.html \
        docs/_posts/2026-04-04-aws-fundamentals-treasury-data.html \
        docs/_posts/2026-04-05-s3-par-curve-ingestion.html \
        docs/_posts/2026-04-06-rds-postgresql-yield-schema.html \
        docs/_posts/2026-04-07-lambda-spot-curve-bootstrapping.html \
        docs/_posts/2026-04-08-cicd-forward-rate-curve.html \
        docs/_posts/2026-04-09-terraform-nelson-siegel.html \
        docs/_posts/2026-04-10-sqs-sns-credit-spreads.html \
        docs/_posts/2026-04-11-websockets-realtime-spreads.html \
        docs/_posts/2026-04-12-elasticache-bond-caching.html \
        docs/_posts/2026-04-13-terraform-advanced-default-probs.html \
        docs/_posts/2026-04-14-cloudwatch-oas-zspreads.html \
        docs/_posts/2026-04-15-integration-testing-credit-var.html
git commit -m "refactor: migrate Tech Stack exercise permalinks to /tech-stack/ prefix"
```

---

### Task 3: Update Quant Lab post permalinks (3 files)

**Files:**
- Modify: `docs/_posts/2026-04-03-quantlab-phase1-explained.html`
- Modify: `docs/_posts/2026-04-16-quantlab-phase2-explained.html`
- Modify: `docs/_posts/2026-04-03-stock-risk-scanner-architecture.html`

- [ ] **Step 1: Update each file's permalink in front matter**

| File | Old | New |
|------|-----|-----|
| 2026-04-03-quantlab-phase1-explained.html | `/2026/04/03/quantlab-phase1-explained/` | `"/quant-lab/phase1-explained/"` |
| 2026-04-16-quantlab-phase2-explained.html | `/2026/04/16/quantlab-phase2-explained/` | `"/quant-lab/phase2-explained/"` |
| 2026-04-03-stock-risk-scanner-architecture.html | `/2026/04/03/stock-risk-scanner-architecture/` | `"/quant-lab/stock-risk-scanner-architecture/"` |

- [ ] **Step 2: Commit**

```bash
cd c:/codebase/finbytes_git
git add docs/_posts/2026-04-03-quantlab-phase1-explained.html \
        docs/_posts/2026-04-16-quantlab-phase2-explained.html \
        docs/_posts/2026-04-03-stock-risk-scanner-architecture.html
git commit -m "refactor: migrate explainer/architecture permalinks to /quant-lab/ prefix"
```

---

### Task 4: Migrate /misc/ permalinks to /tech-stack/ (11 files)

**Files:**
- Modify: `docs/_posts/2026-04-20-aws-services-reference.html`
- Modify: `docs/_posts/2026-04-21-terraform-reference.html`
- Modify: `docs/_posts/2026-04-22-fastapi-reference.html`
- Modify: `docs/_posts/2026-04-23-postgresql-sqlalchemy-reference.html`
- Modify: `docs/_posts/2026-04-24-streamlit-reference.html`
- Modify: `docs/_posts/2026-04-25-github-actions-reference.html`
- Modify: `docs/_posts/2026-07-01-redis-caching-reference.html`
- Modify: `docs/_posts/2026-07-02-message-queues-rabbitmq-reference.html`
- Modify: `docs/_posts/2026-07-03-argparse-cli-reference.html`
- Modify: `docs/_posts/2026-07-04-git-workflow-reference.html`
- Modify: `docs/_posts/2026-07-05-docker-cicd-reference.html`

- [ ] **Step 1: In each file, replace `/misc/` with `/tech-stack/` in the permalink field**

| File | Old | New |
|------|-----|-----|
| 2026-04-20-aws-services-reference.html | `"/misc/aws-services/"` | `"/tech-stack/aws-services/"` |
| 2026-04-21-terraform-reference.html | `"/misc/terraform/"` | `"/tech-stack/terraform/"` |
| 2026-04-22-fastapi-reference.html | `"/misc/fastapi/"` | `"/tech-stack/fastapi/"` |
| 2026-04-23-postgresql-sqlalchemy-reference.html | `"/misc/postgresql-sqlalchemy/"` | `"/tech-stack/postgresql-sqlalchemy/"` |
| 2026-04-24-streamlit-reference.html | `"/misc/streamlit/"` | `"/tech-stack/streamlit/"` |
| 2026-04-25-github-actions-reference.html | `"/misc/github-actions/"` | `"/tech-stack/github-actions/"` |
| 2026-07-01-redis-caching-reference.html | `"/misc/redis-caching/"` | `"/tech-stack/redis-caching/"` |
| 2026-07-02-message-queues-rabbitmq-reference.html | `"/misc/message-queues/"` | `"/tech-stack/message-queues/"` |
| 2026-07-03-argparse-cli-reference.html | `"/misc/argparse-cli/"` | `"/tech-stack/argparse-cli/"` |
| 2026-07-04-git-workflow-reference.html | `"/misc/git-workflow/"` | `"/tech-stack/git-workflow/"` |
| 2026-07-05-docker-cicd-reference.html | `"/misc/docker-cicd/"` | `"/tech-stack/docker-cicd/"` |

- [ ] **Step 2: Commit**

```bash
cd c:/codebase/finbytes_git
git add docs/_posts/2026-04-20-aws-services-reference.html \
        docs/_posts/2026-04-21-terraform-reference.html \
        docs/_posts/2026-04-22-fastapi-reference.html \
        docs/_posts/2026-04-23-postgresql-sqlalchemy-reference.html \
        docs/_posts/2026-04-24-streamlit-reference.html \
        docs/_posts/2026-04-25-github-actions-reference.html \
        docs/_posts/2026-07-01-redis-caching-reference.html \
        docs/_posts/2026-07-02-message-queues-rabbitmq-reference.html \
        docs/_posts/2026-07-03-argparse-cli-reference.html \
        docs/_posts/2026-07-04-git-workflow-reference.html \
        docs/_posts/2026-07-05-docker-cicd-reference.html
git commit -m "refactor: migrate /misc/ permalinks to /tech-stack/"
```

---

### Task 5: Rewrite Python tab

**Files:**
- Modify: `docs/_tabs/python.md`

- [ ] **Step 1: Replace the QuantLab Exercise Posts, Phase 2, and Explainers sections**

Keep sections 1 (Python References) and 2 (Testing — pytest) unchanged.

Replace section 3 "QuantLab Exercise Posts" — remove Docker (exercise 07), update all links to clean `/python/` permalinks:

```html
<div class="py-section">
  <div class="py-section-hdr">QuantLab Exercises</div>
  <ul class="py-list">
    <li>
      <a href="{{ "/python/pytest-tdd-financial-python/" | relative_url }}">TDD with pytest</a>
      <span class="py-desc">Exercise 01 &mdash; red-green-refactor, daily returns, max drawdown</span>
    </li>
    <li>
      <a href="{{ "/python/pydantic-models-trading-data/" | relative_url }}">Pydantic v2 Models</a>
      <span class="py-desc">Exercise 02 &mdash; field validators, computed fields, trading data contracts</span>
    </li>
    <li>
      <a href="{{ "/python/fastapi-your-first-financial-api/" | relative_url }}">FastAPI</a>
      <span class="py-desc">Exercise 03 &mdash; routes, status codes, TestClient, OpenAPI docs</span>
    </li>
    <li>
      <a href="{{ "/python/async-python-for-market-data/" | relative_url }}">Async Python</a>
      <span class="py-desc">Exercise 04 &mdash; asyncio, aiohttp, gather, concurrent price fetching</span>
    </li>
    <li>
      <a href="{{ "/python/yfinance-fetching-market-data/" | relative_url }}">yfinance</a>
      <span class="py-desc">Exercise 05 &mdash; fetching prices, pandas wrangling, data quality</span>
    </li>
    <li>
      <a href="{{ "/python/claude-api-ai-risk-analysis/" | relative_url }}">Claude API</a>
      <span class="py-desc">Exercise 06 &mdash; AI-powered risk narratives, graceful degradation</span>
    </li>
    <li>
      <a href="{{ "/python/postgresql-sqlalchemy-async/" | relative_url }}">PostgreSQL &amp; SQLAlchemy</a>
      <span class="py-desc">Exercise 08 &mdash; async ORM, Alembic migrations, testing with SQLite</span>
    </li>
  </ul>
</div>
```

Remove sections 4 (QuantLab Phase 2) and 5 (Explainers & Architecture) entirely.

- [ ] **Step 2: Commit**

```bash
cd c:/codebase/finbytes_git
git add docs/_tabs/python.md
git commit -m "refactor: restructure Python tab — remove AWS/explainer sections, update links"
```

---

### Task 6: Rewrite Tech Stack tab

**Files:**
- Modify: `docs/_tabs/misc.md`

- [ ] **Step 1: Update permalink and all internal links**

Change front matter `permalink: /misc/` to `permalink: /tech-stack/`.

Replace all `/misc/` hrefs with `/tech-stack/` equivalents in the existing sections.

Add a new section 4 "QuantLab — AWS & Credit Risk" with the exercise posts:

```html
<div class="misc-section" id="quantlab-aws">
  <div class="misc-hdr">QuantLab &mdash; AWS &amp; Credit Risk <span class="sub">exercises 07, 09&ndash;20</span></div>
  <ul class="misc-list">
    <li>
      <a href="{{ "/tech-stack/docker-for-python-services/" | relative_url }}">Docker for Python Services</a>
      <span class="misc-desc">Exercise 07 &mdash; multi-stage builds, compose, .dockerignore</span>
    </li>
    <li>
      <a href="{{ "/tech-stack/aws-fundamentals-treasury-data/" | relative_url }}">AWS Fundamentals &amp; Treasury Data</a>
      <span class="misc-desc">Exercise 09 &mdash; FRED API, IAM, S3 bucket, yield curve classification</span>
    </li>
    <li>
      <a href="{{ "/tech-stack/s3-par-curve-ingestion/" | relative_url }}">S3 Par Curve Ingestion</a>
      <span class="misc-desc">Exercise 10 &mdash; boto3, moto mocks, versioned S3 storage</span>
    </li>
    <li>
      <a href="{{ "/tech-stack/rds-postgresql-yield-schema/" | relative_url }}">RDS PostgreSQL &amp; Yield Schema</a>
      <span class="misc-desc">Exercise 11 &mdash; Alembic migrations, seed from S3, 6-table schema</span>
    </li>
    <li>
      <a href="{{ "/tech-stack/lambda-spot-curve-bootstrapping/" | relative_url }}">Lambda &amp; Spot Curve Bootstrapping</a>
      <span class="misc-desc">Exercise 12 &mdash; Lambda handler, API Gateway REST, 14 tests</span>
    </li>
    <li>
      <a href="{{ "/tech-stack/cicd-forward-rate-curve/" | relative_url }}">CI/CD &amp; Forward Rate Curve</a>
      <span class="misc-desc">Exercise 13 &mdash; GitHub Actions, OIDC, forward rates</span>
    </li>
    <li>
      <a href="{{ "/tech-stack/terraform-nelson-siegel/" | relative_url }}">Terraform &amp; Nelson-Siegel</a>
      <span class="misc-desc">Exercise 14 &mdash; IaC, scipy on Lambda, deployment friction log</span>
    </li>
    <li>
      <a href="{{ "/tech-stack/sqs-sns-credit-spreads/" | relative_url }}">SQS/SNS &amp; Credit Spreads</a>
      <span class="misc-desc">Exercise 15 &mdash; credit spreads, CDS, hazard rates, async messaging</span>
    </li>
    <li>
      <a href="{{ "/tech-stack/websockets-realtime-spreads/" | relative_url }}">WebSockets &amp; Real-Time Spreads</a>
      <span class="misc-desc">Exercise 16 &mdash; API Gateway WS, DynamoDB connections, fan-out</span>
    </li>
    <li>
      <a href="{{ "/tech-stack/elasticache-bond-caching/" | relative_url }}">ElastiCache &amp; Bond Caching</a>
      <span class="misc-desc">Exercise 17 &mdash; Redis cache-aside, TTL strategy, graceful degradation</span>
    </li>
    <li>
      <a href="{{ "/tech-stack/terraform-advanced-default-probs/" | relative_url }}">Terraform Advanced &amp; Default Probabilities</a>
      <span class="misc-desc">Exercise 18 &mdash; piecewise hazard rates, survival curves, modules</span>
    </li>
    <li>
      <a href="{{ "/tech-stack/cloudwatch-oas-zspreads/" | relative_url }}">CloudWatch &amp; OAS/Z-Spread</a>
      <span class="misc-desc">Exercise 19 &mdash; binomial trees, backward induction, callable bonds</span>
    </li>
    <li>
      <a href="{{ "/tech-stack/integration-testing-credit-var/" | relative_url }}">Integration Testing &amp; Credit VaR</a>
      <span class="misc-desc">Exercise 20 &mdash; Monte Carlo, Cholesky, spread duration, portfolio risk</span>
    </li>
  </ul>
</div>
```

- [ ] **Step 2: Commit**

```bash
cd c:/codebase/finbytes_git
git add docs/_tabs/misc.md
git commit -m "refactor: restructure Tech Stack tab — add AWS exercises, update all links to /tech-stack/"
```

---

### Task 7: Update Quant Lab tab + Stock Risk Scanner cross-links

**Files:**
- Modify: `docs/_tabs/quant-lab.md`
- Modify: `docs/_quant_lab/stock-risk-scanner.html`

- [ ] **Step 1: Add Phase 2 capstone section and explainer links to quant-lab.md**

After the existing "Capstone Project" `<ul>`, add a new capstone entry and explainer links:

```html
  <li>
    <a href="{{ "/quant-lab/aws-credit-risk/" | relative_url }}">AWS &amp; Bond/Credit Risk</a>
    <span class="ql-badges"><span class="ql-badge ql-badge-capstone">Capstone</span></span>
    <span class="ql-desc">12-exercise arc &mdash; AWS fundamentals through Monte Carlo Credit VaR</span>
    <span class="ql-tech">Python &middot; AWS (S3, Lambda, RDS, SQS, SNS, ElastiCache, CloudWatch) &middot; Terraform &middot; WebSockets &middot; Redis</span>
  </li>
```

After the capstone `<ul>`, before the mini projects, add an explainer section:

```html
<div class="ql-section">Explainers &amp; Architecture</div>

<ul class="ql-list">
  <li>
    <a href="{{ "/quant-lab/phase1-explained/" | relative_url }}">Phase 1 Explained</a>
    <span class="ql-desc">Every technology and concept from exercises 01&ndash;08, explained from scratch</span>
  </li>
  <li>
    <a href="{{ "/quant-lab/phase2-explained/" | relative_url }}">Phase 2 Explained</a>
    <span class="ql-desc">Every AWS service and finance formula from exercises 09&ndash;20</span>
  </li>
  <li>
    <a href="{{ "/quant-lab/stock-risk-scanner-architecture/" | relative_url }}">Stock Risk Scanner &mdash; Architecture Deep Dive</a>
    <span class="ql-desc">Request flow, module breakdown, deployment, async patterns</span>
  </li>
</ul>
```

- [ ] **Step 2: Update cross-links in stock-risk-scanner.html**

Replace all `/FinBytes/2026/...` hrefs with clean permalinks using `relative_url`:

Lines 60-67 (exercise table):
```html
<tr><td>01</td><td><a href="{{ "/python/pytest-tdd-financial-python/" | relative_url }}">pytest &amp; TDD</a></td><td>Fixtures, parametrize, approx</td><td>Test foundation &mdash; 26 tests covering every module</td></tr>
<tr><td>02</td><td><a href="{{ "/python/pydantic-models-trading-data/" | relative_url }}">Pydantic</a></td><td>Validators, computed fields</td><td>Request/response models</td></tr>
<tr><td>03</td><td><a href="{{ "/python/fastapi-your-first-financial-api/" | relative_url }}">FastAPI</a></td><td>Routes, status codes, TestClient</td><td>API endpoints &mdash; 4 routes</td></tr>
<tr><td>04</td><td><a href="{{ "/python/async-python-for-market-data/" | relative_url }}">Async Python</a></td><td>async/await, asyncio.gather</td><td>Async DB operations and background scan task</td></tr>
<tr><td>05</td><td><a href="{{ "/python/yfinance-fetching-market-data/" | relative_url }}">yfinance</a></td><td>Market data, pandas DataFrames</td><td>Price fetching in market_data.py</td></tr>
<tr><td>06</td><td><a href="{{ "/python/claude-api-ai-risk-analysis/" | relative_url }}">Claude API</a></td><td>Anthropic SDK, prompt engineering</td><td>AI narrative generation in narrative.py</td></tr>
<tr><td>07</td><td><a href="{{ "/tech-stack/docker-for-python-services/" | relative_url }}">Docker</a></td><td>Dockerfile, compose, multi-stage builds</td><td>Containerisation &mdash; app + PostgreSQL services</td></tr>
<tr><td>08</td><td><a href="{{ "/python/postgresql-sqlalchemy-async/" | relative_url }}">PostgreSQL + SQLAlchemy</a></td><td>Async ORM, Alembic migrations</td><td>Scan persistence via ScanRecord model</td></tr>
```

Line 338: change `href="/FinBytes/2026/04/03/stock-risk-scanner-architecture/"` to `href="{{ "/quant-lab/stock-risk-scanner-architecture/" | relative_url }}"`.

Line 469: change `href="{{ "/2026/04/03/quantlab-phase1-explained/" | relative_url }}"` to `href="{{ "/quant-lab/phase1-explained/" | relative_url }}"`.

- [ ] **Step 3: Commit**

```bash
cd c:/codebase/finbytes_git
git add docs/_tabs/quant-lab.md docs/_quant_lab/stock-risk-scanner.html
git commit -m "refactor: update Quant Lab tab with Phase 2 capstone section, fix cross-links"
```

---

### Task 8: Create Phase 2 capstone page

**Files:**
- Create: `docs/_quant_lab/aws-credit-risk.html`

- [ ] **Step 1: Create the capstone page**

Create `docs/_quant_lab/aws-credit-risk.html`:

```html
---
layout: quant-lab-capstone
title: "AWS & Bond/Credit Risk"
description: "Capstone project — a 12-exercise arc from AWS fundamentals through Monte Carlo Credit VaR, covering infrastructure-as-code, serverless compute, and quantitative credit risk."
date: 2026-04-16
tags: [AWS, Terraform, Lambda, S3, RDS, SQS, SNS, Redis, WebSockets, Credit Risk, Bond Pricing, VaR]
---

<div id="tab-brief" class="ql-tab-content active">
  <h2>What is the AWS &amp; Credit Risk Arc?</h2>
  <p>
    Twelve exercises that build a complete bond and credit risk analytics pipeline on AWS. Starting from raw Treasury yield data
    on S3, the arc constructs par curves, bootstraps spot rates, fits Nelson-Siegel models, prices bonds with OAS and Z-spread,
    computes default probabilities and expected losses, streams credit spreads via WebSockets, and culminates in a Monte Carlo
    Credit VaR simulation with correlated spread movements.
  </p>

  <h3>Pipeline Flow</h3>
  <ol>
    <li><strong>Ingest</strong> &mdash; FRED Treasury data &rarr; S3 (versioned, partitioned by date)</li>
    <li><strong>Store</strong> &mdash; RDS PostgreSQL with Alembic-managed 6-table yield schema</li>
    <li><strong>Compute</strong> &mdash; Lambda functions for spot curve bootstrapping, forward rates, Nelson-Siegel fitting</li>
    <li><strong>Deploy</strong> &mdash; Terraform IaC, GitHub Actions CI/CD with OIDC (no stored AWS keys)</li>
    <li><strong>Message</strong> &mdash; SQS/SNS for credit spread event processing, WebSockets for real-time streaming</li>
    <li><strong>Cache</strong> &mdash; ElastiCache Redis for bond price and yield curve caching</li>
    <li><strong>Monitor</strong> &mdash; CloudWatch dashboards and alarms</li>
    <li><strong>Analyse</strong> &mdash; OAS/Z-spread via binomial trees, default probability term structures, Monte Carlo Credit VaR</li>
  </ol>

  <h3>Tech Stack</h3>
  <table>
    <thead><tr><th>Layer</th><th>Technology</th></tr></thead>
    <tbody>
      <tr><td>Data Ingestion</td><td>S3, boto3, FRED API</td></tr>
      <tr><td>Database</td><td>RDS PostgreSQL, SQLAlchemy 2.0 async, Alembic</td></tr>
      <tr><td>Compute</td><td>Lambda, API Gateway (REST + WebSocket)</td></tr>
      <tr><td>Infrastructure</td><td>Terraform (modules, state, workspaces)</td></tr>
      <tr><td>CI/CD</td><td>GitHub Actions, OIDC, automated Lambda deploys</td></tr>
      <tr><td>Messaging</td><td>SQS, SNS, DynamoDB (WebSocket connections)</td></tr>
      <tr><td>Caching</td><td>ElastiCache Redis, cache-aside pattern</td></tr>
      <tr><td>Monitoring</td><td>CloudWatch (metrics, alarms, dashboards)</td></tr>
      <tr><td>Quantitative</td><td>NumPy, SciPy (Nelson-Siegel, Cholesky), Monte Carlo</td></tr>
    </tbody>
  </table>

  <h2>Exercises That Built This Project</h2>
  <table>
    <thead>
      <tr><th>#</th><th>Topic</th><th>Key Concepts</th><th>Pipeline Role</th></tr>
    </thead>
    <tbody>
      <tr><td>07</td><td><a href="{{ "/tech-stack/docker-for-python-services/" | relative_url }}">Docker</a></td><td>Multi-stage builds, compose</td><td>Container orchestration for local dev</td></tr>
      <tr><td>09</td><td><a href="{{ "/tech-stack/aws-fundamentals-treasury-data/" | relative_url }}">AWS Fundamentals</a></td><td>IAM, FRED API, yield classification</td><td>Foundation &mdash; credentials, data source</td></tr>
      <tr><td>10</td><td><a href="{{ "/tech-stack/s3-par-curve-ingestion/" | relative_url }}">S3 Ingestion</a></td><td>boto3, moto, versioned storage</td><td>Data lake for par curves</td></tr>
      <tr><td>11</td><td><a href="{{ "/tech-stack/rds-postgresql-yield-schema/" | relative_url }}">RDS &amp; Yield Schema</a></td><td>Alembic, seed from S3</td><td>Persistent yield curve storage</td></tr>
      <tr><td>12</td><td><a href="{{ "/tech-stack/lambda-spot-curve-bootstrapping/" | relative_url }}">Lambda &amp; Spot Curves</a></td><td>Serverless, API Gateway</td><td>On-demand spot curve computation</td></tr>
      <tr><td>13</td><td><a href="{{ "/tech-stack/cicd-forward-rate-curve/" | relative_url }}">CI/CD &amp; Forward Rates</a></td><td>GitHub Actions, OIDC</td><td>Automated deploy pipeline</td></tr>
      <tr><td>14</td><td><a href="{{ "/tech-stack/terraform-nelson-siegel/" | relative_url }}">Terraform &amp; Nelson-Siegel</a></td><td>IaC, curve fitting</td><td>Declarative infra + smooth curves</td></tr>
      <tr><td>15</td><td><a href="{{ "/tech-stack/sqs-sns-credit-spreads/" | relative_url }}">SQS/SNS &amp; Credit Spreads</a></td><td>Event-driven, CDS, hazard rates</td><td>Async credit spread processing</td></tr>
      <tr><td>16</td><td><a href="{{ "/tech-stack/websockets-realtime-spreads/" | relative_url }}">WebSockets</a></td><td>Real-time streaming, DynamoDB</td><td>Live spread updates to clients</td></tr>
      <tr><td>17</td><td><a href="{{ "/tech-stack/elasticache-bond-caching/" | relative_url }}">ElastiCache &amp; Caching</a></td><td>Redis, TTL, cache-aside</td><td>Bond price and curve caching</td></tr>
      <tr><td>18</td><td><a href="{{ "/tech-stack/terraform-advanced-default-probs/" | relative_url }}">Terraform Advanced</a></td><td>Modules, default probabilities</td><td>Survival curves, expected loss</td></tr>
      <tr><td>19</td><td><a href="{{ "/tech-stack/cloudwatch-oas-zspreads/" | relative_url }}">CloudWatch &amp; OAS</a></td><td>Binomial trees, callable bonds</td><td>Bond pricing with embedded options</td></tr>
      <tr><td>20</td><td><a href="{{ "/tech-stack/integration-testing-credit-var/" | relative_url }}">Credit VaR</a></td><td>Monte Carlo, Cholesky, correlation</td><td>Portfolio-level credit risk</td></tr>
    </tbody>
  </table>
</div>

<div id="tab-links" class="ql-tab-content" style="display:none">
  <h2>Related Posts</h2>
  <ul>
    <li><a href="{{ "/quant-lab/phase2-explained/" | relative_url }}">Phase 2 Explained</a> &mdash; every AWS service and finance formula, from scratch</li>
    <li><a href="{{ "/quant-lab/phase1-explained/" | relative_url }}">Phase 1 Explained</a> &mdash; the Python foundations that precede this arc</li>
  </ul>
</div>
```

- [ ] **Step 2: Commit**

```bash
cd c:/codebase/finbytes_git
git add docs/_quant_lab/aws-credit-risk.html
git commit -m "feat: add Phase 2 AWS & Credit Risk capstone page"
```

---

### Task 9: Create D3.js graph homepage

**Files:**
- Create: `docs/index.html`

- [ ] **Step 1: Create the graph homepage**

Create `docs/index.html`:

```html
---
layout: default
title: Home
permalink: /
---

<style>
.graph-lede {
  color: var(--text-muted-color, #666);
  font-size: .95rem;
  margin-bottom: 1.5rem;
  max-width: 580px;
  line-height: 1.7;
}
.graph-container {
  width: 100%;
  height: 70vh;
  min-height: 400px;
  border: 1px solid var(--border-color, #e8e8e8);
  border-radius: 8px;
  overflow: hidden;
  background: var(--main-bg, #fff);
}
.graph-container svg { width: 100%; height: 100%; }
.graph-tooltip {
  position: absolute;
  padding: 6px 10px;
  background: var(--card-bg, #fff);
  border: 1px solid var(--border-color, #ddd);
  border-radius: 4px;
  font-size: .82rem;
  pointer-events: none;
  opacity: 0;
  transition: opacity 0.15s;
  box-shadow: 0 2px 8px rgba(0,0,0,0.1);
  max-width: 280px;
}
.graph-legend {
  display: flex;
  flex-wrap: wrap;
  gap: 1rem;
  margin-top: 1rem;
  font-size: .78rem;
  color: var(--text-muted-color, #888);
}
.graph-legend-item {
  display: flex;
  align-items: center;
  gap: .35rem;
}
.graph-legend-dot {
  width: 10px;
  height: 10px;
  border-radius: 50%;
  display: inline-block;
}
</style>

<p class="graph-lede">Explore FinBytes &mdash; click any topic to dive in.</p>

<div class="graph-container" id="graph"></div>
<div class="graph-tooltip" id="tooltip"></div>

<div class="graph-legend">
  <span class="graph-legend-item"><span class="graph-legend-dot" style="background:#4a90d9"></span> Python</span>
  <span class="graph-legend-item"><span class="graph-legend-dot" style="background:#2ea043"></span> Tech Stack</span>
  <span class="graph-legend-item"><span class="graph-legend-dot" style="background:#e8893c"></span> Math / Finance</span>
  <span class="graph-legend-item"><span class="graph-legend-dot" style="background:#a371f7"></span> Comparisons</span>
  <span class="graph-legend-item"><span class="graph-legend-dot" style="background:#e24a4a"></span> Quant Lab</span>
</div>

<script src="https://d3js.org/d3.v7.min.js"></script>
<script>
(function() {
  // ── Data generated by Jekyll/Liquid ──
  const posts = [
    {% for post in site.posts %}
    {
      id: {{ forloop.index }},
      title: {{ post.title | jsonify }},
      url: "{{ post.url | relative_url }}",
      tags: {{ post.tags | jsonify }},
      section: {{ post.section | default: "" | jsonify }},
      permalink: {{ post.permalink | default: post.url | jsonify }}
    }{% unless forloop.last %},{% endunless %}
    {% endfor %}
  ];

  // ── Assign sections from permalink prefix ──
  function getSection(p) {
    if (p.section === "math-finance" || p.permalink.startsWith("/math-finance")) return "math-finance";
    if (p.section === "comparisons" || p.permalink.startsWith("/comparisons")) return "comparisons";
    if (p.permalink.startsWith("/quant-lab")) return "quant-lab";
    if (p.permalink.startsWith("/tech-stack")) return "tech-stack";
    if (p.permalink.startsWith("/python")) return "python";
    if (p.section === "infrastructure") return "tech-stack";
    if (p.section === "testing" || p.section === "python") return "python";
    return "python";
  }

  const colorMap = {
    "python": "#4a90d9",
    "tech-stack": "#2ea043",
    "math-finance": "#e8893c",
    "comparisons": "#a371f7",
    "quant-lab": "#e24a4a"
  };

  // ── Build nodes ──
  const nodes = posts.map(p => ({
    id: p.id,
    title: p.title,
    url: p.url,
    section: getSection(p),
    tags: p.tags || [],
    color: colorMap[getSection(p)] || "#999"
  }));

  // ── Build edges: posts sharing 2+ tags ──
  const links = [];
  for (let i = 0; i < nodes.length; i++) {
    for (let j = i + 1; j < nodes.length; j++) {
      const shared = nodes[i].tags.filter(t => nodes[j].tags.includes(t));
      if (shared.length >= 2) {
        links.push({ source: nodes[i].id, target: nodes[j].id, weight: shared.length });
      }
    }
  }

  // ── D3 force simulation ──
  const container = document.getElementById("graph");
  const width = container.clientWidth;
  const height = container.clientHeight;
  const tooltip = document.getElementById("tooltip");

  const svg = d3.select("#graph").append("svg")
    .attr("viewBox", [0, 0, width, height]);

  const g = svg.append("g");

  // Zoom
  svg.call(d3.zoom()
    .scaleExtent([0.3, 4])
    .on("zoom", (event) => g.attr("transform", event.transform)));

  const simulation = d3.forceSimulation(nodes)
    .force("link", d3.forceLink(links).id(d => d.id).distance(80).strength(0.3))
    .force("charge", d3.forceManyBody().strength(-120))
    .force("center", d3.forceCenter(width / 2, height / 2))
    .force("collision", d3.forceCollide().radius(12));

  // Links
  const link = g.append("g")
    .selectAll("line")
    .data(links)
    .join("line")
    .attr("stroke", "var(--border-color, #ddd)")
    .attr("stroke-opacity", 0.4)
    .attr("stroke-width", d => Math.min(d.weight * 0.5, 2));

  // Nodes
  const node = g.append("g")
    .selectAll("circle")
    .data(nodes)
    .join("circle")
    .attr("r", 7)
    .attr("fill", d => d.color)
    .attr("stroke", "var(--main-bg, #fff)")
    .attr("stroke-width", 1.5)
    .style("cursor", "pointer")
    .on("mouseover", function(event, d) {
      tooltip.style.opacity = 1;
      tooltip.textContent = d.title;
      tooltip.style.left = (event.pageX + 12) + "px";
      tooltip.style.top = (event.pageY - 10) + "px";
      d3.select(this).attr("r", 10).attr("stroke-width", 2.5);
    })
    .on("mousemove", function(event) {
      tooltip.style.left = (event.pageX + 12) + "px";
      tooltip.style.top = (event.pageY - 10) + "px";
    })
    .on("mouseout", function() {
      tooltip.style.opacity = 0;
      d3.select(this).attr("r", 7).attr("stroke-width", 1.5);
    })
    .on("click", function(event, d) {
      window.location.href = d.url;
    })
    .call(d3.drag()
      .on("start", (event, d) => { if (!event.active) simulation.alphaTarget(0.3).restart(); d.fx = d.x; d.fy = d.y; })
      .on("drag", (event, d) => { d.fx = event.x; d.fy = event.y; })
      .on("end", (event, d) => { if (!event.active) simulation.alphaTarget(0); d.fx = null; d.fy = null; }));

  simulation.on("tick", () => {
    link
      .attr("x1", d => d.source.x)
      .attr("y1", d => d.source.y)
      .attr("x2", d => d.target.x)
      .attr("y2", d => d.target.y);
    node
      .attr("cx", d => d.x)
      .attr("cy", d => d.y);
  });
})();
</script>
```

- [ ] **Step 2: Commit**

```bash
cd c:/codebase/finbytes_git
git add docs/index.html
git commit -m "feat: add D3.js force-directed graph as site homepage"
```

---

### Task 10: Verify and test

- [ ] **Step 1: Build Jekyll locally to verify no broken links**

```bash
cd c:/codebase/finbytes_git/docs
bundle exec jekyll serve
```

Check:
- Homepage at `/` shows the graph with nodes and edges
- Clicking a node navigates to the correct post
- Python tab at `/python/` lists only exercises 01–06, 08 with clean links
- Tech Stack tab at `/tech-stack/` lists references + exercises 07, 09–20
- Quant Lab tab at `/quant-lab/` shows both capstone sections and explainer links
- Phase 2 capstone at `/quant-lab/aws-credit-risk/` renders correctly
- All old `/2026/...` and `/misc/...` URLs return 404 (confirming old URLs are gone)
- Math/Finance and Comparisons tabs are unchanged

- [ ] **Step 2: Spot-check cross-links**

Verify these specific links work:
- From Stock Risk Scanner capstone → exercise posts (lines 60-67)
- From S3 exercise → AWS Fundamentals exercise (cross-link)
- From FastAPI exercise → Pydantic exercise (cross-link)
- From Phase 1 capstone section → Phase 1 Explained post
