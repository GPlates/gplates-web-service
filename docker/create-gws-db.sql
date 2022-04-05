create user gplates with encrypted password 'this is not a real password! go away!';
grant all privileges on database gplates to gplates;

CREATE EXTENSION postgis;
CREATE EXTENSION postgis_topology;
CREATE EXTENSION postgis_raster;

