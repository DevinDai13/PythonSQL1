-- CMPUT 291 - Winter 2018 
-- TABLES for Project #1, assuming SQLite as database engine (uses the TEXT data type) 


-- The following commands drops the tables in case they exist from earlier runs. 
DROP TABLE IF EXISTS users;
DROP TABLE IF EXISTS service_fulfillments;
DROP TABLE IF EXISTS service_agreements;
DROP TABLE IF EXISTS accounts;
DROP TABLE IF EXISTS drivers;
DROP TABLE IF EXISTS account_managers;
DROP TABLE IF EXISTS personnel;
DROP TABLE IF EXISTS container_waste_types;
DROP TABLE IF EXISTS waste_types;
DROP TABLE IF EXISTS containers;
DROP TABLE IF EXISTS maintenance_records;
DROP TABLE IF EXISTS trucks;


-- The following commands create the tables including FOREIGN KEY constraints

CREATE TABLE users (
  user_id	TEXT, 
  role		TEXT,
  login		TEXT, 
  password	TEXT, 
  PRIMARY KEY (user_id),
  FOREIGN KEY (user_id) REFERENCES personnel(pid) ON DELETE CASCADE
);


CREATE TABLE trucks (
  truck_id          TEXT,
  model             TEXT,
  truck_type        TEXT,
  PRIMARY KEY (truck_id) 
);

CREATE TABLE maintenance_records (
  truck_id          TEXT,
  service_date      DATE,
  description       TEXT,
  PRIMARY KEY (truck_id, service_date),
  FOREIGN KEY (truck_id) REFERENCES trucks ON DELETE CASCADE
);

CREATE TABLE containers (
  container_id      TEXT,
  container_type    TEXT,
  date_when_built   DATE,
  PRIMARY KEY (container_id)
);

CREATE TABLE waste_types (
    waste_type      TEXT,
    PRIMARY KEY (waste_type)
);

CREATE TABLE container_waste_types (
  container_id      TEXT,
  waste_type        TEXT,
  PRIMARY KEY (container_id, waste_type),
  FOREIGN KEY (container_id) REFERENCES containers,
  FOREIGN KEY (waste_type) REFERENCES waste_types
);

CREATE TABLE personnel (
  pid               TEXT, 
  name              TEXT, 
  email             TEXT, 
  address           TEXT, 
  supervisor_pid    TEXT, 
  PRIMARY KEY (PID)
);

CREATE TABLE account_managers (
  pid               TEXT,
  manager_title     TEXT,
  office_location   TEXT,
  PRIMARY KEY (pid),
  FOREIGN KEY (pid) REFERENCES personnel
);

CREATE TABLE drivers (
  pid               TEXT,
  certification     TEXT,
  owned_truck_id    TEXT,
  PRIMARY KEY (pid),
  FOREIGN KEY (pid) REFERENCES personnel,
  FOREIGN KEY (owned_truck_id) REFERENCES trucks(truck_id)
);

CREATE TABLE accounts (
  account_no        TEXT,
  account_mgr       TEXT,
  customer_name     TEXT,
  contact_info      TEXT,
  customer_type     TEXT,
  start_date        DATE,
  end_date          DATE,
  total_amount      REAL,
  PRIMARY KEY (account_no),
  FOREIGN KEY (account_mgr) REFERENCES account_managers(pid)
);

CREATE TABLE service_agreements (
  service_no        TEXT,
  master_account    TEXT,
  location          TEXT,
  waste_type        TEXT,
  pick_up_schedule  TEXT,
  local_contact     TEXT,
  internal_cost     REAL,
  price             REAL,
  PRIMARY KEY (master_account, service_no),
  FOREIGN KEY (master_account) REFERENCES accounts ON DELETE CASCADE, 
  FOREIGN KEY (waste_type) REFERENCES waste_types
); 
  
CREATE TABLE service_fulfillments (
  date_time         DATE,
  master_account    TEXT, 
  service_no        TEXT,
  truck_id          TEXT,
  driver_id         TEXT,
  cid_drop_off      TEXT,
  cid_pick_up       TEXT,
  PRIMARY KEY (date_time, master_account, service_no, truck_id, driver_id, cid_drop_off, cid_pick_up)
  FOREIGN KEY (master_account, service_no) REFERENCES service_agreements,
  FOREIGN KEY (truck_id) REFERENCES trucks,
  FOREIGN KEY (driver_id) REFERENCES drivers(pid),
  FOREIGN KEY (cid_drop_off) REFERENCES containers(container_id),
  FOREIGN KEY (cid_pick_up) REFERENCES containers(container_id)
);