create user gplates with encrypted password 'gplates';
grant all privileges on database gplates to gplates;

CREATE EXTENSION postgis;
CREATE EXTENSION postgis_topology;
CREATE EXTENSION postgis_raster;

create schema raster;
ALTER SCHEMA raster OWNER TO gplates;

-- schema for the GSFML magnetic anomaly identification picks
-- (the "magnetic.picks" table is created and populated by
--  "python manage.py load_magnetic_picks" -- see django/GWS/earth/management/commands/)
create schema magnetic;
ALTER SCHEMA magnetic OWNER TO gplates;

GRANT ALL ON SCHEMA public TO gplates;


