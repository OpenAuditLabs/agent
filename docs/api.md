# API Documentation

## Overview

REST API endpoints for the OAL Agent system.

## API Endpoints Summary

| Path                        | Method | Request Schema    | Response Schema         | Description                                     |
| :-------------------------- | :----- | :---------------- | :---------------------- | :---------------------------------------------- |
| `/`                         | `GET`  | -                 | `dict`                  | Root endpoint.                                  |
| `/health`                   | `GET`  | -                 | `dict`                  | Health check endpoint.                          |
| `/ready`                    | `GET`  | -                 | `dict`                  | Readiness check endpoint.                       |
| `/metrics`                  | `GET`  | -                 | `dict`                  | Metrics endpoint.                               |
| `/build-info`               | `GET`  | -                 | `dict`                  | Returns build information.                      |
| `/api/v1/analysis`          | `HEAD` | -                 | -                       | Perform a readiness check for analysis service. |
| `/api/v1/analysis`          | `POST` | `JobRequest`      | `JobResponse`           | Submit a smart contract for analysis.           |
| `/api/v1/analysis/{job_id}` | `GET`  | -                 | `JobResponse`           | Get the status of an analysis job.              |
| `/api/v1/analysis/{job_id}/results` | `GET`  | -                 | `AnalysisResult`        | Get the results of an analysis job.             |
| `/api/v1/items`             | `GET`  | `PaginationParams`| `PaginatedItemsResponse`| Retrieve a paginated list of all items.         |
| `/api/v1/items`             | `POST` | `ItemCreate`      | `dict`                  | Create a new item.                              |
| `/api/v1/items/{item_id}`   | `PATCH`| `ItemUpdate`      | `dict`                  | Update an existing item.                        |
| `/api/v1/users`             | `GET`  | `PaginationParams`| `dict`                  | Retrieve a list of all users with pagination and optional filtering. |

## Schemas

See the `src/oal_agent/app/schemas/` directory for request/response schemas.
