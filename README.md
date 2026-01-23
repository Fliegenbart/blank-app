# Turn-on Brand Engine

A web service for extracting brand identity (Brand DNA) from documents and generating on-brand content.

## Features

- **Document Analysis**: Upload PDF/PPTX files and extract brand identity
  - Color palette extraction (primary, secondary, neutrals)
  - Typography analysis (heading/body fonts, scale)
  - Layout system detection (margins, grid)
  - Tone of voice analysis
  - Imagery style detection

- **Content Generation**: Generate on-brand outputs
  - Website (HTML + CSS with design tokens)
  - Newsletter (HTML email + MJML source)

- **Multi-Brand & Team Support**
  - Organizations → Brands → Members
  - RBAC: Owner, Editor, Viewer roles

- **Versioned Brand Profiles**
  - Each analysis creates a new version
  - JSON profile + Markdown summary

## Tech Stack

- **Backend**: Python 3.11, FastAPI
- **Frontend**: Next.js 14, React 18, Tailwind CSS, shadcn/ui
- **Database**: PostgreSQL
- **Queue**: Redis + RQ
- **Storage**: MinIO (S3-compatible)
- **Parsing**: python-pptx, pdfplumber, poppler-utils

## Quick Start

### 1. Clone and Setup

```bash
git clone <repo-url>
cd brand-engine

# Copy environment file
cp .env.example .env
```

### 2. Start Services

```bash
cd infra
docker compose up -d
```

This starts:
- **Web UI** on http://localhost:3000
- **API** on http://localhost:8000
- Worker (RQ)
- PostgreSQL on port 5432
- Redis on port 6379
- MinIO on http://localhost:9000 (console: http://localhost:9001)

### 3. Run Migrations

```bash
# Enter the API container
docker compose exec api bash

# Run migrations
alembic upgrade head
```

### 4. Generate Sample Files (Optional)

```bash
cd samples
pip install -r requirements.txt
python generate_samples.py
```

## Web UI

The web frontend is a Next.js 14 application with a modern UI built using shadcn/ui components.

### Features

- **Authentication**: Login and registration with JWT
- **Brand Management**: Create and manage multiple brands
- **Document Uploads**: Drag-and-drop file uploads with progress tracking
- **Job Tracking**: Real-time job status with progress stepper
- **Profile Viewer**: Browse brand profiles with tabs for Summary, Tokens, Imagery, Tone, and Evidence
- **Content Generation**: Generate websites and newsletters with customizable options
- **Team Management**: Invite members with role-based access (Owner, Editor, Viewer)

### Running the Web UI (Development)

```bash
cd apps/web
npm install
npm run dev
```

The development server starts at http://localhost:3000

### Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `NEXT_PUBLIC_API_URL` | Backend API URL | `http://localhost:8000` |

### Pages

| Route | Description |
|-------|-------------|
| `/login` | User login |
| `/register` | User registration |
| `/brands` | Brands list and creation |
| `/brands/[brandId]/overview` | Brand dashboard |
| `/brands/[brandId]/uploads` | Document uploads |
| `/brands/[brandId]/profiles` | Profile versions list |
| `/brands/[brandId]/profiles/[version]` | Profile viewer |
| `/brands/[brandId]/generate` | Content generation hub |
| `/brands/[brandId]/generate/website` | Website generator |
| `/brands/[brandId]/generate/newsletter` | Newsletter generator |
| `/brands/[brandId]/outputs` | Generated outputs |
| `/brands/[brandId]/team` | Team management |
| `/jobs/[jobId]` | Job detail and progress |

## API Documentation

Once running, visit:
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

## Example curl Commands

### Register User

```bash
curl -X POST http://localhost:8000/api/v1/auth/register \
  -H "Content-Type: application/json" \
  -d '{
    "email": "user@example.com",
    "password": "securepassword123",
    "full_name": "John Doe"
  }'
```

### Login

```bash
curl -X POST http://localhost:8000/api/v1/auth/login \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "username=user@example.com&password=securepassword123"
```

Save the `access_token` from the response.

### Create Brand

```bash
export TOKEN="your_access_token_here"

curl -X POST http://localhost:8000/api/v1/brands \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Acme Corp",
    "slug": "acme-corp",
    "description": "Our main brand"
  }'
```

### Upload Document

```bash
export BRAND_ID="your_brand_id_here"

curl -X POST "http://localhost:8000/api/v1/brands/$BRAND_ID/uploads" \
  -H "Authorization: Bearer $TOKEN" \
  -F "file=@samples/sample.pptx"
```

### Analyze Upload

```bash
export UPLOAD_ID="your_upload_id_here"

curl -X POST "http://localhost:8000/api/v1/brands/$BRAND_ID/analyze?upload_id=$UPLOAD_ID" \
  -H "Authorization: Bearer $TOKEN"
```

### Check Job Status

```bash
export JOB_ID="your_job_id_here"

curl "http://localhost:8000/api/v1/jobs/$JOB_ID" \
  -H "Authorization: Bearer $TOKEN"
```

### Get Brand Profile

```bash
# Get latest profile
curl "http://localhost:8000/api/v1/brands/$BRAND_ID/profiles/latest" \
  -H "Authorization: Bearer $TOKEN"

# Get specific version
curl "http://localhost:8000/api/v1/brands/$BRAND_ID/profiles/1" \
  -H "Authorization: Bearer $TOKEN"
```

### Generate Website

```bash
curl -X POST "http://localhost:8000/api/v1/brands/$BRAND_ID/generate/website" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "topic": "Product Launch",
    "pages": [
      {"slug": "index", "title": "Home", "sections": ["hero", "features", "cta"]},
      {"slug": "about", "title": "About Us", "sections": ["hero", "features"]}
    ],
    "brief": "Landing page for our new product"
  }'
```

