gplates_reconstruct_plate_boundaries <- function(age){

  url <- 'http://127.0.0.1:8000/paleocoherence/plate_boundaries/'
  query <- sprintf('?time=%d',age)

  fullrequest <- sprintf(paste0(url,query))
  print(fullrequest)
  
  r <- GET(fullrequest)
  bin <- content(r, "raw")
  writeBin(bin, "myfile.geojson")
  
  dat <- readOGR(dsn="myfile.geojson", layer="OGRGeoJSON", stringsAsFactors=FALSE)
  
  return(dat)
  
}