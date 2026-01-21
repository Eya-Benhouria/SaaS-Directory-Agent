import axios from 'axios';
import type {
    ActivityLog,
    DashboardStats,
    Directory,
    DirectoryCreate,
    SaaSProduct,
    SaaSProductCreate,
    SaaSProductWithStats,
    Submission,
    SubmissionTrend,
    SubmissionWithDetails
} from '../types';

const api = axios.create({
  baseURL: '/api',
  headers: {
    'Content-Type': 'application/json',
  },
});

// SaaS Products
export const productApi = {
  list: async (): Promise<SaaSProduct[]> => {
    const { data } = await api.get('/saas-products');
    return data;
  },

  get: async (id: number): Promise<SaaSProductWithStats> => {
    const { data } = await api.get(`/saas-products/${id}`);
    return data;
  },

  create: async (product: SaaSProductCreate): Promise<SaaSProduct> => {
    const { data } = await api.post('/saas-products', product);
    return data;
  },

  update: async (id: number, product: Partial<SaaSProductCreate>): Promise<SaaSProduct> => {
    const { data } = await api.put(`/saas-products/${id}`, product);
    return data;
  },

  delete: async (id: number): Promise<void> => {
    await api.delete(`/saas-products/${id}`);
  },

  uploadLogo: async (id: number, file: File): Promise<SaaSProduct> => {
    const formData = new FormData();
    formData.append('file', file);
    const { data } = await api.post(`/saas-products/${id}/logo`, formData, {
      headers: { 'Content-Type': 'multipart/form-data' },
    });
    return data;
  },
};

// Directories
export const directoryApi = {
  list: async (status?: string, category?: string): Promise<Directory[]> => {
    const params = new URLSearchParams();
    if (status) params.append('status', status);
    if (category) params.append('category', category);
    const { data } = await api.get(`/directories?${params}`);
    return data;
  },

  getActive: async (): Promise<Directory[]> => {
    const { data } = await api.get('/directories/active');
    return data;
  },

  get: async (id: number): Promise<Directory> => {
    const { data } = await api.get(`/directories/${id}`);
    return data;
  },

  create: async (directory: DirectoryCreate): Promise<Directory> => {
    const { data } = await api.post('/directories', directory);
    return data;
  },

  bulkCreate: async (directories: DirectoryCreate[]): Promise<Directory[]> => {
    const { data } = await api.post('/directories/bulk', { directories });
    return data;
  },

  update: async (id: number, directory: Partial<DirectoryCreate>): Promise<Directory> => {
    const { data } = await api.put(`/directories/${id}`, directory);
    return data;
  },

  delete: async (id: number): Promise<void> => {
    await api.delete(`/directories/${id}`);
  },

  analyze: async (id: number): Promise<void> => {
    await api.post(`/directories/${id}/analyze`);
  },

  getCategories: async (): Promise<string[]> => {
    const { data } = await api.get('/directories/categories');
    return data;
  },
};

// Submissions
export const submissionApi = {
  list: async (
    productId?: number, 
    directoryId?: number, 
    status?: string
  ): Promise<SubmissionWithDetails[]> => {
    const params = new URLSearchParams();
    if (productId) params.append('saas_product_id', productId.toString());
    if (directoryId) params.append('directory_id', directoryId.toString());
    if (status) params.append('status', status);
    const { data } = await api.get(`/submissions?${params}`);
    return data;
  },

  get: async (id: number): Promise<SubmissionWithDetails> => {
    const { data } = await api.get(`/submissions/${id}`);
    return data;
  },

  create: async (productId: number, directoryId: number): Promise<Submission> => {
    const { data } = await api.post('/submissions', { 
      saas_product_id: productId, 
      directory_id: directoryId 
    });
    return data;
  },

  bulkCreate: async (productId: number, directoryIds: number[]): Promise<Submission[]> => {
    const { data } = await api.post('/submissions/bulk', { 
      saas_product_id: productId, 
      directory_ids: directoryIds 
    });
    return data;
  },

  run: async (id: number): Promise<void> => {
    await api.post(`/submissions/${id}/run`);
  },

  retry: async (id: number): Promise<void> => {
    await api.post(`/submissions/${id}/retry`);
  },

  updateStatus: async (id: number, status: string, listingUrl?: string): Promise<Submission> => {
    const params = new URLSearchParams();
    params.append('status', status);
    if (listingUrl) params.append('listing_url', listingUrl);
    const { data } = await api.put(`/submissions/${id}/status?${params}`);
    return data;
  },

  delete: async (id: number): Promise<void> => {
    await api.delete(`/submissions/${id}`);
  },

  getStats: async (): Promise<DashboardStats> => {
    const { data } = await api.get('/submissions/stats');
    return data;
  },

  runBatch: async (limit: number = 5): Promise<{ count: number; submission_ids: number[] }> => {
    const { data } = await api.post(`/submissions/run-batch?limit=${limit}`);
    return data;
  },
};

// Dashboard
export const dashboardApi = {
  getStats: async (): Promise<DashboardStats> => {
    const { data } = await api.get('/dashboard/stats');
    return data;
  },

  getTrends: async (days: number = 7): Promise<SubmissionTrend[]> => {
    const { data } = await api.get(`/dashboard/trends?days=${days}`);
    return data;
  },

  getRecentActivity: async (limit: number = 20): Promise<ActivityLog[]> => {
    const { data } = await api.get(`/dashboard/recent-activity?limit=${limit}`);
    return data;
  },

  getTopDirectories: async (limit: number = 10): Promise<Directory[]> => {
    const { data } = await api.get(`/dashboard/top-directories?limit=${limit}`);
    return data;
  },

  getSystemStatus: async (): Promise<{
    app_name: string;
    app_version: string;
    demo_mode: boolean;
    llm_provider: string;
    has_openai_key: boolean;
    has_anthropic_key: boolean;
    status: string;
  }> => {
    const { data } = await api.get('/dashboard/system-status');
    return data;
  },
};

export default api;
