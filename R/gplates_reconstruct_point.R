gplates_reconstruct_point <- function(lon,lat,age){
  
  library(jsonlite)

  url <- 'http://127.0.0.1:8000/reconstruct/reconstruct_points/'
  query <- sprintf('?points=%d,%d&time=%d&model=default',lon,lat,age)

  fullrequest <- sprintf(paste0(url,query))
  
  print(fullrequest)
  rawdata <- readLines(fullrequest, warn="F") 
  dat <- fromJSON(rawdata)
  
  rcoords = dat['coordinates'][[1]]
  return(rcoords)
  
}