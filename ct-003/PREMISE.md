# ct-003 premise check

Date: 19 Nov 2026. Result: **GO**. The topic is AI job titles: which titles that name AI or machine learning
companies actually post, and how often. Our job index answers it from the titles of 461,985 open jobs on 23,287
company job boards. The top Google results are lists of roles with salary ranges, a LinkedIn post that relays other
sites' figures, and two essays. None of them counts titles in job postings.

## How the topic was chosen

The brief asks for a topic chosen by search demand, built only from our own index data, and different from ct-001
(crawl reliability) and ct-002 (posting day and hour). The index holds, per job: board (company name), title,
location, a remote flag and a posting time. Candidates were ranked in this order: what the data can answer without
bias, whether the top results already publish first-hand data, then demand. No keyword-volume tool is connected, so
demand is what Google itself shows (AI Overview, "People also ask", "People also search for", pages targeting the
query). No volume figures are claimed.

| Candidate | Valid from our index? | Top results | Verdict |
|---|---|---|---|
| ATS market share among hiring companies | **No.** Board counts per ATS follow what our discovery found and what each ATS let us crawl (Workable answered for 3,681 of 10,785 boards on 19 Nov). The index has none of Workday, iCIMS or SmartRecruiters | Not read (ct-002 premise reached the same verdict) | Dropped |
| Where tech companies post jobs | **No**, for the same reason: it asks for shares across ATSs and other channels (LinkedIn, Indeed), and the index covers six ATSs only | Not read | Dropped |
| Remote share by ATS | **Weak.** `remote` comes from a vendor field on Lever, Ashby, Recruitee and Workable and from the word "remote" in the location on Greenhouse and Personio (Workable: 24.1% flagged, 3.6% by the word in title or location). Shares across ATSs would compare definitions | `what percentage of jobs are remote` (Google, 19 Nov): 1 Minneapolis Fed, 2 Robert Half (its own analysis of job postings, Q3 2026), 3 Reddit. Two of three are first-hand data | Dropped: invalid across ATSs, and no originality edge |
| **AI job titles** | **Yes.** A title is the employer's own text. The share of titles that name AI within one ATS's boards, the role names used, their seniority words and their locations do not depend on how many boards of each ATS we found. Cross-ATS totals are stated as "these boards", not the market | `ai job titles`: see below | **Chosen** |

Demand evidence for `ai job titles` (Google, US English, `hl=en&gl=us&pws=0`, read three times on 19 Nov 2026; the
top 8 organic results were the same, in the same order, every time):
- an AI Overview answers it with a grouped list of titles, citing Syracuse iSchool, Drew Breunig and ivanturkovic.com;
- "People also ask": "What are the top 10 AI jobs?", "What is a $900000 AI job?", "What types of AI jobs are
  there?", "What job titles are AI proof?";
- "People also search for" lists eight variants, including "Ai job titles list", "AI job roles", "Best AI jobs for
  beginners" and "Entry level AI jobs salary";
- pages updated in 2026 target it (Georgia Tech, 14 May 2026; Syracuse, 25 Feb 2026; ivanturkovic.com, 24 Apr 2026,
  updated Nov 2026).

## Target query and reader

- **Query:** `ai job titles`. Related questions the page also answers: which AI titles are most common, how many
  open jobs name AI, what share are entry-level, and what "AI trainer" and "forward deployed engineer" listings are.
- **Reader:** a job seeker deciding which titles to search for and which listings are what they seem; a recruiter or
  hiring manager naming a role. Secondary, suited to this site: a developer classifying job titles in a job feed.

## Top results (organic; the AI Overview, "People also ask" and the Reddit thread at #5 are not counted)