### Generate Newsletter

```bash
curl -X POST "http://localhost:8000/api/v1/brands/$BRAND_ID/generate/newsletter" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "topic": "Summer Sale",
    "offer": "50% off all products",
    "cta": "Shop Now"
  }'
```

### Download Output

```bash
export OUTPUT_ID="your_output_id_here"

curl -L "http://localhost:8000/api/v1/outputs/$OUTPUT_ID/download" \
  -H "Authorization: Bearer $TOKEN" \
  -o output.zip
```

## Project Structure

```
brand-engine/
├── apps/
│   ├── api/                 # FastAPI application
│   │   ├── app/
│   │   │   ├── api/v1/      # API endpoints
│   │   │   ├── core/        # Config, security, database
│   │   │   ├── models/      # SQLAlchemy models
│   │   │   ├── schemas/     # Pydantic schemas
│   │   │   └── services/    # Business logic
│   │   └── migrations/      # Alembic migrations
│   ├── web/                 # Next.js 14 frontend
│   │   ├── app/             # App Router pages
│   │   ├── components/      # React components
│   │   │   ├── ui/          # shadcn/ui components
│   │   │   ├── brand/       # Brand-specific components
│   │   │   ├── job/         # Job-related components
│   │   │   ├── layout/      # Layout components
│   │   │   └── profile/     # Profile viewer components
│   │   ├── hooks/           # Custom React hooks
│   │   ├── lib/             # Utilities and API client
│   │   └── types/           # TypeScript types
│   └── worker/              # RQ worker
│       └── app/
│           ├── analyzers/   # Brand analysis
│           ├── generators/  # Content generation
│           ├── parsers/     # Document parsing
│           ├── providers/   # LLM/Vision providers
│           └── tasks/       # RQ tasks
├── infra/
│   └── docker-compose.yml
├── samples/                 # Sample files
├── tests/                   # Test suite
├── .env.example
└── README.md
```

## Storage

Outputs are stored in MinIO under these paths:

- Uploads: `uploads/{brand_id}/{upload_id}/{filename}`
- Debug artifacts: `debug/{job_id}/...`
- Generated outputs: `outputs/{brand_id}/{output_id}/{filename}`
- Profile assets: `profiles/{brand_id}/v{version}/...`

Access MinIO console at http://localhost:9001 (default: minioadmin/minioadmin123)

## Configuration

Key environment variables (see `.env.example`):

| Variable | Description | Default |
|----------|-------------|---------|
| `DATABASE_URL` | PostgreSQL connection | `postgresql://...` |
| `REDIS_URL` | Redis connection | `redis://localhost:6379/0` |
| `MINIO_ENDPOINT` | MinIO endpoint | `localhost:9000` |
| `MINIO_ACCESS_KEY` | MinIO access key | `minioadmin` |
| `MINIO_SECRET_KEY` | MinIO secret key | `minioadmin123` |
| `SECRET_KEY` | JWT signing key | Change in production! |
| `OPENAI_API_KEY` | Optional: OpenAI for advanced analysis | (empty = mock provider) |
| `MAX_UPLOAD_SIZE_MB` | Max upload size | `100` |
| `NEXT_PUBLIC_API_URL` | API URL for web frontend | `http://localhost:8000` |

## AI Providers

By default, the system uses mock providers for tone and imagery analysis.
To enable OpenAI-powered analysis:

```bash
export OPENAI_API_KEY="your-api-key"
```

The system will automatically use OpenAI for more accurate tone analysis.

## Testing

Run tests with pytest:

```bash
# Install test dependencies
pip install pytest pytest-asyncio httpx

# Run all tests
pytest tests/ -v

# Run specific tests
pytest tests/test_api.py::TestAuth -v
```

## Development

### Running Locally (without Docker)

```bash
# Install dependencies
cd apps/api
pip install -r requirements.txt

# Set environment variables
export DATABASE_URL="postgresql://..."
export REDIS_URL="redis://..."

# Run API
uvicorn app.main:app --reload

# In another terminal, run worker
cd apps/worker
pip install -r requirements.txt
rq worker high default low
```

### Adding New Analyzers

1. Create analyzer in `apps/worker/app/analyzers/`
2. Implement the analysis logic
3. Register in `BrandAnalyzer.analyze()`
4. Update `BrandProfileSchema` if needed

### Adding New Providers

1. Create provider in `apps/worker/app/providers/`
2. Implement the provider interface
3. Add environment variable for API key
4. Update `get_*_provider()` to use new provider

## API Endpoints Summary

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/v1/auth/register` | Register new user |
| POST | `/api/v1/auth/login` | Login and get token |
| GET | `/api/v1/users/me` | Get current user |
| GET/POST | `/api/v1/brands` | List/Create brands |
| GET/PUT/DELETE | `/api/v1/brands/{id}` | Brand CRUD |
| POST | `/api/v1/brands/{id}/members` | Add member to brand |
| POST | `/api/v1/brands/{id}/uploads` | Upload document |
| POST | `/api/v1/brands/{id}/analyze` | Start analysis job |
| GET | `/api/v1/brands/{id}/profiles` | List profile versions |
| GET | `/api/v1/brands/{id}/profiles/{v}` | Get profile version |
| POST | `/api/v1/brands/{id}/generate/website` | Generate website |
| POST | `/api/v1/brands/{id}/generate/newsletter` | Generate newsletter |
| GET | `/api/v1/jobs/{id}` | Get job status |
| GET | `/api/v1/outputs/{id}/download` | Download output |

## License

Proprietary - All rights reserved.
