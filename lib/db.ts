import { Pool } from 'pg';

// Use a global variable to preserve the pool across module reloads in development
// (Next.js hot reloading can otherwise exhaust the connection pool)
const globalForDb = global as unknown as { db: Pool };

export const db = globalForDb.db || new Pool({
    connectionString: process.env.POSTGRES_URL,
    ssl: {
        rejectUnauthorized: false
    },
    max: 10,
    idleTimeoutMillis: 30000,
    connectionTimeoutMillis: 10000,
});

if (process.env.NODE_ENV !== 'production') globalForDb.db = db;
