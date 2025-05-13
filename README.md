# Pinecone API Design and Definition

This repository contains the public OpenAPI specifications for Pinecone RESTful APIs and the Protobuf definitions for interacting with gRPC services.
These files represent the Pinecone API services at specific points in time and are versioned according to the month and year they were released.

---

## Table of Contents

1. [Overview](#overview)
2. [What Are OpenAPI and Protobuf Files?](#what-are-openapi-and-protobuf-files)
3. [Code Generation Resources](#code-generation-resources)
4. [Versioned Specifications](#versioned-specifications)
5. [Service-Specific Breakdown](#service-specific-breakdown)

---

## Overview

[Pinecone APIs](https://docs.pinecone.io/reference/api/introduction) provide a way to interact programmatically with your Pinecone account. There are several core services that work with databases (indexes and vectors), inference, and assistant.

- **Database**: The [Database API](https://docs.pinecone.io/reference/api/introduction#database-api) can be used to manage index resources, and the records stored within these indexes. The database services include
  both REST and gRPC specifications. The relevant filenames will include "data", "control", "db_data", or "db_control" depending on the version.
- **Inference**: The [Inference API](https://docs.pinecone.io/guides/inference/understanding-inference) provides access to embedding and reranking models hosted on Pinecone's infrastructure. The inference
  services support REST.
- **Assistant**: The [Assistant API](https://docs.pinecone.io/guides/assistant/overview) facillitates uploading documents, asking questions, and receiving responses that reference your documents. The assistant services support REST.

Support for these services is dependent on which version of the Pinecone API you are working with. For example, inference is only available in version `2024-10` and later.
Read more about [Pinecone API versioning](https://docs.pinecone.io/reference/api/versioning).

---

## What Are OpenAPI and Protobuf Files?

### OpenAPI

OpenAPI is a standardized format for describing RESTful APIs. It provides:

- A human and machine-readable schema of endpoints, request/response payloads, and error codes.
- Tools for generating API documentation, client SDKs, and server stubs.

[OpenAPI Specification Documentation](https://swagger.io/specification/)

### Protobuf

Protocol Buffers (Protobuf) are Google's language-neutral, platform-neutral, extensible mechanism for serializing structured data. Protobuf files:

- Define message structures and service contracts.
- Enable strongly-typed, high-performance communication between clients and servers.

[Protocol Buffers Documentation](https://protobuf.dev/)

---

## Code Generation Resources

You can use the following tools to generate client code, server stubs, and documentation from the specification files in this repository:

### For OpenAPI

- **Swagger Codegen**: [Documentation](https://swagger.io/tools/swagger-codegen/)
- **OpenAPI Generator**: [Documentation](https://openapi-generator.tech/)

### For Protobuf

- **Protobuf Compiler (`protoc`)**: [Documentation](https://protobuf.dev/reference/protoc/)
- **gRPC Code Generators**:
  - Python: `grpcio-tools`
  - Go: `protoc-gen-go`
  - Java: `protoc-gen-grpc-java`

Refer to the tool documentation for usage instructions tailored to your preferred programming language.

---

## Versioned Specifications

Each subdirectory in this repository represents a specific version of the Pinecone API. New versions of the Pinecone API are released quarterly. You can find more about API versioning [here](https://docs.pinecone.io/reference/api/versioning).
Directories are named using the `YYYY-MM` format, corresponding to the year and month of the release.
The API resources corresponding to each version are inside of their respective directory, and will have the format `<resource_name>_<api_version>.<file_extension>`.

Example:

```
2025-04/
- admin_2025-04.oas.yaml
- assistant_control_2025-04.oas.yaml
- assistant_data_2025-04.oas.yaml
- assistant_evaluation_2025-04.oas.yaml
- db_control_2025-04.oas.yaml
- db_data_2025-04.oas.yaml
- db_data_2025-04.proto
- db_metrics_2025-04.oas.yaml
- inference_2025-04.oas.yaml
- oauth_2025-04.oas.yaml
```

- **OpenAPI Files**: Files with the extension `*.oas.yaml`.
- **Protobuf Definitions**: Files with the extension `*.proto`.

---

## Service-Specific Breakdown

The Pinecone API consists of multiple services. Below is a high-level breakdown of some of these services and the associated specification files, and documentation links. The defined services will change across time and versions. You can use the `X-Pinecone-API-Version` header to work with a [specific version](https://docs.pinecone.io/reference/api/versioning#specify-an-api-version).

| Service                | OpenAPI File                            | Protobuf File           | Documentation Link                                                                           |
| ---------------------- | --------------------------------------- | ----------------------- | -------------------------------------------------------------------------------------------- |
| Database - Control     | `db_control_2025-04.oas.yaml`           | N/A                     | [Database Documentation](https://docs.pinecone.io/reference/api/introduction#database-api)   |
| Database - Data        | `db_data_2025-04.oas.yaml`              | `db_data_2025-04.proto` | [Database Documentation](https://docs.pinecone.io/reference/api/introduction#database-api)   |
| Inference              | `inference_2025-04.oas.yaml`            | N/A                     | [Inference Documentation](https://docs.pinecone.io/reference/api/introduction#inference-api) |
| Assistant - Control    | `assistant_control_2025-04.oas.yaml`    | N/A                     | [Assistant Documentation](https://docs.pinecone.io/reference/api/introduction#assistant-api) |
| Assistant - Data       | `assistant_data_2025-04.oas.yaml`       | N/A                     | [Assistant Documentation](https://docs.pinecone.io/reference/api/introduction#assistant-api) |
| Assistant - Evaluation | `assistant_evaluation_2025-04.oas.yaml` | N/A                     | [Assistant Documentation](https://docs.pinecone.io/reference/api/introduction#assistant-api) |

You can find specific links and resources for each service in the [Pinecone API reference](https://docs.pinecone.io/reference/api/introduction). Note: The names of the files may differ across versions.

---
