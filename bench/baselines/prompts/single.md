You are writing a complete research paper from the research repository in your working directory.

Read `brief.md` first: it gives the idea, the claims the authors hope to make, where the results live and what to
cite. The paper is for {venue_text}, at most {page_limit} pages of main text (references excluded), in the official
template already set up in `paper/` (`paper/main.tex`; the bibliography goes in `paper/refs.bib`).

Rules (the same rules the other systems in this study are told):
- Every number in the paper must come from the result files in this repository. Compute each one with code from the
  raw results; never type a number you have not computed.
- Make only claims the results support, at the scope they support (datasets, settings). Mark a comparison as
  significant only if a statistical test you ran supports it.
- Cite only real papers. Find them with web search, and take each reference's title, authors, year and venue from
  its record (DBLP, arXiv, Crossref or the publisher). Each citing sentence must say what the cited paper says.
- Figures are made with code from the results (matplotlib is available), saved into `paper/figures/`.
- Write a full paper: title, abstract, introduction with contributions, related work, method, experimental setup,
  results, discussion with limitations, and references.
- Use only files inside this working directory. Do not edit `results/` or `experiments/`.
- Compile with `{latex} -X compile main.tex` inside `paper/` until it builds without errors and fits the page limit.

When you are done, `paper/main.pdf` must exist. Reply with one line: DONE.
