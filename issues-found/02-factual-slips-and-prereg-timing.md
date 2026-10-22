# Factual slip and unverifiable pre-registration timing (original run)
- writeup.md says English at ~0.21 tokens/byte is "close to the ~0.25 ceiling of byte-level BPE". The real bound is 1 token/byte, so the sentence is wrong. The README's "bytes (upper bound)" row is fine.
- The original README mtime (13:09) is after results/summary.json (13:08). With no git history, the rule's timing can't be verified.
- The "Telugu prose is priced above even code" comparison uses non-parallel content.
- **Status:** open (wording). The follow-up README section is timestamped before any re-test counts, and results/flores-rerun/ was created after it.
