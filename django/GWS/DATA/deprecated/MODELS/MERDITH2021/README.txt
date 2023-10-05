This file describes the plate model accompanying Merdith et al. (2021), 'A continuous, kinematic full-plate motion model from 1 Ga to present'.  It is a compilation of four plate models:  Domeier (2016; 2018); Merdith et al. (2017); Young et al. (2019) and presented purely in a palaeomagnetic reference frame derived from Tetley (2018).

This directory contains Merdith_etal_1_Ga_reconstruction.gproj, which is a GPlates project file that will load the following:

1000_0_rotfile_Merdith_et_al.rot - the Global Rotation Model but with a purely paleomagnetic reference frame
1000_410-*{Convergence/Divergence/Transform/Topologies}-Merdith_et_al.gpml - the plate topologies for 1000 to 410 Ma
410-250_plate_boundaries_Merdith_et_al.gpml - the plate topologies for 410 to 250 Ma
250-0_plate_boundaries_Merdith_et_al.gpml - the plate topologies for 250 to 0 Ma
TopologyBuildingBlocks_Merdith_et_al.gpml - building blocks for some topologies between 410 and 0 Ma
shapes_coastlines_Merdith_et_al.gpml - a Global Coastline file (mainly for the past 400 Ma)
shapes_continents_Merdith_et_al.gpml - a Global Continent shapes file (for the past 1 Ga)
shapes_cratons_Merdith_et_al.gpml - a Global cratonic shapes file (for the past 1 Ga)
shapes_static_polygons_Merdith_et_al.gpml - a Global static polygon file (for the past 1 Ga)
1000-410_poles.gpml - collection of palaeomagnetic data used to constrain the model between 1000 and 410 Ma (corresponds to Table 1 in the associated publication)

For the Mesozoic and Cenozoic, the plates comprising the Pacific Ocean traditionally move in a separate reference to the other ocean basins and continental motions, instead defined by hotspot motion. In order to preserve the plate motion of the Pacific relative to the continental domains where the new GAPWAP was implemented, we extracted relative plate rotations between the Pacific (plateID: 901) and Africa (plateID: 701) in 5 Ma intervals  between 250 and 83 Ma from the Young et al. (2019) model, which has been corrected for errata as discussed in Torsvik et al. (2019). This results in the same relative motion of all Pacific plates to continental plates, however it slightly alters the absolute position of the Pacific plates between 250 and 83 Ma. Studies interested in short(er) timescale (< 5 Ma) analysis or absolute plate motions should use a different model that explicitly links plate motion with the mantle (e.g. (Müller et al. 2019; Tetley et al. 2019)). To be clear, if you want to analyse the Pacific Ocean, including hotspot motion, Hawaiian-Emperor Bend kinematics etc. you should not use this model.

To load these datasets in GPlates do the following:

1.  Open GPlates
2.  Pull down the GPlates File menu and select Open Project
3.  Click to select the GPROJ file
4.  Click Open

Alternatively, drag and drop the GRPOJ file onto the globe.

You now have a global present day continents loaded in GPlates as well as the underlying rotation model and evolving plate topologies.  Play around with the GPlates buttons to make an animation, select features, draw features, etc. For more information, read the GPlates manual which can be downloaded from www.gplates.org.

References
Domeier, M., 2016. A plate tectonic scenario for the Iapetus and Rheic oceans. Gondwana Research, 36, pp.275-295.
Domeier, M., 2018. Early Paleozoic tectonics of Asia: towards a full-plate model. Geoscience Frontiers, 9(3), pp.789-862.
Matthews, K.J., Maloney, K.T., Zahirovic, S., Williams, S.E., Seton, M. and Mueller, R.D., 2016. Global plate boundary evolution and kinematics since the late Paleozoic. Global and Planetary Change, 146, pp.226-250.
Merdith, A.S., Collins, A.S., Williams, S.E., Pisarevsky, S., Foden, J.D., Archibald, D.B., Blades, M.L., Alessio, B.L., Armistead, S., Plavsa, D. and Clark, C., 2017. A full-plate global reconstruction of the Neoproterozoic. Gondwana Research, 50, pp.84-134.
Tetley, M.G., 2018. Constraining Earth’s plate tectonic evolution through data mining and knowledge discovery. PhD Thesis
Torsvik, T.H., Steinberger, B., Shephard, G.E., Doubrovine, P.V., Gaina, C., Domeier, M., Conrad, C.P. and Sager, W.W., 2019. Pacific‐Panthalassic reconstructions: Overview, errata and the way forward. Geochemistry, Geophysics, Geosystems, 20(7), pp.3659-3689.
Young, A., Flament, N., Maloney, K., Williams, S., Matthews, K., Zahirovic, S. and Müller, R.D., 2019. Global kinematics of tectonic plates and subduction zones since the late Paleozoic Era. Geoscience Frontiers, 10(3), pp.989-1013.

Any questions, please email:

  Andrew Merdith <A.S.Merdith@leeds.ac.uk>
