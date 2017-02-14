# Get the plate boundaries from the server
pb <- gplates_plate_boundaries(50)

# Print the unique plate boundary types in the returned array
print(unique(pb$feature_type))

sz_length <- as.numeric(pb$Length[pb$feature_type=='gpml:SubductionZone'])
mor_length <- as.numeric(pb$Length[pb$feature_type=='gpml:MidOceanRidge'])

Earth_Radius = 6371.
print(sum(sz_length)*Earth_Radius)
print(sum(mor_length)*Earth_Radius)