| # | Page | What it gives the reader | What it does not have |
|---|---|---|---|
| 1 | pe.gatech.edu/blog/industry-trends/careers-in-ai ("10 Essential Careers in AI", 14 May 2026) | Ten roles (ML engineer, data scientist, AI research scientist, AI product manager, robotics engineer, AI ethics specialist...) with a paragraph each; cites McKinsey (88% of enterprises use AI) and a Resume Genius survey; promotes the school's courses | No count of any title in job postings; several of its ten (BI developer, algorithm developer, data mining) are not AI-named titles; no locations, seniority or dates |
| 2 | ischool.syracuse.edu/highest-paying-ai-jobs ("10 Highest-Paying AI Jobs & Salaries in 2026", 25 Feb 2026) | Ten roles with salary ranges (unsourced), skills and barriers to entry; one sourced figure (35,445 open US AI roles in Q1 2025); promotes the school's master's degree | No count per title; salary ranges have no source or date; the list is ordered by pay, not by how often employers post the title |
| 3 | linkedin.com/posts/adamrbroda_most-folks-dont-know-ai-created-13m-new-... (career coach's post, about 5 months old) | Ten "titles on the rise", each with a figure taken from LinkedIn Jobs on the Rise, Glassdoor, Indeed, WEF and vendor blogs | Every figure is second-hand and from a different source and date, so they cannot be compared; no method |
| 4 | dbreunig.com/2025/08/21/a-guide-to-ai-titles.html ("Making Sense of AI Job Titles", 21 Aug 2025) | A "decoder ring": modifier (Forward Deployed, Applied) + domain (AI, ML, Gen AI) + role (Engineer, Researcher, Architect), with quoted job descriptions | Illustrative examples, no counts; its claims (for example that "Applied" is becoming the corporate title) are untested |
| 7 | ivanturkovic.com/2026/04/24/ai-job-titles-2026-naming-chaos (CTO essay, 24 Apr 2026, updated Nov 2026; cited in the AI Overview) | 35 titles the author saw in a week; "10 worth hiring for" and "10 that are mostly theater", with pay figures from Levels.fyi, Glassdoor and press reports; predicts most titles will collapse into "AI Engineer" | No counts of titles in postings; its claims ("Prompt Engineer peaked", "GenAI Engineer is a branding variant") are opinions our data can test |

Results 1 to 3 are the brief's top 3. Results 4 and 7 are added as harder comparisons on originality, because they
analyse title naming rather than list careers. The review compares five pages, as ct-002's did.

## What our page will have that they don't

All of it is measured from the job index that ATS Jobs Search built at 04:03 UTC on 19 Nov 2026 (Greenhouse, Lever,
Ashby, Recruitee, Personio, Workable). Exploration counts (the page uses the committed script's numbers): about 4.3%
of open jobs have a title that names AI or ML, on about 3,850 boards.

1. **The ranked list of AI-named titles employers actually use**, ranked by the number of company boards posting
   each title (seniority words and levels removed), with listings alongside. This answers "Ai job titles list" and
   "What are the top 10 AI jobs?" with counts.
2. **The guide titles, counted.** Every title the top results name (Prompt Engineer, LLM Engineer, GenAI Engineer,
   Evals Engineer, Chief AI Officer, AI Ethics Specialist...) with how many boards post it. Some guide titles barely
   appear.
3. **Role groups**: engineering, research, customer-facing (forward deployed, solutions), product, leadership,
   go-to-market, governance, and AI training and data work. A large share of AI-titled listings are freelance
   "AI trainer" and data-contributor listings, concentrated on a few boards; shown both by listings and by boards.
4. **Seniority**: the share of AI-titled listings with a senior word against a junior, intern or student word,
   compared with all listings (answers "entry level AI jobs").
5. **By ATS and region**: the share of each ATS's listings that name AI, and where AI-titled jobs are located
   (US, Europe, other) against all jobs.
6. **Forward Deployed Engineer**, the title the AI Overview and two of the results name: listings, boards, and how
   many of its titles name AI.
7. **A downloadable CSV/JSON and the script** that rebuilds every number from the index files (SHA-256 hashes).

## Limits to state on the page

- One snapshot of open jobs on 23,287 boards our crawler found on six ATSs, not every employer. Shares describe
  these boards. Employers on Workday, iCIMS and others are not covered.
- A title "names AI" when it contains one of a fixed list of terms (AI, ML, LLM, KI, NLP, GenAI, machine learning,
  deep learning, computer vision, agentic...). Titles such as "Research Scientist" or "Inference Engineer" with no
  such term are not counted, and an AI job with a plain title ("Software Engineer") is missed. The index has no job
  descriptions or salaries.
- Rules are keyword rules on the title text, committed in the script, so anyone can rerun or change them.
- Boards, not companies: some companies run more than one board. Copies (same title, location and posting time on
  two boards of one ATS) are counted once, as on the ct-002 page.
- Not covered: crawl reliability (ct-001) and posting day or hour (ct-002).
