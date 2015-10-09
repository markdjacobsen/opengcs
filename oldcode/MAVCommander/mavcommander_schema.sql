create table mav_type (
    uuid          text primary key,
    name          text,
    description   text,
    checklistfile text,
    paramfile     text
);

-- Tasks are steps that can be taken to complete a project
create table mav (
    uuid         text primary key,
    name         text,
    mav_type     text,
    sys_id       integer,
    notes        text
);

create table log (
    uuid         text primary key,
    mav_id       text,
    weight       text,
    cg           text,
    notes        text,
    file         text
);


