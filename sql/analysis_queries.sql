-- 1. Total number of files
SELECT
    COUNT(*) AS total_cases
FROM patients;

-- 2. Distribution of cases by overall stage
SELECT
    overall_stage,
    COUNT(*) AS number_of_cases,
    ROUND(
        100.0 * COUNT(*)
        / (SELECT COUNT(*) FROM tumors),
        2
    ) AS percentage_of_cases
FROM tumors
GROUP BY overall_stage
ORDER BY number_of_cases DESC;

-- 3. Vital status by overall stage
SELECT
    t.overall_stage,
    o.vital_status,
    COUNT(*) AS number_of_cases
FROM tumors AS t
INNER JOIN outcomes AS o
    ON t.case_id = o.case_id
GROUP BY
    t.overall_stage,
    o.vital_status
ORDER BY
    t.overall_stage,
    o.vital_status;

-- 4. Mean lymph node ratio according to N stage
SELECT
    n_stage,
    COUNT(*) AS number_of_cases,
    ROUND(
        AVG(lymph_node_ratio),
        3
    ) AS average_lymph_node_ratio
FROM tumors
WHERE lymph_node_ratio IS NOT NULL
GROUP BY n_stage
ORDER BY n_stage;

-- 5. Number of cases by quality status
SELECT
    quality_status,
    COUNT(*) AS number_of_cases
FROM patients
GROUP BY quality_status
ORDER BY number_of_cases DESC;

-- 6. Number of anomalies by rule and severity
SELECT
    rule_id,
    severity,
    COUNT(*) AS number_of_issues
FROM data_quality_issues
GROUP BY
    rule_id,
    severity
ORDER BY
    number_of_issues DESC,
    rule_id;

-- 7. Number of files containing at least one anomaly
SELECT
    COUNT(DISTINCT case_id)
        AS cases_with_at_least_one_issue
FROM data_quality_issues;

-- 8. Number of cases by vital status
SELECT
    vital_status,
    COUNT(*) AS number_of_cases
FROM outcomes
GROUP BY vital_status
ORDER BY number_of_cases DESC;