# Query-related PR feedback: Graphify-Labs/graphify

Source: the GitHub PR pages fetched with WebFetch on 2026-11-03. Role badges were often not rendered in the fetched text. **safishamsi** is the code owner, is shown as "Member" where a badge was visible (#879, #3866, #1832, #1597, #2338), and is the maintainer throughout. "Not visible on page" means the fetched text did not show the item.

Bot reviews from graphify-labs[bot], github-actions[bot], Copilot and Qodo are summarised in one line each.

Many maintainer "closed" PRs were not merged through GitHub. The maintainer cherry-picked or re-applied them onto `v8` with the author's authorship kept. They are marked **closed (landed via cherry-pick)** below.

---

## #3417 fix(query): emit the ranking it already computes — ANSWER block, camelCase sub-words, test demotion, honest truncation
- **State:** open. **Author:** rek.
- **Change:**
  - Adds an ANSWER block with the top 5 nodes, a `rel=` score per node, matched-term reasons and source lines.
  - Adds a camelCase/PascalCase/SNAKE sub-word tier and plural folding.
  - Down-weights test, fixture, generated, vendor, config and archive paths.
  - Caps zero-match nodes at 15 under a budget, and rewrites the truncation and low-confidence messages.
  - The sort key moved from `(hop,-rel,…)` to relevance-primary `(-relevance, hop, -degree, id)`.
- **Human comments:**
  - rek (author, Sep 8, 2026) wrote the description. It calls the ranking "invisible, not absent" and says the #3284 sort-key choice is "the maintainer's call". It reports 24 failures that are also present on pristine v8.
  - No maintainer comment. The only participant is the author.
- **Bot:** graphify-labs[bot] posted two "Worth a look" reviews, gate PASS, advisory and unverified. Findings: the relevance weight is not applied to the final score, snippets can read files outside the graph root, the legacy collision count uses raw paths, and IDF is applied twice for a per-term singleton.

## #2403 feat(query): exclude test paths from default seeds
- **State:** open. **Author:** zrh805. Fixes #2381.
- **Change:**
  - Excludes `tests/` and nested test paths from initial seed selection only.
  - Adds `--seed-ignore`, `GRAPHIFY_QUERY_IGNORE_PATTERNS` and MCP `seed_ignore_patterns`.
  - Retries unfiltered if every match was excluded.
- **Human comments:**
  - zrh805 (author, Aug 2) replied about hardening non-list input.
  - No maintainer comment.
- **Bot:** graphify-labs[bot] gave three "Looks safe to merge" reviews. They flagged one medium item, raw non-list MCP input, which the author fixed, and an `_score_query` coupling note.

## #3284 fix(query): rank same-hop nodes by query relevance before degree under the budget
- **State:** open. **Author:** andytsai821201-spec.
- **Change:** Passes the `_score_query` ranking into `_subgraph_to_text` as the sort key `(hop, -score, -degree, id)`. No new scoring pass or flag.
- **Human comments:**
  - rek (contributor, Sep 8, 2026) reported the same problem on a 51k-node TypeScript graph. Their #3417 adopted the same key. rek noted that camelCase identifiers stay a single token. "Not a request for anything here."
  - rek (Sep 8, correction) said #3417 switched to relevance-primary `(-relevance, hop, -degree, id)`. "A genuine disagreement about one key, not a composition." rek offered to drop their key if the maintainers prefer hop-primary.
  - No maintainer comment.
- **Bot:** graphify-labs[bot] said "Looks safe to merge", PASS.

## #3636 feat(query): add a body attribute tier so query seeding can reach non-extraction content (#3313)
- **State:** open. **Author:** ayushcodes10.
- **Change:**
  - Adds a `body` attribute tier at 0.35, below rationale at 0.75, in `_score_query` and `_node_search_text`. It does not count toward coverage.
  - A later commit makes `extract_markdown` derive `body` from the frontmatter `description` or `summary`.
- **Human comments:**
  - sortakool (contributor, Oct 4, 2026) said frontmatter `description` is never searched on their 379-file vault. They asked for either `extract_markdown` to emit a capped `body` or for the tier to read frontmatter. They preferred option 1, which "keeps the single documented convention".
  - ayushcodes10 (author, Oct 9) adopted option 1 and added 5 tests.
  - safishamsi was requested as reviewer and is "awaiting requested review". No maintainer comment.
- **Bot:**
  - graphify-labs[bot] said "Looks safe to merge" and noted a `_node_search_text` coupling note.
  - github-actions[bot] asked for a conventional-commit title. The title was later fixed.

## #4601 fix(query): weight seed scoring by file type so captions don't drown out code
- **State:** open. **Author:** ayushcodes10.
- **Change:** Multiplies the query and seed score by file type: code, concept and rationale ×1.0, document and paper ×0.7, image ×0.4.
- **Human comments:**
  - Only the author's description, which says the change "narrows, rather than eliminates, the gap".
  - safishamsi was requested and is "awaiting requested review". No maintainer comment.
- **Bot:**
  - graphify-labs[bot] gave PASS with one medium finding: the multiplier can demote exact image or doc label matches below non-exact code matches (serve.py:759).
  - github-actions[bot] posted a welcome message.

## #4481 feat(query): a natural-language question leads with its best-matching file (#4480)
- **State:** open. **Author:** devkancheti4-design.
- **Change:**
  - For queries of 3 or more terms, the first seed becomes the best node of the file whose top-50 candidates have the highest summed score.
  - Tests lead only when asked for. Shorter queries are unchanged.
  - The author reports SWE-bench Lite gains.
- **Human comments:**
  - devkancheti4-design (author, Oct 21) wrote to @safishamsi. They pitched porting "Model D" ideas, cited 25 to 41 of 120 right-file-first, and wrote "I'd like the title of core performance engineer on Graphify." No reply.
  - safishamsi was requested and is awaiting review. No maintainer comment.
- **Bot:**
  - graphify-labs[bot] reported no blocking issues and flagged `_query_graph_text` as a coupling hotspot with 51 callers.
  - github-actions[bot] posted a welcome message.

## #3866 feat(mcp): improve retrieval quality with phrase bonus, community coherence, and evidence-first truncation (#3810)
- **State:** open. **Author:** nikhilsaxena04.
- **Change:**
  - Adds a contiguous 2- and 3-word phrase bonus in `_score_query`.
  - Adds a majority-community preference in `_pick_seeds`.
  - Puts shortest-path nodes between seeds first in `_subgraph_to_text`, so they survive truncation.
- **Human comments:**
  - nikhilsaxena04 (author, Sep 26) said dropping top seeds is "intentional and by design!" because of a 20% gap threshold.
  - **safishamsi (Member, Oct 6, 2026)** listed blockers:
    1. The parity test was altered so it "silently skips the per-term assertion".
    2. The community filter can discard the top-scored seed.
    - Non-blocking: use the induced subgraph for shortest paths, and split the three heuristics into separate PRs. He will re-review once 1 and 2 are fixed.
  - **safishamsi (Member, Oct 12, 2026)** raised five points:
    - The community filter doesn't exclude the cross-domain seed, because the per-term guarantee re-appends it.
    - Don't mute the parity test.
    - **A before/after retrieval benchmark is needed for ranking changes.**
    - Shortest-path evidence can silently no-op on directed graphs.
    - Rebase and clean up whitespace.
  - nikhilsaxena04 (Oct 13) said everything was addressed: scoped community filter, protected top seed, test bypass removed, undirected induced subgraph, rebased. The benchmark shown measures runtime speedups (1.35 to 1.71x) only, not ranking quality.
  - No maintainer response after Oct 13 is visible.
- **Bot:** graphify-labs[bot] gave two reviews. Findings: the community reorder can drop a per-term guaranteed seed (high), the phrase bonus crosses word boundaries (medium), and `_pick_seeds` no longer returns the top seeds.

## #2294 fix(query): score the `rationale` attribute, not just labels (#2293)
- **State:** open. It targets `main`, and the branch history has about 1,300 unrelated commits. **Author:** nuboxworld-byte.
- **Change:**
  - Adds a rationale tier at 0.75, between substring 1.0 and source 0.5.
  - Adds rationale to the singleton score and the trigram prefilter.
  - Not counted for coverage. `_pick_seeds` is untouched.
- **Human comments:**
  - None besides the author's description. "No reviews".
  - Cross-references: #3288 by andytsai821201-spec (Sep 2), and a safishamsi commit referencing this PR (Sep 5). The idea landed via #3288 in v0.9.54.
- **Bot:** none visible.

## #2975 fix(query): downweight rationale prefix seeds
- **State:** open. **Author:** hopstreax.
- **Change:** Adds a rationale-only prefix factor of 0.01 in `_score_query`, so docstring prefix hits stop outranking code. Example: "what computes ROAS" now leads with `roas_report`.
- **Human comments:** None. Only a cross-reference from #3288. No maintainer comment.
- **Bot:** graphify-labs[bot] said "Looks safe to merge", PASS, with `_score_query` unverified.

## #2113 fix: bound per-term query seed recovery
- **State:** open. **Author:** juanyque. Authored with Codex.
- **Change:**
  - Caps per-term seed recovery in `_pick_seeds` at `max_k`.
  - Prefers higher term coverage, then score, label length and id.
- **Human comments:** None. "No reviews". No maintainer comment.
- **Bot:** none visible.

## #3285 feat(query): surface bridge nodes reached from two or more seeds
- **State:** open. **Author:** andytsai821201-spec.
- **Change:**
  - Adds `_bridge_nodes`, which finds non-seed nodes reached from 2 or more seeds within the traversed set.
  - Adds a `Bridges:` header and renders bridges right after the seeds.
- **Human comments:** Author's description only. No maintainer comment.
- **Bot:** graphify-labs[bot] said "Looks safe to merge", PASS, with coupling notes.

## #2376 fix(serve): reserve budget for EDGE lines so query answers keep relations
- **State:** open. **Author:** nicknikolakakis.
- **Change:**
  - Output only. When over budget, the seed block is charged first, then 50% of the remainder is reserved for EDGE lines.
  - The truncation notice now counts cut edges too.
  - The author says the 50/50 split is "a deliberate compromise rather than a tuned value".
- **Human comments:** Author only. No maintainer comment.
- **Bot:** graphify-labs[bot] said "Looks safe to merge", PASS.

## #4592 fix(query): discard heuristic context filters that isolate seeds
- **State:** open. **Author:** mvanhorn. Closes #2529.
- **Change:**
  - Traversal. An inferred `--context` filter is dropped when it matches no edges or isolates every seed, and the header records the drop.
  - An explicit `--context` is never dropped.
  - Filters also match relation names.
- **Human comments:**
  - mvanhorn (Oct 29, Nov 1, Nov 3) merged v8 three times to resolve CHANGELOG conflicts.
  - safishamsi was requested and is awaiting review. No maintainer comment.
- **Bot:**
  - graphify-labs[bot] gave PASS with one medium finding: the relation fallback applies even when the edge has a different explicit context.
  - github-actions[bot] posted a welcome message.

## #1658 fix: correct query/explain/path resolution failures on natural-language input
- **State:** open. **Author:** nokternol.
- **Change:**
  - Adds a per-term seed guarantee.
  - Applies the joined-query bonus only to multi-token queries.
  - Ranks query output by relevance, not degree.
  - `explain` and `path` list ambiguous candidates, with `--force` to pick anyway.
  - Adds a term-overlap fallback and a watch-rebuild semantic cache reattach.
- **Human comments:** None. "No reviews". No maintainer comment. The per-term seed part landed separately via #1596.
- **Bot:** none visible.

## #4504 fix(search): find a symbol by its docstring (#985)
- **State:** open, draft. **Author:** SrijanSriv.
- **Change:**
  - Extraction stores the full docstring or WHY comment `text`, up to 600 characters.
  - At search time, `_attach_docstrings` copies rationale text onto the documented symbol in memory, so the rationale tier matches it.
- **Human comments:** Author only. safishamsi is "awaiting requested review". No maintainer comment.
- **Bot:**
  - graphify-labs[bot] reported no issues from static checks and noted tests were not run.
  - github-actions[bot] posted a welcome message.

## #3856 feat(serve): add JEV two-stage semantic search, smart BFS pruning, and blast radius analysis
- **State:** open. **Author:** 54Lynnn.
- **Change:**
  - Adds optional LLM-API semantic seeding: community coarse filter, then node selection, then degree hub ranking, with an LRU cache and BFS pruning.
  - Adds an `analyze_blast_radius` MCP tool.
  - Falls back to `_pick_seeds` when the API is unavailable.
- **Human comments:** None. No maintainer comment.
- **Bot:** graphify-labs[bot] gave two "Worth a look" reviews. The first found a hardcoded live API key in `.env.example`, untrusted `.env` redirection, and cross-graph cache IDs. The second found docstrings sent to an external API, prune exceptions aborting BFS, and node-id-0 falsy bugs.

## #3837 feat: add efficient correctness-aware graph retrieval
- **State:** open. **Author:** tkartikey0109-spec.
- **Change:**
  - Adds deterministic query indexing, ontology-aware bounded traversal, evidence packets, and retrieval-token accounting.
  - Adds PageIndex-style doc-section retrieval and a corpus partition policy.
  - Ranking details are not visible on page.
- **Human comments:** Author only. safishamsi is awaiting review. No maintainer comment.
- **Bot:** graphify-labs[bot] left review comments; the text is not visible on page.

## #1782 feat: relevance ranking, evals, chronicle, embeddings, skill drift-check
- **State:** open. **Author:** BarrettHolien.
- **Change:**
  - Replaces degree-only render order with Reciprocal Rank Fusion of lexical, structural (proximity, hub, community) and optional semantic signals.
  - Adds `--top-k`, `--explain` and `--semantic`. Semantic similarity also seeds traversal when the lexical match is empty.
- **Human comments:**
  - The author (Jul 10, 2026) wrote "this supersedes #1760 (same change set, rebased onto current v8 and re-tested)".
  - No reviews. No maintainer comment.
- **Bot:** none visible.

## #166 Add hybrid semantic graph retrieval
- **State:** open. It targets the old `v3` branch. **Author:** chethanuk.
- **Change:**
  - Hybrid keyword plus semantic seed selection.
  - Persisted embeddings and MCP semantic query endpoints.
- **Human comments:** None. "No reviews". No maintainer comment.
- **Bot:** none visible.

## #4470 feat(query): --compact writes the same answer in ~1.7x fewer tokens (#4469)
- **State:** open. **Author:** devkancheti4-design.
- **Change:**
  - Output only. Adds an opt-in `--compact` mode and MCP `compact: true`.
  - Surviving NODE lines are grouped under FILE lines with the community hoisted. Same cut and order.
  - The logic was moved out of `_subgraph_to_text` into a separate pass.
- **Human comments:**
  - nothariharan (contributor, Oct 17) wrote "Reviewed and tests pass (10/10)". They agreed that a `"false"` string being truthy is a real issue and suggested `arguments.get("compact") is True`. They called the community-inheritance finding a likely false positive. "No other blocking issues."
  - safishamsi was requested. No maintainer comment.
- **Bot:**
  - graphify-labs[bot] gave PASS with one medium finding: community-less nodes inherit the file's community.
  - github-actions[bot] posted a welcome message.

## #879 fix(serve): prefer exact label match in MCP shortest_path / query_graph
- **State:** open. **Author:** josephmcknight-bot.
- **Change:**
  - `_find_node` returns exact label matches before substring matches.
  - Adds a +10 exact-match bonus in `_score_nodes`.
  - `shortest_path` prints "Resolving 'X' -> node 'Y'".
- **Human comments:**
  - **safishamsi (Member, May 15, 2026) review:** "Unfortunately this PR was built against a stale baseline and would regress several improvements." It would replace main's 3-tier priority scoring with a weaker scheme, drop diacritic-insensitive normalization, and drop ambiguity warnings. He asked for a rebase onto v8 or main that keeps only the new behavior.
  - **safishamsi (May 27, 2026):** "the exact-match bonus and test structure are excellent" but the PR conflicts with v8's `_find_node` and `_score_nodes`. He asked to "Preserve the prefix tier and diacritic normalization", "Layer your exact-match bonus (+10) on top of the IDF score", keep the refactor and 6 tests, and preserve `_search_tokens` from #994. "The core fix is definitely wanted, just needs reconciliation."
  - No author follow-up is visible. wiz0floyd cross-referenced #1165, which is closed.
- **Bot:** none.

## #347 feat: hierarchical Leiden community detection + community summaries + relevance-pruned query
- **State:** open. It targets the old `v4` branch. **Author:** zoedecker.
- **Change:**
  - `_community_relevance_score` scores community summaries against query terms.
  - `query_graph` keeps the top-K relevant communities before BFS/DFS.
  - Adds a `list_communities` MCP tool.
- **Human comments:** None. "No reviews". No maintainer comment.
- **Bot:** none.

## #424 feat: semantic query via sentence-transformers embeddings
- **State:** open. It targets `v4`. **Author:** juhii31.
- **Change:**
  - `query --embeddings` ranks by cosine similarity "instead of BFS keyword match".
  - `embed_graph` adds INFERRED `semantically_similar_to` edges at similarity of 0.82 or more.
- **Human comments:**
  - Author follow-ups on Apr 17, 18 and 21. They renamed the `source` edge attribute to `provenance` after the bot finding.
  - "No reviews". No maintainer comment.
- **Bot:** Qodo-Free-For-OSS flagged that the `source` edge attribute collides with node-link JSON. The author fixed it.

## #1918 perf(serve): collapse T+1 per-term scoring passes into one traversal
- **State:** closed (landed via cherry-pick). **Author:** Sirhan1.
- **Change:** `_score_query()` computes the combined ranking and the per-term best node in one pass, and `_pick_seeds` uses it. Behavior-preserving.
- **Human comments:**
  - **safishamsi (Jul 15, 2026):** "landed on v8" as `ff999a9` with a small rebase fixup, shipping in 0.9.17. He verified it was behavior-preserving with a differential fuzz against the old per-term scoring. He measured about 1.3 to 1.4x faster, independent of query length.
  - The PR states it supersedes the per-term rescoring loop from #1596. A fork log says it also folds in coverage scaling from #1724 and the multiplicity penalty from #1832.
- **Closed by:** safishamsi, Jul 15, 2026.
- **Bot:** none.

## #1856 feat(query): add relevance-aware scoped retrieval
- **State:** closed, unmerged. **Author:** javargasm.
- **Change:**
  - Adds scope directives (`include:memory`, `community:`, `god:`).
  - Demotes saved Q&A memory to a fallback and adds a cross-community quota.
  - Adds a budget-derived node bound in BFS/DFS.
  - Adds a shared ambiguous-resolver that exits 2 with candidates, plus source display variants.
- **Human comments:** None. "No reviews".
- **Closed by:** the author, javargasm, on Sep 26, 2026. **No reason given.**
- **Bot:** none.

## #2516 fix(query): skip covered-term seed guarantee; relax starving heuristic context filters (#2507)
- **State:** closed, unmerged. **Author:** filipechagas (lawnstarter fork).
- **Change:**
  - Adds a default-off `skip_covered_terms` in `_pick_seeds`.
  - Re-traverses without inferred context filters when they add nothing beyond the seeds. The author measured 2,286 → 138 nodes.
- **Human comments:**
  - The author (Aug 6–7) adopted the bot's finding in 234c5f0 and defended the coupling flags as an intended fixture pattern. "No urgency from our side — we run these on our fork."
  - No maintainer comment.
- **Closed by:** the author, Aug 11, 2026: "We close this PR in favor of one consolidated PR". The replacement is **#2617**, with issue #2615.
- **Bot:** graphify-labs[bot] gave two "Worth a look" reviews: the covered-term skip can starve a distinct term, and the substring test matches short terms.

## #1596 fix: guarantee per-term BFS seed diversity in query (fixes #1445)
- **State:** closed (landed via cherry-pick). **Author:** nokternol.
- **Change:**
  - `_pick_seeds` guarantees at least one seed per query term that has a match, with ties broken by degree.
  - Traversal and the hub threshold are unchanged.
- **Human comments:**
  - mark-butterworth-lookinglocal (Jul 2): "Sorry, I'll get Claude to redo this PR tonight... I'm not sure how the patch got so messed up."
  - **safishamsi (Jul 3, 2026):** "Merged into `v8` as `d56ee83` (your authorship)." He praised the backward-compatible optional args and the degree tie-break. He said it "partially addresses" #1602's seed hijack, with the scoring and term-coverage half still open. "Ships next release."
  - Later, #1918 replaced its rescoring loop and kept the coverage guarantee.
- **Closed by:** safishamsi, Jul 3, 2026.
- **Bot:** none.

## #1724 fix: scale per-term exact/prefix score tiers by squared term coverage (#1602)
- **State:** closed (landed via cherry-pick). **Author:** fkhawajagh.
- **Change:** `_score_nodes` scales per-term exact and prefix tiers by `(matched/total)^2`, counting label hits only and deduplicating terms.
- **Human comments:**
  - **safishamsi (Jul 8, 2026):** "Merged the scoring fix on v8 in 2f9deae, authored to you."
  - He **dropped the bundled README badge commits** as "unrelated to #1602" because they touch "the project's own branding layout".
- **Closed by:** safishamsi, Jul 8, 2026.
- **Bot:** none.

## #1832 fix(query): prevent generic symbol query flooding via multiplicity penalty and seed deduplication
- **State:** closed (partially landed). **Author:** devcool20.
- **Change:**
  - Adds seed dedup by label in `_pick_seeds`.
  - Divides the score by the number of nodes sharing a label.
- **Human comments:**
  - **safishamsi (Member, Jul 13, 2026):** "the seed-deduplication idea is the right fix". It landed in `6ca8604`, shipping in 0.9.14, with a case-normalized dedup key and added regression tests.
  - He **rejected the multiplicity penalty** because "dividing scores there silently reweights path/explain endpoint selection" and "The dedup alone bounds the flood."
  - A Sirhan1 fork commit later claims to fold in the multiplicity penalty, which conflicts with this. Upstream status is not visible.
- **Closed by:** safishamsi, Jul 13, 2026.
- **Bot:** none.

## #1597 fix(serve): drop question/filler stopwords from query terms
- **State:** closed (landed via cherry-pick). **Author:** Edge4711.
- **Change:**
  - `_query_terms` drops English question and filler words, falling back to unfiltered terms if everything is a stopword.
  - Node text is not filtered.
- **Human comments:** **safishamsi (Member, Jul 2, 2026):** "Merged into `v8` as `6e97088` (your authorship)." He noted it also mitigates #1602, the filter stays on the query side only, the all-stopword fallback is kept, and the full suite is green. It released in 0.9.5.
- **Closed by:** safishamsi, Jul 2, 2026.
- **Bot:** none.

## #2473 fix(serve): treat `_` as a token separator so underscore queries match hyphenated labels
- **State:** closed (landed via cherry-pick). **Author:** nadiadatepe-eng.
- **Change:** `_search_tokens` uses `[^\W_]+`, so `_` splits tokens. This broadens seeding.
- **Human comments:**
  - **safishamsi (Aug 17, 2026):** "Landed in v0.9.46", cherry-picked onto v8 with authorship preserved.
  - His commit 4be1999 **added an over-match guard test**, checking that an unrelated single-token node does not outrank the full multi-token match.
- **Closed by:** safishamsi, Aug 17, 2026.
- **Bot:** graphify-labs[bot] said "Looks safe to merge", with a `_query_terms` coupling note.

## #3288 fix(query): score the `rationale` attribute as its own tier (#2293)
- **State:** closed (landed via cherry-pick). **Author:** andytsai821201-spec.
- **Change:**
  - A slimmed version of #2294: a rationale tier at 0.75 that feeds the singleton score but not coverage.
  - `_node_search_text` indexes rationale.
- **Human comments:**
  - The author (Sep 2) said #2294 is "too large to merge as-is" and offered to close in its favor if it is rebased.
  - **safishamsi (Sep 5, 2026):** "Shipped in v0.9.54 — landed on v8 via cherry-pick with your authorship preserved."
- **Closed by:** safishamsi, Sep 5, 2026.
- **Bot:** graphify-labs[bot] said "Looks safe to merge", with a `_node_search_text` coupling note.

## #3373 fix(serve): MCP query_graph traverses undirected, so a seed with no outgoing edges reaches its callers
- **State:** closed (landed via cherry-pick). **Author:** kuchtgpt-svg, a self-described agent.
- **Change:** Traversal. `_traversal_view` gives MCP BFS/DFS and the context filter an undirected view, matching the CLI.
- **Human comments:**
  - The author defended folding reciprocal edges together.
  - **safishamsi (Sep 7, 2026):** "landed on `v8` via cherry-pick" with authorship preserved, in release v0.9.56. He did not address the reciprocal-edge advisory.
- **Closed by:** safishamsi, Sep 7, 2026.
- **Bot:** graphify-labs[bot] gave PASS with one medium finding: reciprocal directed edges are collapsed.

## #2338 fix(query): render every edge between visited nodes, not just traversal edges
- **State:** closed (landed). **Author:** Rishet11. Closes #2323.
- **Change:** Output and traversal. `_complete_induced_edges` appends all induced edges between visited nodes after BFS/DFS, respecting context filters.
- **Human comments:** **safishamsi (Member, Aug 1, 2026):** "Shipped in v0.9.32: `graphify query` now renders every edge between visited nodes." He thanked the author.
- **Closed by:** safishamsi, Aug 1, 2026.
- **Bot:**
  - Copilot could not review because of a quota limit.
  - graphify-labs[bot] said "Looks safe to merge".

## #2662 fix(serve): suppress query truncation banner when no nodes were cut (#2601)
- **State:** closed (landed). **Author:** ousamabenyounes.
- **Change:** Output. No truncation banner when `cut_count == 0`, that is, when only trailing edges were dropped.
- **Human comments:** **safishamsi (Aug 12, 2026):** "Shipped in v0.9.41", credited in the release notes.
- **Closed by:** safishamsi, Aug 12, 2026.
- **Bot:** graphify-labs[bot] gave PASS with one medium finding: with `cut_count==0`, it returns full output including edges past the character budget.

## #308 fix: sort query output by relevance score, not just degree
- **State:** closed, unmerged. It targeted `v4`. **Author:** pieralukasz.
- **Change:**
  - Output. `_subgraph_to_text` takes `node_scores` and sorts by `(score, degree)`, with direct matches first. The CLI and MCP pass `_score_nodes` scores.
  - `get_node` uses `_find_node`.
- **Human comments:** None. "No reviews".
- **Closed by:** the author, pieralukasz, on Sep 25, 2026. **No reason given.**
- **Bot:** none.

## #4478 feat(query): --learned starts from nodes that past useful answers to a similar question cited (#4477)
- **State:** open. **Author:** devkancheti4-design.
- **Change:**
  - Adds `--learned` and MCP `learned: true`.
  - Up to 3 seeds come from reflect-sidecar lessons whose past useful answers covered at least 40% of the question's terms, ahead of keyword seeds.
  - The MCP server reloads the sidecar on change.
- **Human comments:**
  - The author (Oct 15) disputed the bot's finding and fixed a stale-cache bug in e16b32d.
  - nothariharan (contributor, Oct 17) wrote "reviewed and tests pass (10/10)". They suggested `arguments.get("learned") is True` and called the bot finding a likely false positive. They noted overlap with #4481 and suggested the seed order "learned -> lead -> keyword seeds".
  - safishamsi was requested. No maintainer comment.
- **Bot:**
  - graphify-labs[bot] said "Worth a look": the MCP `learned` flag might be a silent no-op.
  - github-actions[bot] posted a welcome message.

## #1783 feat(query): accept external seed files for traversal
- **State:** open. **Author:** shura-v.
- **Change:**
  - Adds `--seed-file`, a JSON array of node IDs that replaces question-text seed scoring.
  - Validates the IDs and keeps their order.
  - Logs to querylog.
- **Human comments:**
  - None. "No reviews".
  - 3 thumbs-up reactions (DmitriyWebDev, cakkypamucm, RusovVladimir).
  - No maintainer comment.
- **Bot:** none.

## #4342 feat(benchmark): `--questions` reports whether query_graph shows the right file
- **State:** open. **Author:** rohit-jsfreaky.
- **Change:**
  - No ranking change. Adds an answer-quality benchmark mode that checks where the expected files appear among the NODE lines of `query_graph` output under the MCP defaults (BFS, depth 3, about 2k token budget).
  - Records answer size and whether the over-budget notice appears.
- **Human comments:**
  - The author (Oct 11) refactored to address the bot's coupling flag and asked for re-review.
  - safishamsi was requested and is awaiting review. No maintainer comment.
- **Bot:**
  - graphify-labs[bot] reported no blocking issues and a `run_answer_benchmark` coupling note.
  - github-actions[bot] posted a welcome message.
