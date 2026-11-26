-- Schema for the healthcare payments denials demo (SQLite dialect).
-- One row per remittance (835-style) service line.

CREATE TABLE remittance_lines (
    line_id       TEXT PRIMARY KEY,
    claim_id      TEXT NOT NULL,       -- resubmissions share the claim id
    submission    INTEGER NOT NULL,    -- 1 = first pass, 2+ = resubmission/appeal
    payer         TEXT NOT NULL,
    cpt_code      TEXT NOT NULL,
    billed        REAL NOT NULL CHECK (billed > 0),
    allowed       REAL,
    paid          REAL NOT NULL,       -- 0 when the line was denied
    denial_code   TEXT,                -- CARC code, NULL when paid
    service_date  TEXT NOT NULL,       -- ISO yyyy-mm-dd
    remit_date    TEXT NOT NULL
);
