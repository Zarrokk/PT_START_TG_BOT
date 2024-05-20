ALTER USER repl_user WITH PASSWORD '123';
CREATE TABLE emails(id SERIAL primary key,email VARCHAR(255));
CREATE TABLE phonenum(id SERIAL primary key,phone VARCHAR(255));
INSERT INTO emails(email)VALUES('test@test.com');
INSERT INTO phonenum(phone)VALUES('89001111111');
