CREATE TABLE objects (
    id integer primary key,
    name text,
    created date,
    times_played integer,
    last_played date
);

CREATE TABLE questions (
    id integer primary key,
    text text,
    created date
);

CREATE TABLE data (
    object_id integer,
    question_id integer,
    value integer
);

CREATE TABLE playlog (
    object_id integer,
    data text,
    right boolean
);
    

CREATE TRIGGER new_object_created after insert on objects
begin
update objects set created = datetime('now')
where rowid = new.rowid;
end;

CREATE TRIGGER new_question_created after insert on questions
begin
update questions set created = datetime('now')
where rowid = new.rowid;
end;

CREATE TRIGGER object_played after update of times_played on objects
begin
update objects set last_played = datetime('now')
where rowid = old.rowid;
end;

CREATE INDEX data_idx ON data(question_id,object_id);
