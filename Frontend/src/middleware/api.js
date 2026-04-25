/**
 * Middleware Frontend para intercepción y gestión centralizada de llamadas a la API.
 * El cliente pide a la dirección relativa del frontend (ej localhost:3000) de forma implícita.
 * Vite intercepta '/api/*' y lo envía al Backend 5000.
 */

// Configuramos la URL base. 
// En producción (dentro de Docker), las peticiones deben ser relativas al host del cliente (navegador).
// El proxy de Vite se encarga de redirigir '/api' al backend.
const API_BASE_URL = '/api';

/**
 * Función middleware central para manejar peticiones, logs y formateo de fallos.
 */
async function fetchFromMiddleware(endpoint, options = {}) {
  try {
    const response = await fetch(`${API_BASE_URL}${endpoint}`, {
      ...options,
      headers: {
        'Content-Type': 'application/json',
        ...options.headers,
      },
    });

    if (!response.ok) {
      throw new Error(`HTTP ERROR: ${response.status}`);
    }

    const data = await response.json();
    return { data, error: null };
  } catch (err) {
    console.error(`[Middleware Error] en petición a ${endpoint}:`, err);
    return { data: null, error: err.message };
  }
}

/**
 * Servicios abstraidos para ser consumidos por React.
 */
export const platformAPI = {
  // Obtiene el estado holístico del dashboard desde /api/all
  getAllDashboardData: async () => {
    return await fetchFromMiddleware('/all');
  }
};
