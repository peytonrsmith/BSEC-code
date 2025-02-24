#8/2024 
#Peyton Smith prs243@cornell.edu
# Load necessary libraries (download if first time using R)
library(ggplot2)
library(sf)
library(readr)
library(ggmap)
library(dplyr)

# You will need to get your own google API key 
register_google(key = "AIzaSyCaTlNyemrm-Cmj3DJhOdxKDPvn2eq-c4Q")

# Prompts you to select the directory containing the CSV files
csv_directory <- choose.dir(caption = "Select Directory Containing Weather Stations CSV Files")

# Prompts you to select the directory to save the output maps
output_directory <- choose.dir(caption = "Select Output Directory for Maps")

# Prompts you to select the shapefile
shapefile_path <- choose.files(caption = "Select Shapefile")

# Define temperature bins and labels
bins <- c(-Inf, seq(16.5, 25.5, by = 1), Inf)
labels <- c(paste("<", 16.5, sep = ""), paste(seq(16.5, 24.5, by = 1), seq(17.5, 25.5, by = 1), sep = "-"), paste(">", 26.5, sep = ""))

# Defines a varied orange-red color palette with equal hue spacing
wider_palette <- c("#FFF7E1", "#FFE6AA", "#FFC678", "#FFA756", "#FF7040", "#FF4629", "#DB2320", "#A70E1A", "#800026", "#4B0010")
varied_palette <- colorRampPalette(wider_palette)(length(labels))
varied_color_palette <- setNames(varied_palette, labels)

# Function to process each CSV file and create a map
process_csv <- function(file_path, shapefile_path, output_directory) {
  # Extract date from the filename (assuming the date is part of the filename)
  file_name <- tools::file_path_sans_ext(basename(file_path))
  date_str <- str_extract(file_name, "\\d{4}-\\d{2}-\\d{2}")  # Assuming the date is in YYYY-MM-DD format
  
  # Load the shapefile
  baltimore_area <- st_read(shapefile_path)
  
  # Load the CSV file
  weatherstations <- read.csv(file_path)
  
  # Print column names to confirm correct indexing
  print(colnames(weatherstations))
  
  # Convert the ninth column to numeric for temperature
  weatherstations$Max_Temp <- as.numeric(as.character(weatherstations[[9]]))
  
  # Convert the DataFrame to an sf object
  weatherstations_sf <- st_as_sf(weatherstations, coords = c("Longitude", "Latitude"), crs = 4326)
  
  # Categorize temperature using the cut function
  weatherstations_sf$Temp_Category <- cut(weatherstations_sf$Max_Temp, breaks = bins, labels = labels, include.lowest = TRUE)
  weatherstations_sf$Temp_Category <- factor(weatherstations_sf$Temp_Category, levels = labels)  # Ensure consistent levels
  
  # Create a dummy data frame with all categories to ensure all are represented in the legend
  dummy_data <- data.frame(
    Longitude = rep(-76.6, length(labels)),  # Dummy longitude
    Latitude = rep(39.3, length(labels)),    # Dummy latitude
    Max_Temp = seq(16, 26, length.out = length(labels)),  # Dummy temperatures for each bin center
    Temp_Category = factor(labels, levels = labels),
    Station.Type = factor(rep("AWS", length(labels)), levels = c("AWS", "OTT", "GOV"))
  )
  
  # Convert dummy data to sf object
  dummy_sf <- st_as_sf(dummy_data, coords = c("Longitude", "Latitude"), crs = 4326)
  
  # Align columns of the dummy data and actual data
  common_cols <- intersect(names(weatherstations_sf), names(dummy_sf))
  weatherstations_sf <- weatherstations_sf[, common_cols]
  dummy_sf <- dummy_sf[, common_cols]
  
  # Combine the actual data with the dummy data
  combined_sf <- rbind(weatherstations_sf, dummy_sf)
  
  # Define the bounding box for the area of interest
  bbox <- st_bbox(baltimore_area)
  names(bbox) <- c("left", "bottom", "right", "top")
  
  # Hides pins on map that distract from weather stations 
  style <- '[{"featureType": "poi","elementType": "all","stylers": [{"visibility": "off"}]},
             {"featureType": "transit.station","elementType": "all","stylers": [{"visibility": "off"}]},
             {"featureType": "poi.medical","elementType": "all","stylers": [{"visibility": "off"}]},
             {"featureType": "poi.business","elementType": "all","stylers": [{"visibility": "off"}]},
             {"featureType": "poi.school","elementType": "all","stylers": [{"visibility": "off"}]},
             {"featureType": "poi.park","elementType": "all","stylers": [{"visibility": "off"}]},
             {"featureType": "poi.sports_complex","elementType": "all","stylers": [{"visibility": "off"}]},
             {"featureType": "poi.place_of_worship","elementType": "all","stylers": [{"visibility": "off"}]}]'
  
  # Get the map background with custom style
  google_map <- get_googlemap(center = c(lon = mean(bbox[c("left", "right")]), lat = mean(bbox[c("bottom", "top")])),
                              zoom = 11,
                              maptype = "roadmap",
                              style = style)
  
  # Plot the map
  plot <- ggmap(google_map) +
    geom_sf(data = baltimore_area, fill = NA, color = "black", size = 0.5, inherit.aes = FALSE) +
    geom_sf(data = combined_sf, aes(shape = Station.Type, fill = Temp_Category), size = 4, color = "black", stroke = 0.5, inherit.aes = FALSE) +
    scale_shape_manual(values = c("AWS" = 21, "OTT" = 22, "GOV" = 24), name = "Station Type") +
    scale_fill_manual(values = varied_color_palette, name = "Min Temperature (°C)", drop = FALSE) +  # Use fixed colors
    guides(
      fill = guide_legend(override.aes = list(shape = 21, size = 6)),
      shape = guide_legend(override.aes = list(size = 6))
    ) +
    labs(title = paste("Min Temperature Map", date_str),
         fill = "Temperature Range",
         shape = "Station Type") +
    theme_minimal() +
    theme(
      plot.title = element_text(size = 20, face = "bold"),
      legend.title = element_text(size = 12),
      legend.text = element_text(size = 10),
      axis.text.x = element_blank(),
      axis.text.y = element_blank(),
      axis.title.x = element_blank(),
      axis.title.y = element_blank(),
      axis.ticks = element_blank(),
      legend.position = "bottom"
    )
  
  # Save the plot in high quality
  output_file <- file.path(output_directory, paste0(file_name, "_map.png"))
  ggsave(output_file, plot = plot, width = 10, height = 8, dpi = 600)
}

# Process each CSV file in the selected directory
csv_files <- list.files(csv_directory, pattern = "\\.csv$", full.names = TRUE)
for (file in csv_files) {
  process_csv(file, shapefile_path, output_directory)
}
