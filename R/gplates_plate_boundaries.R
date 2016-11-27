gplates_plate_boundaries <- function(age){

  url <- 'http://127.0.0.1:8000/topology/plate_boundaries/'
  query <- sprintf('?time=%d',age)

  fullrequest <- sprintf(paste0(url,query))
  print(fullrequest)
  
  #r <- GET(fullrequest)
  #bin <- content(r, "raw")
  #writeBin(bin, "myfile.geojson")
  rawdata <- readLines(fullrequest, warn="F") 
  dat <- fromJSON(rawdata)
  
  pb <- dat['features'][[1]][,1]
  #dat <- readOGR(dsn="myfile.geojson", layer="OGRGeoJSON", stringsAsFactors=FALSE)
  
  return(pb)
  
}
