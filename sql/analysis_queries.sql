-- 1. Nombre total de dossiers
SELECT
    COUNT(*) AS total_cases
FROM patients;


-- 2. Dossiers selon leur statut de qualité
SELECT
    quality_status,
    COUNT(*) AS number_of_cases
FROM patients
GROUP BY quality_status
ORDER BY number_of_cases DESC;


-- 3. Nombre de cas selon le stade
SELECT
    overall_stage,
    COUNT(*) AS number_of_cases
FROM tumors
GROUP BY overall_stage
ORDER BY number_of_cases DESC;


-- 4. Statut vital selon le stade
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


-- 5. Ratio ganglionnaire moyen selon le stade N
SELECT
    n_stage,
    ROUND(
        AVG(lymph_node_ratio),
        3
    ) AS average_lymph_node_ratio
FROM tumors
WHERE lymph_node_ratio IS NOT NULL
GROUP BY n_stage
ORDER BY n_stage;


-- 6. Nombre d'anomalies selon la règle
SELECT
    rule_id,
    severity,
    COUNT(*) AS number_of_issues
FROM data_quality_issues
GROUP BY
    rule_id,
    severity
ORDER BY number_of_issues DESC;


-- 7. Nombre de dossiers présentant au moins une anomalie
SELECT
    COUNT(DISTINCT case_id)
        AS cases_requiring_review
FROM data_quality_issues;