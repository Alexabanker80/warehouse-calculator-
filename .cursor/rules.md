# Cursor Rules (Bashmak)

These rules define how work is organized so you do not need to repeat
instructions each time.

## Core behavior

- Always respond in Russian unless asked otherwise.
- Ask questions one at a time.
- Do not move to solutions until the user confirms understanding.
- Summarize what was understood before asking the next question.

## Storage rules

- Store all company information in `/company/`.
- Use the correct domain folder (e.g. marketing in `06-marketing`).
- For any non-Markdown file (xlsx, pdf, docx), create a same-name `.md`
  summary next to it.
- Use ASCII file names (kebab-case) unless the file already exists in
  a different format.

## Documentation rules

- Use templates from `/company/_templates/`.
- Add short headers to new docs (Title, Owner, Date, Status, Related).
- Keep one source of truth and link to it instead of duplicating.

## Sync rules

- After substantive changes, commit and push.
- Do not revert unrelated changes.
- Keep local and cloud in sync (use the auto-sync rule in
  `/company/01-foundation/auto-sync.md`).
