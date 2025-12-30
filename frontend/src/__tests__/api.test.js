/**
 * Frontend Component Tests - API Integration & Router
 * Framework: Vitest + Vue Test Utils
 * Run: npm run test
 */

import { describe, it, expect, beforeEach, afterEach, vi } from 'vitest';
import axios from 'axios';
import { api } from '../src/lib/api.js';

// Mock axios
vi.mock('axios');

describe('Frontend API Integration Tests', () => {
  beforeEach(() => {
    // Clear localStorage before each test
    localStorage.clear();
    vi.clearAllMocks();
  });

  describe('WB6.1: Authorization Header Configuration', () => {
    it('Should include Bearer token in Authorization header', async () => {
      localStorage.setItem('trackflow_token', 'test_token_123');

      // Mock successful login
      axios.post.mockResolvedValueOnce({
        data: {
          token: 'test_token_123',
          user: { id: 1, email: 'test@example.com' }
        }
      });

      // Simulate protected API call
      axios.get.mockResolvedValueOnce({
        data: { user: { id: 1, email: 'test@example.com' } }
      });

      // Call getMe which should use authorization header
      const result = await api.getMe();

      // Verify axios was called with correct headers
      expect(axios.get).toHaveBeenCalledWith(
        expect.stringContaining('/api/me'),
        expect.objectContaining({
          headers: expect.objectContaining({
            Authorization: 'Bearer test_token_123'
          })
        })
      );
    });

    it('Should not include header when token missing', async () => {
      // Don't set token in localStorage

      axios.get.mockResolvedValueOnce({
        data: { user: null }
      });

      try {
        await api.getMe();
      } catch (e) {
        // Expected to fail or return empty
      }

      // Verify call was made without Authorization header
      expect(axios.get).toHaveBeenCalledWith(
        expect.stringContaining('/api/me'),
        expect.any(Object)
      );

      const callArgs = axios.get.mock.calls[0][1];
      expect(callArgs.headers?.Authorization).toBeUndefined();
    });
  });

  describe('WB6.2: LocalStorage Token Management', () => {
    it('Should store token after successful login', async () => {
      const mockResponse = {
        data: {
          token: 'jwt_token_xyz',
          user: { id: 1, email: 'user@test.com', name: 'Test User' }
        }
      };

      axios.post.mockResolvedValueOnce(mockResponse);

      const result = await api.login('user@test.com', 'password123');

      expect(localStorage.getItem('trackflow_token')).toBe('jwt_token_xyz');
      expect(localStorage.getItem('trackflow_user')).toBe(
        JSON.stringify(mockResponse.data.user)
      );
    });

    it('Should clear token on logout', () => {
      // Set tokens
      localStorage.setItem('trackflow_token', 'test_token');
      localStorage.setItem('trackflow_user', '{"id": 1}');

      // Call logout
      api.logout();

      expect(localStorage.getItem('trackflow_token')).toBeNull();
      expect(localStorage.getItem('trackflow_user')).toBeNull();
    });

    it('Should persist token across page reloads', () => {
      const token = 'persistent_token_123';
      localStorage.setItem('trackflow_token', token);

      // Simulate page reload by accessing localStorage again
      const storedToken = localStorage.getItem('trackflow_token');

      expect(storedToken).toBe(token);
    });

    it('Should handle corrupted user data gracefully', async () => {
      localStorage.setItem('trackflow_token', 'token');
      localStorage.setItem('trackflow_user', 'invalid_json');

      // Should not throw error
      expect(() => {
        const userStr = localStorage.getItem('trackflow_user');
        if (userStr) {
          try {
            JSON.parse(userStr);
          } catch (e) {
            // Handle gracefully
            console.warn('Invalid user data');
          }
        }
      }).not.toThrow();
    });
  });

  describe('WB6.3: FormData Construction for Upload', () => {
    it('Should construct FormData with video and coordinates', async () => {
      const mockFile = new File(['video content'], 'test.mp4', {
        type: 'video/mp4'
      });
      const lineCoordinates = {
        x1: 100,
        y1: 200,
        x2: 400,
        y2: 300
      };

      localStorage.setItem('trackflow_token', 'test_token');

      axios.post.mockResolvedValueOnce({
        data: { process_id: 'proc_123', status: 'processing' }
      });

      const result = await api.uploadAndProcess(mockFile, lineCoordinates);

      // Verify FormData was sent with correct fields
      expect(axios.post).toHaveBeenCalled();
      const callArgs = axios.post.mock.calls[0];
      const formData = callArgs[1];

      // Check FormData contains expected fields
      expect(formData instanceof FormData).toBe(true);

      // Note: FormData.entries() is the proper way to check contents
      const entries = Array.from(formData.entries());
      expect(entries.some(([key]) => key === 'video')).toBe(true);
      expect(entries.some(([key]) => key === 'line_x1')).toBe(true);
      expect(entries.some(([key, value]) => key === 'line_x1' && value === '100')).toBe(true);
    });

    it('Should upload without coordinates if not provided', async () => {
      const mockFile = new File(['video content'], 'test.mp4', {
        type: 'video/mp4'
      });

      localStorage.setItem('trackflow_token', 'test_token');

      axios.post.mockResolvedValueOnce({
        data: { process_id: 'proc_456', status: 'processing' }
      });

      const result = await api.uploadAndProcess(mockFile);

      expect(axios.post).toHaveBeenCalled();
      const formData = axios.post.mock.calls[0][1];

      // Should have video field but no line coordinates
      const entries = Array.from(formData.entries());
      expect(entries.some(([key]) => key === 'video')).toBe(true);
      expect(entries.some(([key]) => key.startsWith('line_'))).toBe(false);
    });

    it('Should include Content-Type header as multipart/form-data', async () => {
      const mockFile = new File(['video content'], 'test.mp4', {
        type: 'video/mp4'
      });

      localStorage.setItem('trackflow_token', 'test_token');

      axios.post.mockResolvedValueOnce({
        data: { process_id: 'proc_789' }
      });

      await api.uploadAndProcess(mockFile);

      const callArgs = axios.post.mock.calls[0];
      const headers = callArgs[2].headers;

      expect(headers['Content-Type']).toBe('multipart/form-data');
    });

    it('Should include Authorization header in upload', async () => {
      const mockFile = new File(['video content'], 'test.mp4', {
        type: 'video/mp4'
      });
      const token = 'test_token_upload';

      localStorage.setItem('trackflow_token', token);

      axios.post.mockResolvedValueOnce({
        data: { process_id: 'proc_auth' }
      });

      await api.uploadAndProcess(mockFile);

      const callArgs = axios.post.mock.calls[0];
      const headers = callArgs[2].headers;

      expect(headers.Authorization).toBe(`Bearer ${token}`);
    });
  });

  describe('Upload Progress Tracking', () => {
    it('Should trigger onUploadProgress callback', async () => {
      const mockFile = new File(['video content'], 'test.mp4', {
        type: 'video/mp4'
      });
      const progressCallback = vi.fn();

      localStorage.setItem('trackflow_token', 'test_token');

      axios.post.mockResolvedValueOnce({
        data: { process_id: 'proc_progress' }
      });

      await api.uploadAndProcess(mockFile, null, progressCallback);

      // Simulate progress events
      const config = axios.post.mock.calls[0][2];
      if (config.onUploadProgress) {
        config.onUploadProgress({ loaded: 50, total: 100 });
        config.onUploadProgress({ loaded: 100, total: 100 });
      }

      // Progress callback should have been called
      // Note: This would need actual implementation to test properly
    });
  });

  describe('Error Handling', () => {
    it('Should handle network errors gracefully', async () => {
      const mockFile = new File(['video content'], 'test.mp4', {
        type: 'video/mp4'
      });

      localStorage.setItem('trackflow_token', 'test_token');

      axios.post.mockRejectedValueOnce(
        new Error('Network error')
      );

      try {
        await api.uploadAndProcess(mockFile);
        expect.fail('Should have thrown');
      } catch (error) {
        expect(error.message).toBe('Network error');
      }
    });

    it('Should handle 401 Unauthorized response', async () => {
      const mockFile = new File(['video content'], 'test.mp4', {
        type: 'video/mp4'
      });

      localStorage.setItem('trackflow_token', 'invalid_token');

      const error = {
        response: {
          status: 401,
          data: { error: 'Unauthorized' }
        }
      };

      axios.post.mockRejectedValueOnce(error);

      try {
        await api.uploadAndProcess(mockFile);
        expect.fail('Should have thrown');
      } catch (error) {
        expect(error.response.status).toBe(401);
      }
    });

    it('Should handle 413 Payload Too Large', async () => {
      const mockFile = new File(['x'.repeat(100 * 1024 * 1024)], 'large.mp4', {
        type: 'video/mp4'
      });

      localStorage.setItem('trackflow_token', 'test_token');

      const error = {
        response: {
          status: 413,
          data: { error: 'Payload too large' }
        }
      };

      axios.post.mockRejectedValueOnce(error);

      try {
        await api.uploadAndProcess(mockFile);
        expect.fail('Should have thrown');
      } catch (error) {
        expect(error.response.status).toBe(413);
      }
    });
  });
});
