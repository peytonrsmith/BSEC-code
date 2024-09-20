#Peyton Smith 8/24 prs243@cornell.edu

#  you need to download libraries if not already done 
library(tidycensus)
library(sf)
library(dplyr)
library(tigris)
library(tidyverse)

# create your own census api key 
census_api_key("273983b851bd05f546e743ac334b18277e8c67d1", install = TRUE)

baltimore_tracts <- tracts(state = "MD", county = "Baltimore City", year = 2020, cb = TRUE) %>%
  st_transform(crs = 4326) %>%
  mutate(centroid = st_centroid(geometry))

# choose file with stations of interest 
weather_data <- read.csv(choose.files())

# Create an sf object for weather stations
weather_sf <- st_as_sf(weather_data, coords = c("longitude", "latitude"), crs = 4326)

#not sure if these steps are necessary 
utm_crs <- 32618  # UTM Zone 18N

baltimore_tracts <- baltimore_tracts %>%
  st_transform(crs = utm_crs) %>%
  mutate(centroid = st_centroid(geometry))

weather_sf <- st_transform(weather_sf, crs = utm_crs)

# Function to find the nearest weather station
find_nearest_station <- function(census_point, weather_points) {
  distances <- st_distance(census_point, weather_points)
  nearest_index <- which.min(distances)
  return(weather_points[nearest_index, ])
}

# Calculate the nearest weather station for each census tract
baltimore_tracts <- baltimore_tracts %>%
  rowwise() %>%
  mutate(
    nearest_station = list(find_nearest_station(centroid, weather_sf$geometry)),
    distance_to_nearest_station = as.numeric(st_distance(centroid, nearest_station))
  )

# Extract nearest station details and distances into separate columns
baltimore_tracts <- baltimore_tracts %>%
  mutate(
    nearest_station_longitude = st_coordinates(nearest_station)[1],
    nearest_station_latitude = st_coordinates(nearest_station)[2]
  ) %>%
  select(GEOID, nearest_station_longitude, nearest_station_latitude, distance_to_nearest_station)

# change variable based on population of interest 
census_data <- get_acs(
  geography = "tract",
  variables = "B03002_012E",
  state = "MD",
  county = "Baltimore City",
  year = 2020,
  geometry = FALSE
) %>%
  rename(Hispanic_Population = estimate)

# Join the demographic data with the census tract data
baltimore_tracts <- baltimore_tracts %>%
  left_join(census_data, by = "GEOID") %>%
  mutate(weighted_distance = Hispanic_Population * distance_to_nearest_station)

# Sums the weighted distances and divides by the total number of Hispanic people
total_hispanic_population <- sum(baltimore_tracts$Hispanic_Population, na.rm = TRUE)
total_weighted_distance <- sum(baltimore_tracts$weighted_distance, na.rm = TRUE)
average_weighted_distance <- total_weighted_distance / total_hispanic_population

print(average_weighted_distance)
