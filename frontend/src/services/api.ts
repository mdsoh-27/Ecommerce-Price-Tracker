const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:5000';

console.log('API URL:', API_URL); // Debug log

export const trackProduct = async (product: string) => {
  try {
    const res = await fetch(`${API_URL}/track`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ product }),
    });
    
    if (!res.ok) {
      const errorData = await res.json().catch(() => ({}));
      throw new Error(errorData.error || `Failed to fetch product data (Status: ${res.status})`);
    }
    
    const data = await res.json();
    return data;
  } catch (error: any) {
    console.error('Track Product Error:', error);
    throw error;
  }
};

export const getPriceHistory = async (product: string) => {
  try {
    const res = await fetch(`${API_URL}/history/${encodeURIComponent(product)}`);
    
    if (!res.ok) {
      const errorData = await res.json().catch(() => ({}));
      throw new Error(errorData.error || `Failed to fetch price history (Status: ${res.status})`);
    }
    
    const data = await res.json();
    return data.history || data; // Handle both old and new format
  } catch (error: any) {
    console.error('Get Price History Error:', error);
    throw error;
  }
};

export const getLatestPrices = async (limit: number = 10) => {
  try {
    const res = await fetch(`${API_URL}/latest?limit=${limit}`);
    
    if (!res.ok) {
      const errorData = await res.json().catch(() => ({}));
      throw new Error(errorData.error || `Failed to fetch latest prices (Status: ${res.status})`);
    }
    
    const data = await res.json();
    return data.latest || data;
  } catch (error: any) {
    console.error('Get Latest Prices Error:', error);
    throw error;
  }
};

export const getPerformanceStats = async () => {
  try {
    const res = await fetch(`${API_URL}/performance`);
    
    if (!res.ok) {
      throw new Error(`Failed to fetch performance stats (Status: ${res.status})`);
    }
    
    return await res.json();
  } catch (error: any) {
    console.error('Get Performance Stats Error:', error);
    throw error;
  }
};
