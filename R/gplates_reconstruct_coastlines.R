gplates_reconstruct_coastlines <- function(age){
  
  library(jsonlite)
  library(rgdal)
  #library(geojsonio)

  url <- 'http://portal.gplates.org/service/get_coastline_polygons/'
  query <- sprintf('?time=%d',age)

  fullrequest <- sprintf(paste0(url,query))
    
  rawdata <- readLines(fullrequest, warn="F")
  dat <- fromJSON(rawdata)
  #dat <- rawdata
  
  return(dat)
  
}