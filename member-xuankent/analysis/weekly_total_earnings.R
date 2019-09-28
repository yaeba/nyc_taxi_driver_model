#!/usr/bin/env Rscript
## Script to plot weekly total earnings vs wday vs hour
## Usage: ./weekly_total_earnings <in.rds> <out.pdf>

suppressMessages(library(tidyverse))


args <- commandArgs(trailingOnly=TRUE)


plot_day_week <- function(df, week) {
  df %>%
    group_by(Pickup_wday, Pickup_hour) %>%
    summarise(Total_earnings = median(Total_earnings)) %>%
    ggplot(aes(x=Pickup_wday, y=Pickup_hour, fill=Total_earnings)) +
    geom_tile() +
    scale_fill_distiller(palette="Spectral") +
    scale_y_continuous(breaks=seq(0, 23)) +
    theme_bw() +
    labs(x="Day of the week", y="Hour of the day",
         title=paste(
           "Median total earnings in each day of week vs hour,",
           week)
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
  
  weeks <- unique(df$Pickup_week)
  
  for (week in weeks) {
    message("Plotting week ", week)

    df %>%
      filter(Pickup_week == week) %>%
      plot_day_week(week) %>%
      print() %>%
      invisible()
  }
  invisible(dev.off())
  
}

main(args)
