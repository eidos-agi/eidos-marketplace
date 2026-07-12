---
description: Author complex test cases before building — cases that can actually catch something
---

Run the `complextestcases` skill for this repo.

Author cases BEFORE the work, `ctc redcheck` them (every case must be RED), then
build. A case that has never been seen red certifies nothing — it scores zero.

If the user has already written the code, say so plainly: the case cannot be
red-checked, so it is VACUOUS and proves nothing. Offer to stash the code, watch
the case go red, and restore.
