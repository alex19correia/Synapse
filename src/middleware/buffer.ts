import { stringToBuffer, bufferToString } from '../lib/buffer';

const LARGE_STRING_THRESHOLD = 1024 * 50; // 50KB

/**
 * Middleware para converter grandes strings em Buffer
 */
export const bufferMiddleware = {
  /**
   * Converte strings grandes para Buffer antes de armazenar
   */
  beforeStore: (value: any): any => {
    if (typeof value === 'string' && value.length > LARGE_STRING_THRESHOLD) {
      return stringToBuffer(value);
    }
    return value;
  },

  /**
   * Converte Buffer de volta para string quando necessário
   */
  afterRetrieve: (value: any): any => {
    if (Buffer.isBuffer(value)) {
      return bufferToString(value);
    }
    return value;
  }
}; 