#!/usr/bin/env Rscript
## Script to prepare yearly trips dataset
## Usage: ./prepare_dataset.R <path> <pattern> <out.rds>

suppressMessages(library(tidyverse))
suppressMessages(library(data.table))
suppressMessages(library(lubridate))


args <- commandArgs(trailingOnly=TRUE)

read_cols <- c("Pickup_datetime", "Dropoff_datetime", 
               "Passenger_count", "Trip_distance", 
               "Tip_amount", "Fare_amount", "Payment_type",
               "Pickup_cell", "Dropoff_cell")

keep_cols <- c("lpep_pickup_datetime", "Lpep_dropoff_datetime", 
               "lpep_dropoff_datetime",
               "tpep_pickup_datetime", "tpep_dropoff_datetime",
               "Passenger_count", "passenger_count", 
               "Trip_distance", "trip_distance",
               "Tip_amount", "tip_amount", 
               "Fare_amount", "fare_amount",
               "Payment_type", "payment_type",
               "PickupCell", "DropoffCell")

out_cols <- c("Season", "Pickup_month", "Pickup_week", "Pickup_wday", 
              "Weekend", "Pickup_hour", "Time", "Pickup_day", 
              "Pickup_minute", "Pickup_cell", "Dropoff_cell",
              "Trip_distance", "Trip_duration", "Total_earnings")

# function to compute total earnings
compute_total_earnings <- function(taxi_data) {
  taxi_data %>%
    mutate(Total_earnings = Fare_amount + Tip_amount)
}

# function to compute trip duration
compute_trip_duration <- function(taxi_data) {
  taxi_data %>%
    mutate(Pickup_datetime = ymd_hms(Pickup_datetime),
           Dropoff_datetime = ymd_hms(Dropoff_datetime),
           Trip_duration = difftime(Dropoff_datetime, Pickup_datetime, units="mins"),
           Trip_duration = as.numeric(Trip_duration) %>% round(digits=2))
}

clean_taxi_data <- function(taxi_data) {
  taxi_data %>%
    # remove rows with missing value(s)
    drop_na() %>%
    # data cleansing
    filter(Passenger_count > 0, Passenger_count <= 6,
           Trip_duration > 1, Trip_duration < (2 * 60),
           Total_earnings > 0, Total_earnings < 100,
           wday(Pickup_datetime, label=T) != "Sun" & wday(Dropoff_datetime, label=T) != "Mon",
           Pickup_cell != "", Dropoff_cell != "",
           Payment_type <= 2)
}

# helper function to return US season
season <- function(datetime) {
  m <- month(datetime)
  terms <- c("Spring", "Summer", "Autumn", "Winter")
  s <- factor(character(length(m)), levels=terms)
  s[m %in% c(3, 4, 5)] <- terms[1]
  s[m %in% c(6, 7, 8)] <- terms[2]
  s[m %in% c(9, 10, 11)] <- terms[3]
  s[m %in% c(12, 1, 2)] <- terms[4]
  s
}


# function to extract day time-related features
extract_time_features <- function(taxi_data) {
  taxi_data %>%
    mutate(Pickup_month = month(Pickup_datetime, label=TRUE),
           Pickup_week = week(Pickup_datetime),
           Pickup_wday = wday(Pickup_datetime, label=TRUE),
           Pickup_day = day(Pickup_datetime),
           Pickup_hour = hour(Pickup_datetime),
           Pickup_minute = minute(Pickup_datetime),
           Season = season(Pickup_datetime),
           Weekend = Pickup_wday %in% c("Sat", "Sun"),
           Time = ifelse(Pickup_hour >= 6 & Pickup_hour < 18,
                         "Daytime",
                         "Nighttime"),
           Time = factor(Time, levels=c("Daytime", "Nighttime")))
}


read_columns <- function(filename, keep_cols) {
  header <- fread(filename, nrows=1, header=FALSE) %>%
    unlist()
  header[header %in% keep_cols]
}

read_one_taxi_data <- function(filename, read_columns=read_cols,
                               out_columns=out_cols,
                               keep_columns=keep_cols) {
  message("Reading ", filename)
  cols <- read_columns(filename, keep_columns)
  fread(filename, select=cols, fill=TRUE, 
        showProgress=FALSE, col.names=read_columns) %>%
    as_tibble() %>%
    compute_total_earnings() %>%
    compute_trip_duration() %>%
    clean_taxi_data() %>%
    extract_time_features() %>%
    mutate_at(vars(Pickup_cell, Dropoff_cell), factor) %>%
    select(out_columns)
}


read_all_taxi_data <- function(path, pattern) {
  lapply(list.files(path, pattern, full.names=TRUE), 
         function(x) read_one_taxi_data(x, read_cols, out_cols)) %>%
    rbindlist()
}


main <- function(args) {
  if (length(args) != 3) {
    stop("Incorrect number of arguments supplied", call.=FALSE)
  }
  
  path <- args[1]
  pattern <- args[2]
  output <- args[3]
  
  message("Found file(s): ", list.files(path, pattern))
  
  # Read data
  message("Reading data")
  df <- read_all_taxi_data(path, pattern)
  
  
  # Save data
  message("Saving data")
  if (!grepl(".rds$", output)) {
    output <- paste0(output, ".rds")
  }
  saveRDS(df, file=output)
}

main(args)
