CREATE TABLE error_logs (
  id uuid DEFAULT gen_random_uuid() PRIMARY KEY,
  ticket_id VARCHAR(255),
  module_name VARCHAR(255),
  error_message TEXT,
  created_at TIMESTAMP WITH TIME ZONE DEFAULT timezone('utc'::text, now())
);
