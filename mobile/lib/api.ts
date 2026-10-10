import axios, { AxiosInstance } from 'axios';
import { useSettingsStore } from '@/store/providers';

const API_BASE_URL = __DEV__ 
  ? 'http://localhost:8000' 
  : 'https://api.openbird.org';

class ApiClient {
  private client: AxiosInstance;

  constructor() {
    this.client = axios.create({
      baseURL: API_BASE_URL,
      timeout: 10000,
      headers: {
        'Content-Type': 'application/json',
      },
    });

    this.client.interceptors.request.use((config) => {
      const language = useSettingsStore.getState().language;
      config.headers['Accept-Language'] = language;
      return config;
    });
  }

  async searchSpecies(query: string, limit = 20) {
    const response = await this.client.get('/api/search', {
      params: { q: query, limit },
    });
    return response.data;
  }

  async getSpecies(scientificName: string) {
    const response = await this.client.get(`/api/species/${encodeURIComponent(scientificName)}`);
    return response.data;
  }

  async getTaxonomy() {
    const response = await this.client.get('/api/taxonomy');
    return response.data;
  }

  async getSpeciesByFamily(family: string) {
    const response = await this.client.get('/api/taxonomy/family', {
      params: { family },
    });
    return response.data;
  }

  async getSpeciesByOrder(order: string) {
    const response = await this.client.get('/api/taxonomy/order', {
      params: { order },
    });
    return response.data;
  }

  async getFilters() {
    const response = await this.client.get('/api/filters');
    return response.data;
  }
}

export const api = new ApiClient();