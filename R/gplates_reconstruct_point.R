gplates_reconstruct_point <- function(lon,lat,age){
  
  library(jsonlite)

  url <- 'http://portal.gplates.org/service/reconstruct_points/'
  query <- sprintf('?points=%d,%d&time=%d&model=default',lon,lat,age)

  fullrequest <- sprintf(paste0(url,query))
  
  rawdata <- readLines(fullrequest, warn="F") 
  dat <- fromJSON(rawdata)
  
  rcoords = dat['coordinates'][[1]]
  return(rcoords)
  
}