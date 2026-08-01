CREATE TABLE users (
    id SERIAL PRIMARY KEY,
    full_name VARCHAR(255),
    role VARCHAR(50),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE image_cases (
    id SERIAL PRIMARY KEY,
    user_id INTEGER REFERENCES users(id),
    original_filename TEXT NOT NULL,
    stored_path TEXT NOT NULL,
    file_hash CHAR(64) NOT NULL,
    uploaded_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    status VARCHAR(50) NOT NULL
);

CREATE TABLE image_analysis (
    id SERIAL PRIMARY KEY,
    case_id INTEGER NOT NULL REFERENCES image_cases(id),
    real_score DOUBLE PRECISION NOT NULL,
    ai_score DOUBLE PRECISION NOT NULL,
    manipulated_score DOUBLE PRECISION NOT NULL,
    final_verdict VARCHAR(100) NOT NULL,
    confidence VARCHAR(50) NOT NULL,
    model_version VARCHAR(50) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE forensic_features (
    id SERIAL PRIMARY KEY,
    case_id INTEGER NOT NULL REFERENCES image_cases(id),
    exif_json JSONB,
    jpeg_quality DOUBLE PRECISION,
    has_camera_model BOOLEAN,
    software_tag TEXT,
    metadata_anomaly_score DOUBLE PRECISION,
    frequency_anomaly_score DOUBLE PRECISION
);

CREATE TABLE manipulation_masks (
    id SERIAL PRIMARY KEY,
    case_id INTEGER NOT NULL REFERENCES image_cases(id),
    mask_path TEXT,
    heatmap_path TEXT,
    edited_area_percent DOUBLE PRECISION
);

CREATE TABLE reports (
    id SERIAL PRIMARY KEY,
    case_id INTEGER NOT NULL REFERENCES image_cases(id),
    pdf_path TEXT,
    docx_path TEXT,
    json_path TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

