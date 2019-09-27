#!/usr/bin/env Rscript
## Script to plot monthly total earnings vs day vs hour
## Usage: ./monthly_total_earnings <path> <pattern> <out_prefix>

suppressMessages(library(tidyverse))
suppressMessages(library(data.table))
suppressMessages(library(lubridate))


args <- commandArgs(trailingOnly=TRUE)

read_cols <- c("lpep_pickup_datetime", "Lpep_dropoff_datetime", 
               "PickupCell", "DropoffCell",
               "Passenger_count", "Trip_distance", 
               "Tip_amount", "Fare_amount", "Payment_type")

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
    rename(Pickup_datetime = lpep_pickup_datetime,
           Dropoff_datetime = Lpep_dropoff_datetime) %>%
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
           week(Pickup_datetime) == week(Dropoff_datetime),
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
           Weekend = Pickup_day %in% c("Sat", "Sun"),
           Time = ifelse(Pickup_hour >= 6 & Pickup_hour < 18,
                         "Daytime",
                         "Nighttime"),
           Time = factor(Time, levels=c("Daytime", "Nighttime")))
}

read_one_taxi_data <- function(filename, read_columns=read_cols,
                               out_columns=out_cols) {
  message("Reading ", filename)
  fread(filename, select=read_columns, fill=TRUE, showProgress=FALSE) %>%
    as_tibble() %>%
    rename(Pickup_cell = PickupCell, Dropoff_cell = DropoffCell) %>%
    compute_total_earnings() %>%
    compute_trip_duration() %>%
    clean_taxi_data() %>%
    extract_time_features() %>%
    select(out_columns)
}


read_all_taxi_data <- function(path, pattern) {
  lapply(list.files(path, pattern, full.names=TRUE), 
         function(x) read_one_taxi_data(x, read_cols, out_cols)) %>%
    rbindlist()
}


plot_day_month <- function(df, month) {
  df %>%
    group_by(Pickup_day, Pickup_hour) %>%
    summarise(Total_earnings = sum(Total_earnings)) %>%
    ggplot(aes(x=Pickup_day, y=Pickup_hour, fill=Total_earnings)) +
    geom_tile() +
    scale_fill_distiller(palette="Spectral") +
    scale_y_continuous(breaks=seq(0, 23)) +
    scale_x_continuous(breaks=seq(1, 31, 2)) +
    theme_bw() +
    labs(x="Day of the month", y="Hour of the day",
         title=paste(
           "Sum of total earnings in each day of month vs hour,",
           month)
    )
}


plot_day_week <- function(df, month) {
  df %>%
    group_by(Pickup_wday, Pickup_hour) %>%
    summarise(Total_earnings = sum(Total_earnings)) %>%
    ggplot(aes(x=Pickup_wday, y=Pickup_hour, fill=Total_earnings)) +
    geom_tile() +
    scale_fill_distiller(palette="Spectral") +
    scale_y_continuous(breaks=seq(0, 23)) +
    theme_bw() +
    labs(x="Day of the month", y="Hour of the day",
         title=paste(
           "Sum of total earnings in each day of week vs hour,",
           month)
    )
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
  
  # Plot data
  plot_name <- paste0(output, ".pdf")
  pdf(file=plot_name, width=7, height=7)
  
  months <- unique(df$Pickup_month)
  
  for (month in months) {
    message("Plotting ", month)
    tmp <- filter(df, Pickup_month == month)
    tmp %>%
      filter(Pickup_month == month) %>%
      plot_day_month(month) %>%
      print() %>%
      invisible()
    
    tmp %>%
      filter(Pickup_month == month) %>%
      plot_day_week(month) %>%
      print() %>%
      invisible()
  }
  dev.off()
  
  rm(tmp)
  
  # Save data
  message("Saving data")
  save_name <- paste0(output, ".rds")
  saveRDS(df, file=save_name)
}

main(args)
