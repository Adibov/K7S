CREATE TABLE IF NOT EXISTS health_checks
(
    id            SERIAL PRIMARY KEY,
    failure_count INT         NOT NULL DEFAULT 0,
    success_count INT         NOT NULL DEFAULT 0,
    last_failure  TIMESTAMP   NULL,
    last_success  TIMESTAMP   NULL,
    app_name      VARCHAR(20) NOT NULL,
    created_at    TIMESTAMP   NOT NULL DEFAULT current_timestamp
);

INSERT INTO health_checks (app_name)
VALUES ('myapp');