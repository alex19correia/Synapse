import { useState, useCallback } from 'react';
import { bufferMiddleware } from '../middleware/buffer';

interface UseBufferedDataOptions {
  initialData?: any;
  autoBuffer?: boolean;
}

/**
 * Hook para gerenciar dados com buffer automaticamente
 */
export const useBufferedData = (options: UseBufferedDataOptions = {}) => {
  const { initialData, autoBuffer = true } = options;
  const [data, setData] = useState(initialData);

  /**
   * Armazena dados, convertendo para Buffer se necessário
   */
  const setBufferedData = useCallback((newData: any) => {
    if (autoBuffer) {
      setData(bufferMiddleware.beforeStore(newData));
    } else {
      setData(newData);
    }
  }, [autoBuffer]);

  /**
   * Recupera dados, convertendo de Buffer se necessário
   */
  const getBufferedData = useCallback(() => {
    if (autoBuffer && data) {
      return bufferMiddleware.afterRetrieve(data);
    }
    return data;
  }, [data, autoBuffer]);

  return {
    data: getBufferedData(),
    setData: setBufferedData,
    rawData: data,
  };
}; 