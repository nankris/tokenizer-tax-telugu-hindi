# Original verdict double-counted one tokenizer; headline median described no tokenizer
- **What:** the original run's "PROVEN 4/6" counts Llama-3.2 and cl100k separately, even though their Telugu counts are identical to 2 decimals (226.7). Of 5 distinct tokenizers, only 3 clear 2×. The 4.9× headline is the median of a bimodal set.
- **Evidence:** results/summary.csv (original run); review fact sheet 21 Oct.
- **Fix:** the follow-up re-test (README section "Follow-up re-test on fresh sentences", [RESULTS_flores_rerun.md](../RESULTS_flores_rerun.md)) uses a dedupe rule and 1,809 fresh sentences, and the headline reports the range and clusters. Under the corrected rule H2 still comes out PROVEN (7/10 distinct, 6/9 under the strict merge).
- **Status:** resolved by the follow-up re-test.
