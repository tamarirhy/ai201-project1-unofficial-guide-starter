# The Unofficial Guide — Project 1

> **How to use this template:**
> Complete each section *after* you've built and tested the corresponding part of your system.
> Do not write placeholder text — if a section isn't done yet, leave it blank and come back.
> Every section below is required for submission. One-liners will not receive full credit.

---

## Domain

<!-- What topic or category of knowledge does your system cover?
     Why is this knowledge valuable, and why is it hard to find through official channels?
     Example: "Student reviews of CS professors at [university] — useful because official
     course descriptions don't reflect teaching style, exam difficulty, or workload." -->
College student off-campus housing experiences in Atlanta, Georgia. This knowledge is valuable because housing strongly affects student's cost of living, safety, academic performance, and overall college experience. It is hard to find through official channels because universities only provide formal housing information, while real student experiences are spread across Reddit, reviews, social media, and informal discussions.
---

## Document Sources

<!-- List every source you collected documents from.
     Be specific: include URLs, subreddit names, forum thread titles, or file names.
     Aim for variety — sources that together cover different subtopics or perspectives. -->

| # | Source | Description | URL or location |
|---|--------|-------------|-----------------|
| 1 | Reddit | Quality off-campus housing for graduate students, some lists of what people value in where they're living. | https://www.reddit.com/r/gatech/comments/1k55yq7/what_are_some_good_offcampus_housing_options_for/ |
| 2 | Rambler | In depth information on cost of living near georgia tech in midtown (2026).| https://rambleratlanta.com/resources/whats-the-cost-of-living-near-georgia-tech-in-atlanta-midtown/ | 
| 3 | Reddit | Discusses college apartment experiences with lists of student housing in Atlanta available. | https://www.reddit.com/r/ATLHousing/comments/1d0jivo/whats_your_college_apartment_story_what_would_you/ |
| 4 | Yelp | Reviews on a specific student housing apartment in midtown, provides pictures and explanations. | https://www.yelp.com/biz/university-house-midtown-atlanta-4#reviews |
| 5 | Apartments | Provides list and picures of housing in the Atlantic station area, map to show location, provides pricing, restrictions, apartment availability, and more. | https://www.apartments.com/atlantic-station-atlanta-ga/student-housing/ |
| 6 | Apartment Ratings | Reviews on Wemstmar Student Apartments | https://www.apartmentratings.com/ga/atlanta/westmar-student-lofts_404897100330318/?page=8 |
| 7 | Apartment Ratings| List of apartments with alphabetical ratings, reviews, rank in the city, floor plans available, etc. | https://www.apartmentratings.com/ga/30318/ |
| 8 | Amber Blog | Provides budgeting and moving tips, cost of: rent, neighborhood, utilities, tansportation, health and insurance, food/groceries, enterainment, miscellaneous, etc. | https://amberstudent.com/blog/post/cost-of-living-in-atlanta-ga-budgeting-moving-tips |
| 9 | Ellen Cook | A guide on how life is living in Midtown Atlanta, FAQs, what to expect, general housing options, getting around Midtown, food options, arts, etc. | https://ellencookatlanta.com/blog/what-its-like-to-live-in-midtown-atlanta |
| 10 | Apartment List | Summaries of the best college neighborhoods | https://www.apartmentlist.com/renter-life/atlanta-college-neighborhoods |

---

## Chunking Strategy

<!-- Describe your chunking approach with enough specificity that someone else could reproduce it.
     Include:
     - Chunk size (characters or tokens) and why that size fits your documents
     - Overlap size and why (or why not) you used overlap
     - Any preprocessing you did before chunking (e.g., stripping HTML, removing headers)
     - What your final chunk count was across all documents -->

**Chunk size:**
700
**Overlap:**
100
**Why these choices fit your documents:**
These choices fit my documents because they consist of student housing reviews, apartment listings, and blog-style narratives that often contatin multiple related details within a single paragraph. The chunk size and overlap improves retrieval accuracy while keeping chunks small enough for semantic search to distinguish between different apartments, neighborhoods, and experiences. 
**Final chunk count:**
447
---

