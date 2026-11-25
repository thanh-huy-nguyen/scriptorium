Your paper is in `paper/` and the research repository is your working directory; `brief.md` gives the brief.

Review the paper as a careful co-author would, then fix what you find. Check in this order:
1. Every number: recompute it from the raw result files with code and correct any that differ, including numbers in
   tables, captions and figures.
2. Every claim: is it supported by the results, at the scope stated? Is every "significant" backed by a test?
3. Every citation: does the cited paper exist with these details, and does it say what the sentence says?
4. Writing, structure, figures, and the page limit ({page_limit} pages of main text).

Edit the paper, recompile with `{latex} -X compile main.tex` inside `paper/`, and reply with one line: DONE.
