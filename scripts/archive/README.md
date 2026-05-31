# Archived Generator Scripts — DO NOT USE

These eight scripts were the source of the schema-content bug fixed on May 31, 2026
(see `outputs/GENERATOR_AUDIT.md`).

All of them open a template HTML file (`cudjoe-key-boat-rentals-florida-keys-cudjoe-key.html`)
that no longer exists on disk and do regex/string replacements for ~12 fields.
Any field NOT in that replacement list (TouristAttraction.description, aggregateRating,
FAQPage content, visible FAQ body, "Caribbean coast" in body copy) is silently
inherited from the template — which is how 4,763 operator pages ended up describing
themselves as "the iconic Pink Party Boat of <city>".

**If you need to add new operators, use `gen_missing_slug_pages.py` instead.**
It renders every page from scratch using f-strings + json.dumps, with a real guard
on aggregateRating (only emitted when reviews > 0). That's the correct pattern.

Files archived here:
- `gen_html_batch.py`
- `gen_b552_554.py`
- `gen_b555_563.py`
- `add_b564_569.py`
- `add_b570_576.py`
- `add_b577_581.py`
- `add_b582_585.py`
- `add_b586_588.py`
