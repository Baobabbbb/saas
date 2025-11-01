-- Migration Stripe Production Setup

-- Fix generation_permissions table
ALTER TABLE generation_permissions
DROP COLUMN IF EXISTS is_active,
ADD COLUMN IF NOT EXISTS is_active BOOLEAN DEFAULT true,
ALTER COLUMN user_id TYPE uuid USING user_id::uuid,
ADD CONSTRAINT fk_generation_permissions_user_id
  FOREIGN KEY (user_id) REFERENCES profiles(id) ON DELETE CASCADE;

-- Fix payment_history table
ALTER TABLE payment_history
ALTER COLUMN user_id TYPE uuid USING user_id::uuid,
ADD CONSTRAINT fk_payment_history_user_id
  FOREIGN KEY (user_id) REFERENCES profiles(id) ON DELETE CASCADE;

-- Add updated_at columns for tracking
ALTER TABLE generation_permissions
ADD COLUMN IF NOT EXISTS updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW();

ALTER TABLE payment_history
ADD COLUMN IF NOT EXISTS updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW();

-- Create index for better performance
CREATE INDEX IF NOT EXISTS idx_generation_permissions_user_content
ON generation_permissions(user_id, content_type, is_active);

CREATE INDEX IF NOT EXISTS idx_generation_permissions_stripe_payment
ON generation_permissions(stripe_payment_intent_id);

CREATE INDEX IF NOT EXISTS idx_payment_history_user
ON payment_history(user_id);

CREATE INDEX IF NOT EXISTS idx_payment_history_stripe
ON payment_history(stripe_payment_id);
