# Project 1 Planning: The Unofficial Guide

> Write this document before you write any pipeline code.
> Your spec and architecture diagram are what you'll use to direct AI tools (Claude, Copilot, etc.) to generate your implementation — the more specific they are, the more useful the generated code will be.
> Update the Retrieval Approach and Chunking Strategy sections if you change your approach during implementation.
> Update this file before starting any stretch features.

---

## Domain

<!-- What domain did you choose? Why is this knowledge valuable and hard to find through official channels? -->
College student off-campus housing experiences in Atlanta, Georgia. This knowledge is valuable because housing strongly affects student's cost of living, safety, academic performance, and overall college experience. It is hard to find through official channels because universities only provide formal housing information, while real student experiences are spread across Reddit, reviews, social media, and informal discussions.
---

## Documents

<!-- List your specific sources: URLs, subreddit names, forum threads, or file descriptions.
     Aim for at least 10 sources that together cover different subtopics or perspectives within your domain. -->

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

<!-- How will you split documents into chunks?
     State your chunk size (in tokens or characters), overlap size, and explain why those
     numbers fit the structure of your documents.
     A review-heavy corpus warrants different chunking than a long FAQ. -->

**Chunk size:**
600 characters
**Overlap:**
100 reasoning
**Reasoning:**
The dataset consists of student housing reviews, apartment listings, and blog-style narratives that often contatin multiple related details within a single paragraph. The chunk size and overlap improves retrieval accuracy while keeping chunks small enough for semantic search to distinguish between different apartments, neighborhoods, and experiences. 
---

## Retrieval Approach

<!-- Which embedding model are you using (e.g., all-MiniLM-L6-v2 via sentence-transformers)?
     How many chunks will you retrieve per query (top-k)?
     If you were deploying this for real users and cost wasn't a constraint, what tradeoffs
     would you weigh in choosing a different embedding model — context length, multilingual
     support, accuracy on domain-specific text, latency? -->

**Embedding model:**
all-MiniLM-L6-v2
**Top-k:**
5
**Production tradeoff reflection:**
I chose all-MiniLM-L6-v2 because my dataset consists of mostly paragraph based text including reviews, blogs, and summaries. It's also fast, free, runs locally, and is well suited for semantic search on short passages of text. I chose a top-k value of 5 because I have a smaller dataset consiting of 10 documents. By doing this, the most relevant chunks will provide enough context for the LLM to generate an accurate repsonse without overwhelming it with unnecessary or unrealted information. If I were to deploy this system in production, i would consider retrieval accuracy, latency, and computational cost when selecting an embedding model.
---

## Evaluation Plan

<!-- List your 5 test questions with their expected correct answers.
     Questions should be specific enough that you can judge whether the system's response
     is right or wrong. "What are good dining halls?" is too vague.
     "What do students say about wait times at [dining hall name] during lunch?" is testable. -->

| # | Question | Expected answer |
|---|----------|-----------------|
| 1 | Which apartment complexes in the dataset mention nearby shopping or retail access? | Apartment X has has the lowest listed rent at approximately $.. per month and is near ....(lists of retail).|
| 2 | According to the Rambler article. what factors contribute to the cost of living near Georgia Tech?| Housing costs, utilities, transportation, food, and other living expenses are identified as major contributors. |
| 3 | Based on the dataset, what amenities and features are commonly highlighted for student housing in the Atlantic Station area? | Gym, study spaces, washer & dryer, pool , parking, utilities included, and patios.|
| 4 | What neighborhoods are recommended for college students and why? | Buckhead, Midtown, West Midtown, Atlantic Station, Downtown due to their location, public transportation options, pricing, entertainment, diverse housing options, and more miscellaneous benefits.|
| 5 | What characteristics do students value when choosing off-campus housing in Atlanta? | Students commonly value affordability, quality, location, and safety.|

---

## Anticipated Challenges

<!-- What could go wrong? Name at least two specific risks with reasoning.
     Consider: noisy or inconsistent documents, missing source attribution, off-topic
     retrieval, chunks that split key information across boundaries. -->

1. My dataset includes Reddit posts, apartement listings, and review websites, which all presents different styles of reliability. Reddit users may delete their posts or commentsand somem may be remove for violating the platforms guidelines, which could lead to missing or incomplete data in the dataset. Additionally, inconsistencies may be introduced during retrieval due to differences between subjetive opinions and factual information across sources.

2. Some documents contain key information within the same paragraph or section. If chuncking splits these details acrosss separate chunks, the retrieval system may return incomplete contecxt, leading to inaccurate or partially informed responses from the LLM.

---

## Architecture

