create user gplates with encrypted password 'gplates';
grant all privileges on database gplates to gplates;

CREATE EXTENSION postgis;
CREATE EXTENSION postgis_topology;
CREATE EXTENSION postgis_raster;

create schema raster;
ALTER SCHEMA raster OWNER TO gplates;


