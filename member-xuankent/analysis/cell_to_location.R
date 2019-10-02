#!/usr/bin/env Rscript
## Script to map cell ids to zones and boroughs
## Usage: ./cell_to_location.R <output.rds> <zones.shp> <data.csv>...


suppressMessages(library(tidyverse))
suppressMessages(library(data.table))
suppressMessages(library(sp))
suppressMessages(library(rgdal))


args <- commandArgs(trailingOnly=TRUE)


read_zones <- function(infile) {
  taxi_zones <- readOGR(dsn = infile, verbose=FALSE)
  
  taxi_zones@data <- taxi_zones@data %>%
    mutate(zone = as.factor(zone))
  
  # reproject to commonly used CRS
  taxi_zones <- spTransform(taxi_zones, CRS("+init=epsg:4326"))
  
  taxi_zones
}


read_cols <- c("Pickup_longitude", "Pickup_latitude", 
               "Dropoff_longitude", "Dropoff_latitude",
               "Pickup_cell", "Dropoff_cell")

keep_cols <- c("Pickup_longitude", "pickup_longitude",
               "Pickup_latitude", "pickup_latitude",
               "Dropoff_longitude", "dropoff_longitude",
               "Dropoff_latitude", "dropoff_latitude",
               "PickupCell", "DropoffCell")

out_cols <- c("Pickup_cell", "Dropoff_cell", 
              "Pickup_zone", "Pickup_borough",
              "Dropoff_zone", "Dropoff_borough")



clean_taxi_data <- function(taxi_data) {
  taxi_data %>%
    # remove rows with missing value(s)
    drop_na() %>%
    # data cleansing
    filter(Pickup_cell != "", Dropoff_cell != "")
}


spatial_overlap_zones <- function(taxi_data, zones) {
  # find intersect between trip locations and taxi zones
  pickup_zones <- SpatialPointsDataFrame(coords=taxi_data[, c('Pickup_longitude', 'Pickup_latitude')],
                                         data=taxi_data,
                                         proj4string=CRS(proj4string(zones))) %>%
    over(zones) %>%
    select(zone, borough)
  
  dropoff_zones <- SpatialPointsDataFrame(coords=taxi_data[, c('Dropoff_longitude', 'Dropoff_latitude')],
                                          data=taxi_data,
                                          proj4string=CRS(proj4string(zones))) %>%
    over(zones) %>%
    select(zone, borough)
  
  taxi_data %>%
    mutate(Pickup_zone = pickup_zones$zone,
           Pickup_borough = pickup_zones$borough,
           Dropoff_zone = dropoff_zones$zone,
           Dropoff_borough = dropoff_zones$borough) %>%
    # some trips may not fall in known taxi zones
    drop_na()
}


read_columns <- function(filename, keep_cols) {
  header <- fread(filename, nrows=1, header=FALSE) %>%
    unlist()
  header[header %in% keep_cols]
}


read_one_taxi_data <- function(filename, taxi_zones, read_columns=read_cols,
                               out_columns=out_cols,
                               keep_columns=keep_cols) {
  message("Reading ", filename)
  cols <- read_columns(filename, keep_columns)
  fread(filename, select=cols, fill=TRUE, 
        showProgress=FALSE, col.names=read_columns) %>%
    as_tibble() %>%
    clean_taxi_data() %>%
    spatial_overlap_zones(taxi_zones) %>%
    mutate_at(vars(Pickup_cell, Dropoff_cell, 
                   Pickup_zone, Pickup_borough,
                   Dropoff_zone, Dropoff_borough), 
              factor) %>%
    select(out_columns)
}


cap_str <- function(x) {
  paste0(toupper(substring(x, 1, 1)), substring(x, 2))
}


main <- function(args) {
  if (length(args) < 3) {
    stop("Incorrect number of arguments supplied", call.=FALSE)
  }
  
  output <- args[1]
  zones_path <- args[2]
  args <- args[-c(1, 2)]
    
  # Read data
  message("Reading data")
  taxi_zones <- read_zones(zones_path)
  
  df <- lapply(args, function(x) read_one_taxi_data(x, taxi_zones)) %>%
    rbindlist()
  
  
  # Concat pickup and dropoff cells
  message("Concatenating data")
  cols <- c("cell", "zone", "borough")
  
  df <- rbindlist(lapply(c("Pickup_", "Dropoff_"),
                        function(x) df %>% 
                          select(paste0(x, cols)) %>% 
                          rename_all(function(x) cap_str(cols)))
  )
  
  # Counting zones and boroughs
  message("Counting")
  zones <- df %>%
    group_by(Cell, Zone) %>%
    tally(name = "Count") %>%
    ungroup() %>%
    arrange(desc(Count)) %>%
    group_by(Cell) %>%
    top_n(1, Count) %>%
    ungroup() %>%
    arrange(Cell) %>%
    select(-Count)
  
  boroughs <- df %>%
    group_by(Cell, Borough) %>%
    tally(name = "Count") %>%
    ungroup() %>%
    arrange(desc(Count)) %>%
    group_by(Cell) %>%
    top_n(1, Count) %>%
    ungroup() %>%
    arrange(Cell) %>%
    select(-Count)
  
  # Join and save data
  message("Joining and saving data")
  if (!grepl(".rds$", output)) {
    output <- paste0(output, ".rds")
  }
  zones %>% 
    inner_join(boroughs, by=c("Cell" = "Cell")) %>%
    saveRDS(file=output)
}

main(args)