<!-- Draw a diagram of your pipeline showing the five stages:
     Document Ingestion → Chunking → Embedding + Vector Store → Retrieval → Generation
     Label each stage with the tool or library you're using.
     You can use ASCII art, a Mermaid diagram, or embed a sketch as an image.
     You'll use this diagram as context when prompting AI tools to implement each stage. -->
     Documents (Reddit, Apartments.com, Reviews, Blogs)
                    │
                    ▼
        Document Ingestion (Python)
        - pdfplumber / requests / BeautifulSoup
                    │
                    ▼
            Chunking (Python)
        - 500–800 char chunks
        - 100–150 overlap
                    │
                    ▼
 Embeddings (sentence-transformers: all-MiniLM-L6-v2)
                    │
                    ▼
     Vector Store (ChromaDB)
                    │
                    ▼
     Retrieval (Top-k = 5 similarity search)
                    │
                    ▼
 LLM Generation (Groq: llama-3.3-70b-versatile)
                    │
                    ▼
 Answer with Source Attribution

---

## AI Tool Plan

<!-- For each part of the pipeline below, describe:
     - Which AI tool you plan to use (Claude, Copilot, ChatGPT, etc.)
     - What you'll give it as input (which sections of this planning.md, which requirements)
     - What you expect it to produce
     - How you'll verify the output matches your spec

     "I'll use AI to help me code" is not a plan.
     "I'll give Claude my Chunking Strategy section and ask it to implement chunk_text()
     with my specified chunk size and overlap" is a plan. -->

**Milestone 3 — Ingestion and chunking:**

I will use ChatGPT and Claude to help design and debug my document ingestion and chunking pipleline. I will provide my chunkign strategy section from planning.md and examples of raw text from my sources. I expetc assistance writing Python function to clean text, remove irrelevant sections, and split documents into 700 characters chunks with overlaps. I will verify correctnes by checking that chunks are consistent in size and preserve full ideas without cutting off important context.

**Milestone 4 — Embedding and retrieval:**

I will use ChatGPT and Claude to help implement embeddings using sentence transformers (all-MiniLM-L6-v2) and set up ChromaDB as the vector store. I will provide my chunked dataset and ask for guidance on embedding generation, indexing, and similarity search queries. I expect working code for storing embeddings and retriving the top-k (k=5) most relevant chunks for a query. I will verify correctness by testing retrieval results against known queries and checking whether returned chunks are semantically relevant. 
**Milestone 5 — Generation and interface:**

I will use Claude and ChatGPT to help build the final RAG pipeline that connects retrieval to the Groq LLM (llama-3.3-70b-versatile). I will provide retrieved chunks and prompt structure requirements and ask for help constructing a grounded prompt that forces the model to only use retrieved context. I expect a working interface (CLI or notebook) that accepts user queries and returens answers with source attribution. I will verify correctness by ensuring responses are based only on retrieved chunks and do not hallucinate information outside the dataset.

## Retrieval Evaluation Results
QUERY1: According to the Rambler article. what factors contribute to the cost of living near Georgia Tech?
============================================================

Rank 1: Rambler Article - irrelevant | chunk #25 | distance: 0.2704 - acceptable

Rank 2: Rambler Article - relevant| chunk #0 | distance: 0.2825 - acceptable

Rank 3: Rambler - relevant | chunk #24 | distance: 0.3287 - acceptable

Rank 4: Rambler - partially relevant | chunk #2 |distance: 0.3564 - acceptable

Rank 5: Rambler - irrelevant | chunk #1 | distance: 0.3832 - acceptable

============================================================
QUERY2: What neighborhoods are recommended for college students and why?
============================================================

Rank 1: aptlist.txt - irrelevant | chunk #2 | distance: 0.2114 - acceptable

Rank 2: aptlist.txt - relevant | chunk #20 | distance: 0.3301 - acceptable

Rank 3 | aptlist.txt - partially relevant| chunk #1 | distance: 0.3326 - acceptable

Rank 4: aptlist.txt - irrelevant | chunk #8 | distance: 0.3375 - acceptable

Rank 5: aptlist.txt - partially relevant| chunk #9 | distance: 0.3558 - acceptable

============================================================
QUERY3: What characteristics do students value when choosing off-campus housing in Atlanta?
============================================================

Rank 1: aptlist.txt - partially relevant| chunk #1 | distance: 0.2567 - acceptable

Rank 2: aptlist.txt - irrelevant| chunk #0 | distance: 0.2652 - acceptable

Rank 3: yelp.txt - partially| chunk #56 | distance: 0.2951 - acceptable

Rank 4: reddit1.txt - partial | chunk #0 | distance: 0.2995 - accept

Rank 5: aptlist.txt - irrelevant | chunk #8 | distance: 0.3177 - acceptable
Failure case: 
Some queries return summaries or introductory/marketing-style content instead of specific, actionable information. This happens because several chunks contain shallow or non-informative sections, which reduces the density of useful semantic signals. As a result, embeddings match on general topic similarity rather than specific intent, leading to less precise retrieval. 