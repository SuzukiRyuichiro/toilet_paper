import { fetchWeatherApi } from "openmeteo";
import { weatherCodeData } from "./weather-code-data";

const fixToOneDecimal = (number: Number) => {
  return parseFloat(number.toFixed(1));
};

export const getWeatherInChiyoda = async () => {
  const params = {
    latitude: 35.6917,
    longitude: 139.7619,
    daily: [
      "weather_code",
      "temperature_2m_max",
      "temperature_2m_min",
      "precipitation_sum",
    ],
    past_days: 0,
    forecast_days: 3,
  };
  const url = "https://api.open-meteo.com/v1/forecast";
  const responses = await fetchWeatherApi(url, params);

  // Process first location. Add a for-loop for multiple locations or weather models
  const response = responses[0];

  // Attributes for timezone and location
  const latitude = response.latitude();
  const longitude = response.longitude();
  const elevation = response.elevation();
  const utcOffsetSeconds = response.utcOffsetSeconds();
  const daily = response.daily()!;

  // Note: The order of weather variables in the URL query and the indices below need to match!
  const dailyData = {
    time: Array.from(
      {
        length:
          (Number(daily.timeEnd()) - Number(daily.time())) / daily.interval(),
      },
      (_, i) =>
        new Date(
          (Number(daily.time()) + i * daily.interval() + utcOffsetSeconds) *
            1000,
        ),
    ),
    weather_code: [...daily.variables(0)!.valuesArray()],
    temperature_2m_max: [...daily.variables(1)!.valuesArray()].map(
      fixToOneDecimal,
    ),
    temperature_2m_min: [...daily.variables(2)!.valuesArray()].map(
      fixToOneDecimal,
    ),
    precipitation_sum: [...daily.variables(3)!.valuesArray()].map(
      fixToOneDecimal,
    ),
  };

  // Reshape into an array of day objects with Japanese descriptions and icon bytearrays
  const weatherData = dailyData.time.map((date, i) => {
    const code = dailyData.weather_code[i];
    const codeData = weatherCodeData[code] || weatherCodeData[0];

    return {
      date: date.toISOString(),
      weather: {
        description: codeData.descriptionJa,
        icon: codeData.icon,
      },
      temperature_2m_min: dailyData.temperature_2m_min[i],
      temperature_2m_max: dailyData.temperature_2m_max[i],
      precipitation_sum: dailyData.precipitation_sum[i],
    };
  });

  // The 'weatherData' object now contains a simple structure, with arrays of datetimes and weather information
  console.log("\nDaily data:\n", weatherData);

  return weatherData;
};
