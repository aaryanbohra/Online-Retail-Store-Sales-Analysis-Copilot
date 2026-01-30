import postgres from 'postgres';

const connectionString = process.env.DATABASE_URL || process.env.POSTGRES_URL;

console.log('Connection string check:');
console.log('DATABASE_URL:', process.env.DATABASE_URL ? 'set' : 'not set');
console.log('POSTGRES_URL:', process.env.POSTGRES_URL ? 'set' : 'not set');
console.log('Final connectionString:', connectionString ? connectionString.substring(0, 50) + '...' : 'undefined');

if (!connectionString) {
  throw new Error('DATABASE_URL or POSTGRES_URL environment variable is required');
}

export const sql = postgres(connectionString);
