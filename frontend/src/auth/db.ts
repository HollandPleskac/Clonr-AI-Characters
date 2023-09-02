const Pool = require('pg').Pool;

const pool = new Pool({
    user: process.env.POSTGRES_USER as string || "postgres",
    password: process.env.POSTGRES_PASSWORD as string || "postgres",
    database: process.env.POSTGRES_DB as string || "postgres",
    host: "postgres",
    port: parseInt(process.env.POSTGRES_PORT as string || "5432")
});

export default pool;