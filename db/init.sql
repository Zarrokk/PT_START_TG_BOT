CREATE USER repl_user WITH PASSWORD 'Qq12345' REPLICATION;

CREATE TABLE IF NOT EXISTS hba ( lines text );
COPY hba FROM '/var/lib/postgresql/data/pg_hba.conf';
INSERT INTO hba (lines) VALUES ('host replication all 0.0.0.0/0 scram-sha-256');
COPY hba TO '/var/lib/postgresql/data/pg_hba.conf';
SELECT pg_reload_conf();

CREATE TABLE IF NOT EXISTS Emails  (
    emailid SERIAL PRIMARY KEY,
    emailaddress VARCHAR(256)
);

CREATE TABLE IF NOT EXISTS Phones  (
    phoneid SERIAL PRIMARY KEY,
    phonenumber VARCHAR(256)
);
