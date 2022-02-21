CREATE TABLE IF NOT EXISTS AppList (
    package_name TEXT PRIMARY KEY,
    installs INTEGER,
    install_date DATE,
    extract_date DATE
);