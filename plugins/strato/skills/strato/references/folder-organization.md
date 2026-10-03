# Folder organization

Folder structure supports navigation; native relationships carry traceability. No universal industry standard prescribes Strato folder names. Tailor the hierarchy to the product, its boundaries, and the user's review needs.

When present, read `.strato/product-state.json` for the selected product's `products.<slug>.organization`. This optional state records only the user's chosen organizing principles for `specifications`, `designs`, and `test_cases`. Use them to guide placement after inspecting current Strato content; they neither describe the current tree nor authorize a reorganization. Missing state is normal and does not block work. Record or revise a principle when the user selects it, preserving other products' entries; do not rewrite state after every sync or silently substitute a new principle. New user direction takes precedence over saved preferences.

Keep this file limited to these product-scoped preferences. Do not add folder names or IDs, record mappings, inventories, cached content, completion flags, pending actions, or sync checkpoints. Strato remains authoritative for its records and folders; confirmed sync events remain in `sync-history.json`.

Before writing, inspect the existing tree and representative records. Choose and state a primary organizing principle for each record category, based on the product and how its users review the records. Apply it consistently within each branch; do not impose a predefined combination of disciplines, functions, assemblies, or test levels. These trees need not mirror one another. Show the proposed target tree and representative placements during planning; proceed with already-authorized organization once its basis is clear. Preserve record identity and relationships when moving records.

Use a few broad parents and meaningful subfolders where they improve navigation. Keep siblings comparable in scope and abstraction. Avoid mixing functional domains, physical components, and shared constraints as undifferentiated siblings. Explain deliberately separate branches for concerns that span several subsystems. Each record has one primary home; use native links instead of duplicate records to represent other allocations.

Assess proposed folders against actual record content: would reviewers know where a new record belongs, are neighboring folders comparable, and are overlapping responsibilities handled through native links rather than duplicate records? Refine the principle or hierarchy when placement is ambiguous. Do not derive a reusable taxonomy from one product's component names.

Create folders for substantive records or an explicitly selected roadmap. If planned empty branches are useful, identify them as planned and name the evidence or decision needed to populate them. Folder presence is not specification, design, or verification coverage. Reconcile an existing skeleton before expanding it; a cleaner tree does not by itself make its contents complete.
