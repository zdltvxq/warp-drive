# Writing rules for this repository

These rules apply to the README, research notes, comments, docstrings, and changelog entries. Keep the existing language and tone of the file you edit.

## Write plainly

- Start with the method, result, or action the reader needs. Cut chatbot greetings, rhetorical questions, and summaries that repeat what the reader just read.
- Do not use slogans, sales language, forced metaphors, or stock contrasts such as "not just X, but Y." Replace broad claims with the specific result or leave them out.
- Use the same term for the same thing. Do not swap in synonyms for technical terms or add anecdotes, opinions, or deliberate mistakes to make prose sound human.
- Use headings, lists, and emphasis when they help the reader find information. Avoid decorative emoji, strings of em dashes, and bold labels on every bullet.

## State what the evidence supports

- Distinguish assumptions, published findings, results reproduced here, and work still planned. Name the paper or point to the script, test, or output behind a claim. Never invent citations, numbers, or test results.
- Keep conclusions within the model and the checks performed. For example, `optimize.qi_audit` estimates energy at specified wall thicknesses; it does not solve the quantum inequality.
- Preserve equations, units, sign conventions, commands, citations, attribution, and AI disclosures. If an edit changes a technical claim, check it against the relevant source or code and report the correction separately from the style edits.

Before submitting, read the changed text once for filler and once for accuracy. Run `git diff --check` and check any links or commands you changed.
