-- Table for all recorded triggers
CREATE TABLE IF NOT EXISTS all_triggers (
    path TEXT,
    box_min_x DECIMAL,
    box_min_y DECIMAL,
    box_max_x DECIMAL,
    box_max_y DECIMAL,
    start_frame DECIMAL,
    end_frame DECIMAL,
    data_collection_id DECIMAL,
    time_stamp TIMESTAMP
);
-- Table for data collections 
CREATE TABLE IF NOT EXISTS data_collections (name TEXT, timestamp TIMESTAMP);


-- Addin primary key to data_collections table
ALTER TABLE "data_collections"
ADD "id" smallserial NOT NULL,
    ADD PRIMARY KEY ("id");

ALTER TABLE "all_triggers"
ADD "id" smallserial NOT NULL,
ADD PRIMARY KEY ("id");
COMMENT ON TABLE "all_triggers" IS '';


COMMENT ON TABLE "data_collections" IS '';