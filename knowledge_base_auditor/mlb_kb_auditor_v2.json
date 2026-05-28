CREATE TABLE knowledge_base_index (
  id uuid DEFAULT gen_random_uuid() PRIMARY KEY,
  doc_id VARCHAR(255),
  title VARCHAR(255),
  key_phrases TEXT,
  created_at TIMESTAMP WITH TIME ZONE DEFAULT timezone('utc'::text, now())
);
