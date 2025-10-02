# API Documentation

## Overview

REST API endpoints for the OAL Agent system.

## Endpoints

### POST /analysis
Submit a smart contract for analysis.

### GET /analysis/{job_id}
Get the status and results of an analysis job.

### GET /analysis/{job_id}/results
Get detailed results for a completed analysis.

## Schemas

See the `src/oal_agent/app/schemas/` directory for request/response schemas.
