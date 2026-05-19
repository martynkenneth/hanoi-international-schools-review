# Hanoi International Schools Review Platform Blueprint

## Vision
Build the most trusted parent decision platform for international schools in Hanoi by combining:
- transparent school comparisons,
- continuously updated promotions/scholarships,
- high-quality editorial guidance,
- and AI/LLM-friendly content architecture.

## Core Product Positioning
**For parents:** a free, trustworthy decision engine that saves time, money, and stress.

**For schools (B2B):** a performance-based visibility and lead-generation channel.

---

## 1) Must-Have Website Sections (Phase 1)

### 1.1 School Profile Pages (one page per school)
Each page should include:
- Hero photo + campus gallery.
- School quick facts (curriculum, ages, tuition range, location, language, accreditation).
- Admissions timeline and required documents.
- Parent-relevant pros/cons in plain language.
- Commute map and neighborhood guide.
- FAQs with concise answers (LLM-ready).
- “Latest verified offers” module (scholarships, fee waivers, sibling discounts).
- “Last verified on” timestamp.

### 1.2 Compare Schools Tool
- Side-by-side comparison for up to 4 schools.
- Compare: tuition, class size, curriculum, language support, facilities, special needs support, exam outcomes, university placements.
- Shareable comparison URL.

### 1.3 Promotions & Scholarships Hub
- Filter by age group, curriculum, district, deadline, discount type.
- “Verified offer” badge + source link.
- Countdown to deadline.
- “Potential savings calculator” (annual + multi-child).

### 1.4 Parent Resource Center
- City-specific admissions guides.
- Curriculum explainers (IB vs Cambridge vs AP).
- Visa/relocation checklist for expat families.
- School interview preparation checklist.

### 1.5 Lead Capture + Gated Discount Pages
- Lead form: name + email + child age + preferred district.
- Gated “active discount sheets” and downloadable eBook.
- Email delivery of personalized shortlist and new-offer alerts.

---

## 2) High-Impact Features to Make It the #1 Platform

### 2.1 Trust Features (critical for conversion)
- **Verification ladder:** self-reported, source-verified, school-confirmed.
- **Source transparency panel:** website URL + social URL + date captured.
- **Independent editorial notes** separate from sponsored placements.
- **Change log** on each school page (what changed and when).

### 2.2 Parent Decision Intelligence
- **Best-fit recommender quiz** (budget, curriculum preference, commute, learning style).
- **Tuition total-cost estimator** including hidden fees (enrollment, meals, uniforms, transport).
- **Admissions probability heuristic** (non-guaranteed but useful guidance).
- **Waitlist risk indicator** by season.

### 2.3 LLM / AI Search Optimization (AEO)
- Every school page should include:
  - question-based H2/H3 headings,
  - concise direct answers under each heading,
  - bullet lists with facts,
  - structured data (JSON-LD),
  - summary block (“If you only read 30 seconds…”).
- Add **FAQ schema**, **Organization schema**, **Offer schema**, and **Review schema** where applicable.
- Publish an **open data snapshot page** for AI crawlers with canonical facts and verification timestamps.

### 2.4 Community + Social Proof
- Verified parent testimonials by child age group.
- Anonymous “what we wish we knew before applying” snippets.
- Q&A forum with moderated expert responses.
- Parent ambassador program for each district.

### 2.5 B2B Revenue Features (without losing trust)
- Sponsored school slots clearly labeled.
- Cost-per-qualified-lead packages.
- Premium analytics dashboard for schools (impressions, saves, lead quality).
- “Promotion campaign manager” for schools to submit offers with expiry.
- SLAs for verification turnaround.

---

## 3) Data Collection & Freshness Engine

### 3.1 Offer Discovery Sources
- Official school websites (admissions/promotions/news pages).
- Official school social profiles (Facebook, Instagram, LinkedIn).
- School newsletters (optional ingestion).

### 3.2 Update Workflow
1. Crawl/scrape target sources on schedule.
2. Detect new/changed offer text.
3. Classify into scholarship, discount, waiver, event-based incentive.
4. Human moderation queue for high-confidence publication.
5. Publish with “verified at” timestamp and source links.