## Embedding Model

<!-- Name the embedding model you used and explain your choice.
     Then answer: if you were deploying this system for real users and cost wasn't a constraint,
     what tradeoffs would you weigh in choosing a different model?
     Consider: context length limits, multilingual support, accuracy on domain-specific text,
     latency, and local vs. API-hosted. -->

**Model used:**
all-MiniLM-L6-v2
**Production tradeoff reflection:**
I chose this model for it's fast, lightweight, perforamnce and because it's is well suited for semantic search on short to medium length passages of text(like my dataset consists of). In a production setting, I would trade off speed and cost for higher retrieval accuracy by using a larger or more advanced embedding model, especially for better handling of nuanced or indirect queries. I would also conside models with stronger multilingual support, longer context handling, and better domain-soecific performance depending on the dataset scale and user needs.
---

## Grounded Generation

<!-- Explain how your system enforces grounding — how does it prevent the LLM from answering
     beyond the retrieved documents?
     Describe both your system prompt (what instruction you gave the model) and any structural
     choices (e.g., how you formatted the context, whether you filtered low-relevance chunks).
     Do not just say "I told it to use the documents" — show the actual instruction or explain
     the mechanism. -->

**System prompt grounding instruction:**
The model is instructed to answer only using the retrieved context, cite specific review snippets for each claim, avoid summarizing across multiple chunks unless the same idea apears repeatedly, and return "not enough information" when the context does not support the answer.
**How source attribution is surfaced in the response:**
Source attribution is handled by including the retrieved chunk metadata (source filename and chunk index) in the prompt context, and the model is instructed to list the sources used at the end of its response.

---

## Evaluation Report

<!-- Run your 5 test questions from planning.md through your system and record the results.
     Be honest — a partially accurate or inaccurate result that you explain well is more
     valuable than a suspiciously perfect result. -->

| # | Question | Expected answer | System response (summarized) | Retrieval quality | Response accuracy |
|---|----------|-----------------|------------------------------|-------------------|-------------------|
| 1 |Which apartment complexes in the dataset mention nearby shopping or retail access? |Apartment X has has the lowest listed rent at approximately $.. per month and is near ....(lists of retail). |The system failed to identify specific apartment complexes. It returned vague references to areas like Midtown and Tech Square and included unclear tokens (e.g., “govt_surveillance,” “Acoww123”), then stated that retail access was not explicitly mentioned and shifted into inference rather than extracting entities. |Off-target |Inaccurate |
| 2 |According to the Rambler article. what factors contribute to the cost of living near Georgia Tech? |Housing costs, utilities, transportation, food, and other living expenses are identified as major contributors. |The system correctly extracted cost drivers from the Rambler text such as housing type, unit size, amenities, and building features, but omitted broader expected categories like utilities, transportation, and food. |relevant |partially accurate |
| 3 |Based on the dataset, what amenities and features are commonly highlighted for student housing in the Atlantic Station area? |Gym, study spaces, washer & dryer, pool , parking, utilities included, and patios. |The system accurately retrieved amenities from apartment listings including fitness center, pool, in-unit laundry, clubhouse, and controlled access, all grounded in the dataset. |relevant |accurate |
| 4 |What neighborhoods are recommended for college students and why? |Buckhead, Midtown, West Midtown, Atlantic Station, Downtown due to their location, public transportation options, pricing, entertainment, diverse housing options, and more miscellaneous benefits. |The system only retrieved Buckhead and described it as upscale but expensive, missing other key neighborhoods and reasoning from the dataset. |partially relevant |partially accurate |
| 5 |What characteristics do students value when choosing off-campus housing in Atlanta? |Students commonly value affordability, quality, location, and safety. |The system returned a partial answer stating affordability, proximity to campus, and quality, but also claimed insufficient information overall and failed to consolidate all relevant characteristics from multiple sources. |partially relevant |partially accurate |

**Retrieval quality:** Relevant / Partially relevant / Off-target  
**Response accuracy:** Accurate / Partially accurate / Inaccurate

