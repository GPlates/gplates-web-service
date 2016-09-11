gplates_reconstruct_coastlines <- function(age){
  
  library(jsonlite)
  library(rgdal)
  #library(geojsonio)

  url <- 'http://127.0.0.1:8000/reconstruct/coastlines/'
  query <- sprintf('?time=%d',age)

  fullrequest <- sprintf(paste0(url,query))
  print(fullrequest)
  
  r <- GET(fullrequest)
  bin <- content(r, "raw")
  writeBin(bin, "myfile.geojson")
  
  dat <- readOGR(dsn="myfile.geojson", layer="OGRGeoJSON", stringsAsFactors=FALSE)
  
  return(dat)
  
}