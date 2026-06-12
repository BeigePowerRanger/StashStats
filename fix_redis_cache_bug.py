# The code review pointed out a valid flaw:
# 1) `results` is an iterator (from `executor.map(fetch_detail, dirty_items)` which returns a generator/iterator usually in Python `concurrent.futures`, although it is wrapped in `list()` on line 299). Wait, it is wrapped in list() in the original code!
# Let's check model.py line 299:
# `results = list(executor.map(fetch_detail, dirty_items))`
# Since it is a list, it won't be exhausted. However, the extreme DRY violation is fully valid. We duplicated the fiber pack parsing just to push it to Redis via pipeline.
# We can just initialize the pipeline BEFORE the loop, call `pipe.setex` INSIDE the loop using `new_packs` which we already calculated, and then call `pipe.execute()` AFTER the loop.
