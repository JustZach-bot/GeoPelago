"""Item definitions for GeoPelago."""

BASE_ID = 7_340_000

# One item per country. These names must match the GeoPelago website exactly.
COUNTRY_NAMES = ['United States', 'Canada', 'Mexico', 'Brazil', 'Argentina', 'Chile', 'Colombia',
     'Peru', 'Ecuador', 'Bolivia', 'Uruguay', 'United Kingdom', 'Ireland', 'France',
     'Spain', 'Portugal', 'Italy', 'Germany', 'Netherlands', 'Belgium', 'Switzerland',
     'Austria', 'Poland', 'Czechia', 'Slovakia', 'Hungary', 'Romania', 'Bulgaria', 'Greece',
     'Croatia', 'Serbia', 'Denmark', 'Sweden', 'Norway', 'Finland', 'Iceland', 'Estonia',
     'Latvia', 'Lithuania', 'Ukraine', 'Turkey', 'Russia', 'Mongolia', 'Japan',
     'South Korea', 'Taiwan', 'Thailand', 'Indonesia', 'Philippines', 'Malaysia',
     'Singapore', 'India', 'Sri Lanka', 'Israel', 'Jordan', 'United Arab Emirates',
     'South Africa', 'Kenya', 'Senegal', 'Botswana', 'Australia', 'New Zealand']

FILLER_ITEM = "Map Pin"

ITEM_NAME_TO_ID = {name: BASE_ID + 1 + i for i, name in enumerate(COUNTRY_NAMES)}
ITEM_NAME_TO_ID[FILLER_ITEM] = BASE_ID + 500
