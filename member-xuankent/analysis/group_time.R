#!/usr/bin/env Rscript
## Script to prepare dataset for each (day, hour) combination
## Usage: ./group_time.R  <out.rds> <year:in.rds>...

suppressMessages(library(tidyverse))
suppressMessages(library(data.table))

args <- commandArgs(trailingOnly=TRUE)


prepare_time_dataset <- function(infile) {
  message("Reading ", infile)
  readRDS(infile) %>%
    group_by(Season, Pickup_month, Pickup_week, 
             Pickup_wday, Weekend, Pickup_hour, 
             Time, Pickup_day) %>%
    summarise(Median_earnings = median(Total_earnings),
              Median_duration = median(Trip_duration),
              Median_distance = median(Trip_distance),
              Total_earnings = sum(Total_earnings),
              Trip_duration = sum(Trip_duration),
              Trip_distance = sum(Trip_distance),
              Trip_freq = n()) %>%
    ungroup()
}

main <- function(args) {
  if (length(args) <= 1) {
    stop("Incorrect number of arguments supplied", call.=FALSE)
  }
  
  out <- args[1]
  args <- args[-1]
  if (!all(grepl(':', args))) {
    stop("Name and rds must be separated by ':'", call.=FALSE)
  }
  
  
  if (!grepl(".rds$", out)) {
    out <- paste0(out, ".rds")
  }
  
  names_rds <- str_split(args, ':', simplify=TRUE)
  setNames(as.list(names_rds[, 2]), names_rds[, 1]) %>%
    lapply(prepare_time_dataset) %>%
    rbindlist(idcol="Pickup_year") %>%
    saveRDS(out)
}

main(args)
