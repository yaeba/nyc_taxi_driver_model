#!/usr/bin/env Rscript
## Script to plot monthly total earnings vs day vs hour
## Usage: ./monthly_total_earnings <in.rds> <out.pdf>

suppressMessages(library(tidyverse))


args <- commandArgs(trailingOnly=TRUE)


plot_day_month <- function(df, month) {
  df %>%
    group_by(Pickup_day, Pickup_hour) %>%
    summarise(Total_earnings = median(Total_earnings)) %>%
    ggplot(aes(x=Pickup_day, y=Pickup_hour, fill=Total_earnings)) +
    geom_tile() +
    scale_fill_distiller(palette="Spectral") +
    scale_y_continuous(breaks=seq(0, 23)) +
    scale_x_continuous(breaks=seq(1, 31, 2)) +
    theme_bw() +
    labs(x="Day of the month", y="Hour of the day",
         title=paste(
           "Median total earnings in each day of month vs hour,",
           month)
    )
}


main <- function(args) {
  if (length(args) != 2) {
    stop("Incorrect number of arguments supplied", call.=FALSE)
  }
  
  infile <- args[1]
  plot_name <- args[2]
  
  if (!file.exists(infile)) {
    stop("File does not exist", call.=FALSE)
  }
  
  message("Found rds: ",infile)
  
  # Read data
  message("Reading rds")
  df <- readRDS(infile)
  
  # Plot data
  if (!grepl(".pdf$", plot_name)) {
    plot_name <- paste0(plot_name, ".pdf")
  }
  message("Plotting to ", plot_name)
  pdf(file=plot_name, width=7, height=7)
  
  months <- unique(df$Pickup_month)
  
  for (month in months) {
    message("Plotting ", month)
    
    df %>%
      filter(Pickup_month == month) %>%
      plot_day_month(month) %>%
      print() %>%
      invisible()
  }
  invisible(dev.off())

}

main(args)
