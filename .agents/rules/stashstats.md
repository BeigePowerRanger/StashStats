# StashStats Project Rules

## API-First Storage Design

Before designing any storage schema, persistence model, or caching layer for Ravelry data, first
verify whether the API already exposes that data natively. Run a live `GET` call and inspect the
actual response structure. Do not duplicate fields the API already tracks — use a reference (ID)
and resolve live when needed.

## No Storage-Layer Deduplication for Pandas Consumers

Do not implement deduplication logic inside storage or persistence code for time-series or
observation data when the consumer is a pandas DataFrame. Leave deduplication to the analysis
layer (`df.drop_duplicates`, groupby, etc.) where it is more flexible and explicit about which
columns to key on.

## Save Deferred Plans to `plans/`

When a design or implementation plan is approved but deferred ("not right now", "save for later",
"don't implement yet"), always copy the plan document to `plans/<descriptive-slug>.md` in the
project root. Do not rely solely on artifact storage — the `plans/` directory is the durable
record in version control.
