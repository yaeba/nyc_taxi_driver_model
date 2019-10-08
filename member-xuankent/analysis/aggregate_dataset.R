#!/usr/bin/env Rscript
## Script to aggregate tripdata data into minute of month (Only in Manhattan)
## Usage: ./aggregate_dataset.R <output.rds> <cell_location.csv> <data.rds>...

suppressMessages(library(tidyverse))
suppressMessages(library(data.table))

args <- commandArgs(trailingOnly=TRUE)


read_cell_location <- function(in_csv) {
  read_csv(in_csv, col_types="fff") %>%
    as.data.table()
}

append_cell_location <- function(df, cell2location) {
  message("Merging with cell location")
  df[cell2location, on=c(Pickup_cell = "Cell"), c("Zone", "Borough") := list(Zone, Borough)]
  df %>%
    drop_na()
}


group_data <- function(df) {
  message("Grouping and aggregating")
  grouping <- c("Season", "Pickup_month", "Pickup_week", "Pickup_day", "Pickup_wday",
                "Weekend", "Pickup_hour", "Time", "Pickup_minute", "Borough", "Zone",
                "Pickup_cell")
  
  df[, .(Number_trips = .N, 
         Median_earnings = median(Total_earnings),
         Median_distance = median(Trip_distance),
         Median_duration = median(Trip_duration)),
     by = grouping]
}


main <- function(args) {
  if (length(args) <= 2) {
    stop("Incorrect number of arguments supplied", call.=FALSE)
  }
  
  out <- args[1]
  cell2location <- args[2] %>%
    read_cell_location()
  
  args <- args[c(-1, -2)]
  
  if (!grepl(".rds$", out)) {
    out <- paste0(out, ".rds")
  }
  
  lapply(args, function(x) {
    message("Reading ", x)
    readRDS(x) %>%
      append_cell_location(cell2location) %>%
      filter(Borough == "Manhattan")
  }) %>%
    rbindlist() %>%
    group_data() %>%
    saveRDS(out)
}

main(args)
