import '@testing-library/jest-dom';
import { vi } from 'vitest';

// Mock environment variables
vi.stubEnv('ANTHROPIC_API_KEY', 'test-api-key');
vi.stubEnv('POSTGRES_URL', 'postgresql://test:test@localhost:5432/test');
