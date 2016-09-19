
recon_time = 60;
js = urlread(['http://127.0.0.1:8000/reconstruct/coastlines/?time=', ...
    num2str(recon_time)]);
cs = loadjson(js);
js = urlread(['http://127.0.0.1:8000/reconstruct/static_polygons/?time=', ...
    num2str(recon_time)]);
sp = loadjson(js);
js = urlread(['http://127.0.0.1:8000/topology/plate_polygons/?time=', ...
    num2str(recon_time)]);
pp = loadjson(js);

figure
hold on
box on

for j=1:length(pp.features)
    xy = pp.features{j}.geometry.coordinates;
    fill(xy(:,1),xy(:,2),[0.6,0.6,0.9])
end
for j=1:length(sp.features)
    xy = sp.features{j}.geometry.coordinates;
    fill(xy(:,1),xy(:,2),[0.2,0.2,0.2],'facealpha',0.5)
end
for j=1:length(cs.features)
    xy = cs.features{j}.geometry.coordinates;
    fill(xy(:,1),xy(:,2),[0.5,0.8,0.5])
end
for j=1:length(pp.features)
    xy = pp.features{j}.geometry.coordinates;
    plot(xy(:,1),xy(:,2),'r','linewidth',1.5)
end

axis equal tight xy
