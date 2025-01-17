import { describe, expect, test } from '@jest/globals';

describe('Exemplo de Teste', () => {
  test('deve passar sempre', () => {
    expect(true).toBe(true);
  });

  test('deve fazer soma corretamente', () => {
    const soma = (a: number, b: number) => a + b;
    expect(soma(2, 2)).toBe(4);
  });

  // Exemplo de teste assíncrono
  test('deve resolver Promise corretamente', async () => {
    const asyncFunc = () => Promise.resolve('sucesso');
    const resultado = await asyncFunc();
    expect(resultado).toBe('sucesso');
  });
}); 