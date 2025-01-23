-- Function to get index statistics
CREATE OR REPLACE FUNCTION get_index_stats()
RETURNS TABLE (
    index_name TEXT,
    total_scans BIGINT,
    avg_scan_time FLOAT,
    size_bytes BIGINT,
    last_vacuum TIMESTAMP WITH TIME ZONE
)
LANGUAGE plpgsql
AS $$
BEGIN
    RETURN QUERY
    SELECT
        schemaname || '.' || indexrelname AS index_name,
        idx_scan AS total_scans,
        COALESCE(avg_scan_time, 0) AS avg_scan_time,
        pg_relation_size(indexrelid) AS size_bytes,
        last_vacuum
    FROM
        pg_stat_user_indexes
        JOIN pg_index ON pg_index.indexrelid = pg_stat_user_indexes.indexrelid
        JOIN pg_class ON pg_class.oid = pg_index.indexrelid
    WHERE
        indexrelname LIKE '%vector%';
END;
$$;

-- Function to analyze vector query performance
CREATE OR REPLACE FUNCTION analyze_vector_query(
    query_embedding VECTOR,
    embedding_type TEXT
)
RETURNS TABLE (
    query_plan JSONB,
    estimated_cost FLOAT,
    actual_time FLOAT
)
LANGUAGE plpgsql
AS $$
BEGIN
    -- Create temporary table for EXPLAIN output
    CREATE TEMP TABLE IF NOT EXISTS explain_output (
        plan JSONB
    );
    
    -- Execute EXPLAIN ANALYZE and capture results
    EXECUTE format('
        EXPLAIN (FORMAT JSON, ANALYZE, TIMING)
        SELECT id, content, metadata
        FROM enhanced_documents
        WHERE 1 - (embeddings->>%L)::vector <=> %L::vector > 0.5
        ORDER BY 1 - (embeddings->>%L)::vector <=> %L::vector DESC
        LIMIT 5',
        embedding_type, query_embedding, embedding_type, query_embedding
    );
    
    -- Return query plan analysis
    RETURN QUERY
    SELECT
        plan,
        (plan->0->'Plan'->>'Total Cost')::float AS estimated_cost,
        (plan->0->'Plan'->>'Actual Total Time')::float AS actual_time
    FROM explain_output;
    
    -- Cleanup
    DROP TABLE IF EXISTS explain_output;
END;
$$; 