### 3.3 Data Confidence Scoring
- Confidence factors: source authority, recency, matching across channels, language clarity.
- Auto-expire offers after deadline.
- Flag stale offers for review.

---

## 4) Suggested Information Architecture

- `/hanoi/` city hub
- `/hanoi/schools/` directory
- `/hanoi/schools/{school-slug}` profile page
- `/hanoi/compare` comparison tool
- `/hanoi/promotions` all active offers
- `/hanoi/guides/{topic}` editorial guides
- `/ebook/international-schools-hanoi` gated lead magnet
- `/for-schools` B2B landing page

Future expansion:
- `/ho-chi-minh-city/...`
- `/bangkok/...`
- `/singapore/...`
- reusable city template + localized data pipelines.

---

## 5) SEO + LLM Content Template (per school page)

### Recommended section headings
- Is this school a good fit for my child?
- What are tuition and total annual costs?
- What scholarships or discounts are available now?
- What curriculum and university pathways are offered?
- What do parents like most and least?
- How competitive is admission?

### On-page content rules
- First 120 words answer top query directly.
- Each section starts with a 1-2 sentence summary.
- Use bullet points for factual details.
- Include an update timestamp and source links.
- Add FAQ block with 5-10 high-intent parent questions.

---

## 6) Lead Generation Funnel (Email + eBook)

### Lead Magnet Ideas
- “2026 Hanoi International School Fees & Discounts Handbook”.
- “Parent Checklist: 21 Questions to Ask Before Applying”.
- “Scholarship Deadlines Calendar”.

### Funnel Flow
1. User views school/promotions page.
2. CTA: “Unlock active discounts + fee savings tracker”.
3. Form capture (name, email, child age).
4. Instant access + email delivery.
5. Nurture sequence:
   - Day 0: eBook + shortlist tool.
   - Day 2: curriculum comparison guide.
   - Day 5: latest verified offers.
   - Day 8: call booking or concierge support.

---

## 7) Monetization Model

### Parent side
- Free core discovery and comparison.
- Optional premium concierge (paid) for personalized admissions support.

### School side (B2B)
- Featured profile subscriptions.
- Sponsored placements in comparison/promotions pages.
- Qualified lead bundles.
- Seasonal campaign add-ons (open day promotion, scholarship drives).

---

## 8) Trust, Ethics, and Compliance

- Clearly separate editorial rankings from paid promotions.
- Prominent disclosure labels on sponsored content.
- Data privacy compliance for lead capture (consent + unsubscribe).
- School data correction request workflow.
- No fake scarcity; show real deadlines and verification dates.

---

## 9) 12-Week Execution Roadmap

### Weeks 1-2
- Brand, positioning, data model, source list, school universe.

### Weeks 3-5
- Build directory, school templates, comparison engine, promotions hub.

### Weeks 6-7
- Implement verification workflow + moderation queue + confidence scoring.

### Weeks 8-9
- Launch lead magnet funnel, email automation, gated pages.

### Weeks 10-11
- SEO/AEO optimization (schema, FAQ, structured Q&A, page speed).

### Week 12
- Launch, analytics baseline, sponsor outreach kit.

---

## 10) KPI Dashboard (What to Track)

### Parent value KPIs
- Monthly active users.
- Offer click-through rate.
- Comparison tool usage rate.
- Email signup conversion rate.
- Time to shortlist decision.

### B2B KPIs
- Qualified leads per school.
- Lead-to-visit and visit-to-enrollment estimates.
- Sponsored listing ROI.
- Offer campaign engagement.

### Content trust KPIs
- % offers verified within 7 days.
- % pages updated in last 30 days.
- User-reported inaccuracies.

---

## 11) Recommended Next Build Items (Priority)
1. School profile template with “latest verified offers” component.
2. Promotions database + expiry logic + source citation block.
3. Comparison table MVP.
4. Gated eBook landing page + email capture.
5. FAQ-rich content templates for LLM discoverability.
6. Sponsored listing framework with compliance labels.

This blueprint is designed to make the platform defensible through trust + freshness + decision utility, while monetizing sustainably through B2B partnerships.
