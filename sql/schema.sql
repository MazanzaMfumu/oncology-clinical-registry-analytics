-- Enables relationship enforcement between tables.
PRAGMA foreign_keys = ON;

-- Drops old tables during a rebuild.
-- Dependent tables are dropped before the patients table.
DROP TABLE IF EXISTS data_quality_issues;
DROP TABLE IF EXISTS outcomes;
DROP TABLE IF EXISTS tumors;
DROP TABLE IF EXISTS patients;

-- Table containing general case information.
CREATE TABLE patients (
    case_id TEXT PRIMARY KEY,
    age REAL,
    race TEXT,
    marital_status TEXT,
    quality_status TEXT NOT NULL
);

-- Table containing tumor information.
CREATE TABLE tumors (
    case_id TEXT PRIMARY KEY,
    t_stage TEXT,
    n_stage TEXT,
    overall_stage TEXT,
    grade TEXT,
    a_stage TEXT,
    tumor_size REAL,
    estrogen_status TEXT,
    progesterone_status TEXT,
    regional_nodes_examined REAL,
    regional_nodes_positive REAL,
    lymph_node_ratio REAL,

    FOREIGN KEY (case_id)
        REFERENCES patients(case_id)
);

-- Table containing survival and vital status information.
CREATE TABLE outcomes (
    case_id TEXT PRIMARY KEY,

    survival_months REAL CHECK (
        survival_months >= 0
        OR survival_months IS NULL
    ),

    vital_status TEXT CHECK (
        vital_status IN ('Alive', 'Dead')
        OR vital_status IS NULL
    ),

    event INTEGER CHECK (
        event IN (0, 1)
        OR event IS NULL
    ),

    CHECK (
        vital_status IS NULL
        OR event IS NULL
        OR (vital_status = 'Alive' AND event = 0)
        OR (vital_status = 'Dead' AND event = 1)
    ),

    FOREIGN KEY (case_id)
        REFERENCES patients(case_id)
);

-- Table containing one row per detected anomaly.
CREATE TABLE data_quality_issues (
    issue_id INTEGER PRIMARY KEY AUTOINCREMENT,
    case_id TEXT,
    rule_id TEXT NOT NULL,
    field TEXT,
    severity TEXT,
    message TEXT,

    FOREIGN KEY (case_id)
        REFERENCES patients(case_id)
);

-- Indexes designed to facilitate certain searches.
CREATE INDEX idx_tumors_overall_stage
    ON tumors(overall_stage);

CREATE INDEX idx_tumors_n_stage
    ON tumors(n_stage);

CREATE INDEX idx_outcomes_vital_status
    ON outcomes(vital_status);

CREATE INDEX idx_quality_issues_rule
    ON data_quality_issues(rule_id, severity);