---

## Failure Case Analysis

<!-- Identify at least one question where retrieval or generation did not work as expected.
     Write a specific explanation of *why* it failed, tied to a part of the pipeline.

     "The answer was wrong" is not an explanation.

     "The relevant information was split across a chunk boundary, so retrieval returned
     only half the context — the model didn't have enough to answer correctly" is an explanation.

     "The embedding model treated the professor's nickname as out-of-vocabulary and returned
     results from an unrelated review" is an explanation. -->

**Question that failed:**
|Which apartment complexes in the dataset mention nearby shopping or retail access?
**What the system returned:**
- 1. The apartment complexes that mention nearby shopping or retail access are not explicitly stated, but some reviews mention proximity to certain areas that may imply shopping or retail access, such as "midtown amenities" (govt_surveillance), "tech square" (govt_surveillance), and "campus" (Acoww123). However, without direct mention of shopping or retail, this is an inference. 
- 2. Sources used: 
    - [Source: reddit1.txt] 
    - govt_surveillance 
    - Acoww123
**Root cause (tied to a specific pipeline stage):**
The failure comes from chunking/data quality issue, retrieval + embedding weakness, and generation over-interface.
**What you would change to fix it:**
I would improve cleaning by removing usernames, tags or system labels, increase the chunk structure quality to containcomplete descriptions, add retrieval filtering/reranking to prioritize chunks containing explicit entity mentions, and strengthen the prompt instruction to enforce "Only return explicility named entities, do NOT infer apartment locations"
---

## Spec Reflection

<!-- Reflect on how planning.md shaped your implementation.
     Answer both questions with at least 2–3 sentences each. -->

**One way the spec helped you during implementation:**
The spec helped structure my project into clear stages (ingestion, chunking, embedding adn retrieval, and generation), which made it easier to build and test each part separately. It also guided key desgn decisions like chunk sixe, overlap, and evaluation testing before moving to later milestones.
**One way your implementation diverged from the spec, and why:**
My implementation divereged in chunking because I shifted from simple fixed-sixe splitting to paragraph-aware chunking to preserve readability and context. I made this change because my dataset contained review-style text, and paragraph-based chunks improved retrieval quality comapared to fragmented sentences.

---

## AI Usage

<!-- Describe at least 2 specific instances where you used an AI tool during this project.
     For each: what did you give the AI as input, what did it produce, and what did you
     change, override, or direct differently?

     "I used Claude to help me code" is not sufficient.
     "I gave Claude my Chunking Strategy section from planning.md and asked it to implement
     chunk_text(). It returned a function using a fixed character split. I overrode the
     chunk size from 500 to 200 because my documents are short reviews, not long guides." -->

**Instance 1**
- *What I gave the AI:*
Help me design a strict grounding prompt for a RAG system about college off-campus housing in Atlanta. The model must only use retrieved context, must say ‘I don’t have enough information’ if the answer is not in the context, and must return answers with source attribution. Show me 2–3 versions (basic, strict, and very strict).”
- *What it produced:*
It generated a basic prompt including the model to answer using provied context, return "I don't have enough information" if the answer is not in the context, and include soruce attribution. Showed 2 versions(basic and strict)
- *What I changed or overrode:*
I strengthened the prompt to require strict grounding using only retrieved context, enforce citation of specific review snippets for every claim, prevent cross-review summariaztion unless explicitly supported, and standardize the output format to include both an answer and sources.

**Instance 2**

- *What I gave the AI:*
I gave Claude my milestone 3 chunking requirements and asked it to generate a document loading and chunking pipeline for my RAG system.
- *What it produced:*
It produced a Python script that laoded .txt files, cleaned HTML and metadata, and chunked text into fixed-sixe segments with overlap, then returned structured chunk dictionaries for embedding.
- *What I changed or overrode:*
With the help of ChatGPT, I modified the cleaning step to remove extra URL and review metadata more aggressively, and adjusted the hcunking behavior to better preserve full paragraphs so the retrieved chunks were more readable and less fragmented. 