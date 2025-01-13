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

The [Pinecone APIs](https://docs.pinecone.io/reference/api/introduction) allow you to interact programmatically with your Pinecone account. There are several core services which allow you to work with
databases (indexes and vectors), inference, and assistant.

- **Database**: The [database API](https://docs.pinecone.io/reference/api/introduction#database-api) allows managing index resources, and the records stored within these indexes. The database APIs include
  both REST and gRPC specifications. The relevant filenames will include "data", "control", "db_data", or "db_control" depending on the version.
- **Inference**: The [inference API](https://docs.pinecone.io/guides/inference/understanding-inference) gives you access to embedding and reranking models hosted on Pinecone's infrastructure. The inference
  service supports REST.
- **Assistant**: The [assistant API](https://docs.pinecone.io/guides/get-started/assistant-quickstart) is a service that allows you to upload documents, ask questions, and receive responses
  that reference your documents.

Support for these services is dependent on which version of the Pinecone API you are working with. For example, inference is only available in version `2024-10` and later.
Read more about [Pinecone API versioning](https://docs.pinecone.io/reference/api/versioning#get-updates).

---

## What Are OpenAPI and Protobuf Files?

### OpenAPI

OpenAPI is a standardized format for describing RESTful APIs. It provides:

- A human and machine-readable schema of endpoints, request/response payloads, and error codes.
- Tools for generating API documentation, client SDKs, and server stubs.

### Protobuf

Protocol Buffers (Protobuf) are Google's language-neutral, platform-neutral, extensible mechanism for serializing structured data. Protobuf files:

- Define message structures and service contracts.
- Enable strongly-typed, high-performance communication between clients and servers.

For more details, see [OpenAPI Specification Documentation](https://swagger.io/specification/) and [Protocol Buffers Documentation](https://protobuf.dev/).

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

Each subdirectory in this repository represents a specific version of the Pinecone API. New versions of the Pinecone API are released quarterly.
You can find more about API versioning [here](https://docs.pinecone.io/reference/api/versioning#get-updates). Directories are named using the `YYYY-MM` format, corresponding to the year and month of the release.

Example:

```
2024-04/
  - db_control_2024-10.oas.yaml
  - db_data_2024-10.oas.yaml
  - db_data_2024-10.proto
  - inference_2024-10.oas.yaml
```

- **OpenAPI Files**: Files with the extension: `*.oas.yaml`.
- **Protobuf Definitions**: Files with the extension: `*.proto`.

---

## Service-Specific Breakdown

The Pinecone API consists of multiple services. Below is a high-level breakdown of the services and the associated specification files:

| Service                | OpenAPI File                                  | Protobuf File                 | Documentation Link                                                                           |
| ---------------------- | --------------------------------------------- | ----------------------------- | -------------------------------------------------------------------------------------------- |
| Database - Control     | `db_control_<API_VERSION>.oas.yaml`           | N/A                           | [Database Documentation](https://docs.pinecone.io/reference/api/introduction#database-api)   |
| Database - Data        | `db_data_<API_VERSION>.oas.yaml`              | `db_data_<API_VERSION>.proto` | [Database Documentation](https://docs.pinecone.io/reference/api/introduction#database-api)   |
| Inference              | `inference_<API_VERSION>.oas.yaml`            | N/A                           | [Inference Documentation](https://docs.pinecone.io/reference/api/introduction#inference-api) |
| Assistant - Control    | `assistant_control_<API_VERSION>.oas.yaml`    | N/A                           | [Assistant Documentation](https://docs.pinecone.io/reference/api/introduction#assistant-api) |
| Assistant - Data       | `assistant_data_<API_VERSION>.oas.yaml`       | N/A                           | [Assistant Documentation](https://docs.pinecone.io/reference/api/introduction#assistant-api) |
| Assistant - Evaluation | `assistant_evaluation_<API_VERSION>.oas.yaml` | N/A                           | [Assistant Documentation](https://docs.pinecone.io/reference/api/introduction#assistant-api) |

You can find specific links and resources for each service in the [Pinecone API reference](https://docs.pinecone.io/reference/api/introduction). Note: The names of the files may differ across versions.

---
