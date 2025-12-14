CREATE TABLE IF NOT EXISTS helmet_violations (
  id BIGSERIAL PRIMARY KEY,
  event_id UUID UNIQUE NOT NULL,
  camera_id TEXT NOT NULL,
  track_id INT NOT NULL,
  violation_type TEXT NOT NULL,
  confidence_ratio REAL NOT NULL,
  frame_index INT NOT NULL,
  event_time TIMESTAMPTZ NOT NULL,
  evidence_image TEXT NOT NULL,
  evidence_path TEXT NOT NULL,
  source_video TEXT NOT NULL,
  model_path TEXT NOT NULL,
  det_conf REAL NOT NULL,
  window_size INT NOT NULL,
  enter_ratio REAL NOT NULL,
  raw_json JSONB NOT NULL,
  created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_helmet_violations_time ON helmet_violations (event_time);
CREATE INDEX IF NOT EXISTS idx_helmet_violations_camera ON helmet_violations (camera_id);
