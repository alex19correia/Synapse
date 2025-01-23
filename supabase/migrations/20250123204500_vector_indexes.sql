-- Drop existing indexes if they exist
DROP INDEX IF EXISTS idx_semantic_vector;
DROP INDEX IF EXISTS idx_keyword_vector;
DROP INDEX IF EXISTS idx_code_vector;

-- Add vector columns if they don't exist
DO $$
BEGIN
    IF NOT EXISTS (
        SELECT 1 FROM information_schema.columns 
        WHERE table_name = 'enhanced_documents' AND column_name = 'semantic_vector'
    ) THEN
        ALTER TABLE enhanced_documents ADD COLUMN semantic_vector vector(1536);
    END IF;

    IF NOT EXISTS (
        SELECT 1 FROM information_schema.columns 
        WHERE table_name = 'enhanced_documents' AND column_name = 'keyword_vector'
    ) THEN
        ALTER TABLE enhanced_documents ADD COLUMN keyword_vector vector(1536);
    END IF;

    IF NOT EXISTS (
        SELECT 1 FROM information_schema.columns 
        WHERE table_name = 'enhanced_documents' AND column_name = 'code_vector'
    ) THEN
        ALTER TABLE enhanced_documents ADD COLUMN code_vector vector(1536);
    END IF;
END
$$;

-- Drop existing trigger if exists
DROP TRIGGER IF EXISTS update_vectors ON enhanced_documents;

-- Create or replace the vector update function
CREATE OR REPLACE FUNCTION update_vector_columns()
RETURNS TRIGGER AS $$
BEGIN
    NEW.semantic_vector = (NEW.embeddings->>'semantic')::vector(1536);
    NEW.keyword_vector = (NEW.embeddings->>'keyword')::vector(1536);
    NEW.code_vector = (NEW.embeddings->>'code')::vector(1536);
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Create trigger for vector updates
CREATE TRIGGER update_vectors
    BEFORE INSERT OR UPDATE ON enhanced_documents
    FOR EACH ROW
    EXECUTE FUNCTION update_vector_columns();

-- Create vector-specific indexes
CREATE INDEX idx_semantic_vector ON enhanced_documents 
USING ivfflat (semantic_vector vector_cosine_ops);

CREATE INDEX idx_keyword_vector ON enhanced_documents 
USING ivfflat (keyword_vector vector_cosine_ops);

CREATE INDEX idx_code_vector ON enhanced_documents 
USING ivfflat (code_vector vector_cosine_ops); 