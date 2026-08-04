PRAGMA foreign_keys = ON;

DROP TABLE IF EXISTS data_quality_issues;
DROP TABLE IF EXISTS outcomes;
DROP TABLE IF EXISTS tumors;
DROP TABLE IF EXISTS patients;

CREATE TABLE patients (
    case_id TEXT PRIMARY KEY,
    age REAL,
    race TEXT,
    marital_status TEXT,
    quality_status TEXT NOT NULL
);

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

CREATE TABLE outcomes (
    case_id TEXT PRIMARY KEY,
    survival_months REAL,
    vital_status TEXT,
    event INTEGER CHECK (
        event IN (0, 1)
        OR event IS NULL
    ),

    FOREIGN KEY (case_id)
        REFERENCES patients(case_id)
);

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