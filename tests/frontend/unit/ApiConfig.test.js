/**
 * Tests for config/api.js
 * Covers getApiUrl and getApiBaseUrl in different environments
 */

describe('API Configuration', () => {
  const originalEnv = process.env;

  beforeEach(() => {
    jest.resetModules();
    process.env = { ...originalEnv };
  });

  afterEach(() => {
    process.env = originalEnv;
  });

  describe('getApiUrl', () => {
    test('returns path with leading slash in development', () => {
      process.env.NODE_ENV = 'development';
      process.env.REACT_APP_API_URL = '';
      const { getApiUrl } = require('../../../frontend/src/config/api');
      expect(getApiUrl('/api/test')).toBe('/api/test');
    });

    test('strips double slash when path already has leading slash in development', () => {
      process.env.NODE_ENV = 'development';
      const { getApiUrl } = require('../../../frontend/src/config/api');
      const result = getApiUrl('/api/test');
      expect(result.startsWith('//')).toBe(false);
      expect(result).toBe('/api/test');
    });

    test('returns relative path when path has no leading slash in development', () => {
      process.env.NODE_ENV = 'development';
      const { getApiUrl } = require('../../../frontend/src/config/api');
      expect(getApiUrl('api/test')).toBe('/api/test');
    });

    test('prepends apiUrl in production when REACT_APP_API_URL is set', () => {
      process.env.NODE_ENV = 'production';
      process.env.REACT_APP_API_URL = 'https://backend.example.com';
      const { getApiUrl } = require('../../../frontend/src/config/api');
      expect(getApiUrl('/api/test')).toBe('https://backend.example.com/api/test');
    });

    test('returns relative path when no REACT_APP_API_URL in production', () => {
      process.env.NODE_ENV = 'production';
      delete process.env.REACT_APP_API_URL;
      const { getApiUrl } = require('../../../frontend/src/config/api');
      jest.spyOn(console, 'warn').mockImplementation(() => {});
      const result = getApiUrl('/api/test');
      expect(result).toBe('/api/test');
    });

    test('logs warning when no REACT_APP_API_URL in production', () => {
      process.env.NODE_ENV = 'production';
      delete process.env.REACT_APP_API_URL;
      const { getApiUrl } = require('../../../frontend/src/config/api');
      const warnSpy = jest.spyOn(console, 'warn').mockImplementation(() => {});
      getApiUrl('/api/test');
      expect(warnSpy).toHaveBeenCalledWith(expect.stringContaining('REACT_APP_API_URL'));
      warnSpy.mockRestore();
    });

    test('does NOT log warning in development mode', () => {
      process.env.NODE_ENV = 'development';
      const { getApiUrl } = require('../../../frontend/src/config/api');
      const warnSpy = jest.spyOn(console, 'warn').mockImplementation(() => {});
      getApiUrl('/api/test');
      expect(warnSpy).not.toHaveBeenCalled();
      warnSpy.mockRestore();
    });
  });

  describe('getApiBaseUrl', () => {
    test('returns empty string when no REACT_APP_API_URL', () => {
      delete process.env.REACT_APP_API_URL;
      const { getApiBaseUrl } = require('../../../frontend/src/config/api');
      expect(getApiBaseUrl()).toBe('');
    });

    test('returns configured URL when REACT_APP_API_URL is set', () => {
      process.env.REACT_APP_API_URL = 'https://api.example.com';
      const { getApiBaseUrl } = require('../../../frontend/src/config/api');
      expect(getApiBaseUrl()).toBe('https://api.example.com');
    });
  });

  describe('default config export', () => {
    test('isProduction is true when NODE_ENV is production', () => {
      process.env.NODE_ENV = 'production';
      const config = require('../../../frontend/src/config/api').default;
      expect(config.isProduction).toBe(true);
    });

    test('isDevelopment is true when NODE_ENV is development', () => {
      process.env.NODE_ENV = 'development';
      const config = require('../../../frontend/src/config/api').default;
      expect(config.isDevelopment).toBe(true);
    });

    test('apiUrl reflects REACT_APP_API_URL value', () => {
      process.env.REACT_APP_API_URL = 'https://custom.api.com';
      const config = require('../../../frontend/src/config/api').default;
      expect(config.apiUrl).toBe('https://custom.api.com');
    });

    test('apiUrl is empty string when REACT_APP_API_URL is not set', () => {
      delete process.env.REACT_APP_API_URL;
      const config = require('../../../frontend/src/config/api').default;
      expect(config.apiUrl).toBe('');
    });
  });
});
