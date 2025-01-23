-- Enable pgvector extension if not enabled
CREATE EXTENSION IF NOT EXISTS vector;

-- Create enhanced documents table
CREATE TABLE IF NOT EXISTS enhanced_documents (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    content TEXT NOT NULL,
    embeddings JSONB NOT NULL, -- Stores multiple embeddings as JSON
    metadata JSONB NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT TIMEZONE('utc', NOW()),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT TIMEZONE('utc', NOW())
);

-- Create function to match documents using specific embedding type
CREATE OR REPLACE FUNCTION match_enhanced_documents(
    query_embedding VECTOR,
    embedding_type TEXT,
    match_threshold FLOAT DEFAULT 0.5,
    match_count INT DEFAULT 5
)
RETURNS TABLE (
    id UUID,
    content TEXT,
    metadata JSONB,
    similarity FLOAT
)
LANGUAGE plpgsql
AS $$
BEGIN
    RETURN QUERY
    SELECT
        d.id,
        d.content,
        d.metadata,
        1 - (d.embeddings->>embedding_type)::vector <=> query_embedding AS similarity
    FROM
        enhanced_documents d
    WHERE
        d.embeddings ? embedding_type -- Check if embedding type exists
        AND 1 - (d.embeddings->>embedding_type)::vector <=> query_embedding > match_threshold
    ORDER BY
        similarity DESC
    LIMIT
        match_count;
END;
$$;

-- Create function to cast JSONB to vector (IMMUTABLE)
CREATE OR REPLACE FUNCTION jsonb_to_vector(embedding JSONB)
RETURNS vector
LANGUAGE plpgsql
IMMUTABLE
PARALLEL SAFE
AS $$
BEGIN
    RETURN (embedding#>>'{}')::vector;
END;
$$;

-- Create updated_at function
        CREATE OR REPLACE FUNCTION update_updated_at_column()
        RETURNS TRIGGER AS $$
        BEGIN
            NEW.updated_at = TIMEZONE('utc', NOW());
            RETURN NEW;
        END;
        $$ language 'plpgsql';

-- Drop trigger if exists
DROP TRIGGER IF EXISTS update_enhanced_documents_updated_at ON enhanced_documents;

-- Create trigger
        CREATE TRIGGER update_enhanced_documents_updated_at
            BEFORE UPDATE ON enhanced_documents
            FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

-- Create basic indexes
DROP INDEX IF EXISTS idx_semantic;
DROP INDEX IF EXISTS idx_keyword;
DROP INDEX IF EXISTS idx_code;

CREATE INDEX IF NOT EXISTS idx_semantic ON enhanced_documents ((embeddings->>'semantic'));
CREATE INDEX IF NOT EXISTS idx_keyword ON enhanced_documents ((embeddings->>'keyword'));
CREATE INDEX IF NOT EXISTS idx_code ON enhanced_documents ((embeddings->>'code')); 