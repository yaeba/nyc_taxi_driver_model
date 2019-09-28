#!/usr/bin/env Rscript
## Script to plot monthly <quantity> vs day vs hour
## Usage: ./plot_monthly <quantity> <in.rds> <out.pdf>

suppressMessages(library(tidyverse))


args <- commandArgs(trailingOnly=TRUE)


plot_day_month <- function(df, quantity, month, year) {
  df %>%
    filter(Pickup_year == year, Pickup_month == month) %>%
    ggplot(aes_string(x="Pickup_day", y="Pickup_hour", fill=quantity)) +
    geom_tile() +
    scale_fill_distiller(palette="Spectral") +
    scale_y_continuous(breaks=seq(0, 23)) +
    scale_x_continuous(breaks=seq(1, 31, 2)) +
    theme_bw() +
    labs(x="Day of the month", y="Hour of the day",
         title=paste(
           quantity,
           "in each day of month vs hour,",
           month,
           year)
    )
}


main <- function(args) {
  if (length(args) != 3) {
    stop("Incorrect number of arguments supplied", call.=FALSE)
  }
  
  quantity <- args[1]
  infile <- args[2]
  plot_name <- args[3]
  
  if (!file.exists(infile)) {
    stop("File does not exist", call.=FALSE)
  }
  
  message("Found rds: ",infile)
  
  # Read data
  message("Reading rds")
  df <- readRDS(infile)
  
  if (!quantity %in% colnames(df)) {
    stop("Quantity does not exist in dataframe", call.=FALSE)
  }
  
  # Plot data
  if (!grepl(".pdf$", plot_name)) {
    plot_name <- paste0(plot_name, ".pdf")
  }
  message("Plotting to ", plot_name)
  pdf(file=plot_name, width=7, height=7)
  
  years <- unique(df$Pickup_year)
  
  for (year in years) {
    months <- unique(filter(df, Pickup_year == year)$Pickup_month)
    
    for (month in months) {
      message("Plotting ", month, " ", year)
      
      df %>%
        plot_day_month(quantity, month, year) %>%
        print() %>%
        invisible()
    }
  }
  invisible(dev.off())

}

main(args)
