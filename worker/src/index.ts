import { getWeatherInChiyoda } from "./weather";

export default {
  async fetch(request): Promise<Response> {
    const data = await getWeatherInChiyoda();
    return Response.json(data);
  },
} satisfies ExportedHandler;
