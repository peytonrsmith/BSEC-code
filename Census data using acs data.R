#Peyton Smith 8/24 prs243@cornell.edu 

# you need to download libraries if not already done 
library(tidycensus)
library(sf)
library(dplyr)
library(tigris)

# create your own census api key 
census_api_key("273983b851bd05f546e743ac334b18277e8c67d1", install = TRUE)

baltimore_tracts <- tracts(state = "MD", county = "Baltimore City", year = 2020, cb = TRUE) %>%
  st_transform(crs = 4326) %>%
  mutate(centroid = st_centroid(geometry))  # Calculate centroid of each tract

# choose files of weather stations interested in. All should be in the google drive. 
weather_data <- read.csv(choose.files())


weather_sf <- st_as_sf(weather_data, coords = c("Longitude", "Latitude"), crs = 4326)

# Finds the nearest weather station for each census tract centroid
nearest_station_indices <- st_nearest_feature(baltimore_tracts$centroid, weather_sf)

# Extract the closest weather stations using the indices
closest_stations <- weather_sf[nearest_station_indices, ]

# Calculate the distances to the closest station
closest_distances <- st_distance(baltimore_tracts$centroid, closest_stations, by_element = TRUE)

# Add the nearest station and distance to the census tract data
baltimore_tracts <- baltimore_tracts %>%
  mutate(distance_to_nearest_station = as.numeric(closest_distances))  

# change variable code to population of interest 
acs_data_all_years <- data.frame()

for (year in 2019:2023) {
  acs_data <- try(get_acs(
    geography = "tract",
    variables = "B03002_012E",  # Hispanic or Latino population
    state = "MD",
    county = "Baltimore City",
    year = year
  ) %>%
    rename(population = estimate) %>%
    mutate(Year = year))  
  
  # If data retrieval was successful, append to the dataframe
  if (!inherits(acs_data, "try-error")) {
    acs_data_all_years <- bind_rows(acs_data_all_years, acs_data)
  }
}

# Joins the ACS data with the census tract data
baltimore_tracts <- baltimore_tracts %>%
  left_join(acs_data_all_years, by = "GEOID") %>%
  mutate(weighted_distance = population * distance_to_nearest_station)

# Calculates total pop of interest and sums distnaces 
total_population <- sum(baltimore_tracts$population, na.rm = TRUE)
total_weighted_distance <- sum(baltimore_tracts$weighted_distance, na.rm = TRUE)

# Calculates the average distance 
average_weighted_distance <- total_weighted_distance / total_population

# Print the average weighted distance for Hispanic population
print(average_weighted_distance)

# Save the combined results with weighted distance to a CSV
write.csv(baltimore_tracts, "baltimore_tracts_with_weighted_distances_hispanic_2019_2023.csv", row.names = FALSE)
