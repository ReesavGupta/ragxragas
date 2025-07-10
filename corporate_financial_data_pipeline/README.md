# Corporate Financial Data RAG Pipeline

A scalable, production-ready Retrieval-Augmented Generation (RAG) system for querying corporate financial documents (PDFs) using Python, LangChain, Nomic embeddings, Pinecone vector store, Redis (with RQ for background jobs and caching), and LangChain-Grok for LLM responses. Includes a Streamlit UI for user interaction.

## Initial Setup

1. **Clone the repository**
2. **Navigate to the project directory:**
   ```bash
   cd corporate_financial_data_pipeline
   ```
3. **Create a virtual environment:**
   ```bash
   python -m venv .venv
   ```
4. **Activate the virtual environment:**
   - On Windows:
     ```bash
     .venv\Scripts\activate
     ```
   - On macOS/Linux:
     ```bash
     source .venv/bin/activate
     ```
5. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

6. **Set up environment variables:**
   - Create a `.env` file with your API keys and configuration (see PRD.md for required variables).

---

For more details, see the PRD.md file.

## RQ Worker Setup (Background Ingestion)

This project uses **Redis Queue (RQ)** for background document ingestion jobs.

### Enqueue an Ingestion Job

Run the following command to enqueue a job that will process all PDFs in the `data/` directory:

```bash
python src/ingest_worker.py
```

### Start an RQ Worker

In a separate terminal, start an RQ worker to process jobs from the `ingest` queue:

```bash
rq worker ingest
```

- Make sure your Redis server is running and accessible at the `REDIS_URL` specified in your `.env` file.
- You can run multiple workers for higher throughput.

---

For more advanced usage, see the code in `src/ingest_worker.py`.

## Prometheus Monitoring

This project exposes a `/metrics` endpoint for Prometheus scraping.

### Sample Prometheus Config

Add this to your `prometheus.yml` scrape_configs:

```yaml
scrape_configs:
  - job_name: 'rag-fastapi'
    static_configs:
      - targets: ['localhost:8000']  # Change port if needed
    metrics_path: /metrics
```

- Make sure your FastAPI app is running on the specified port (default: 8000).
- Start Prometheus with this config, and you’ll see metrics from your RAG API.

---

You can now build Grafana dashboards or set up alerts based on these metrics!

## Grafana Dashboard Setup

You can use **Grafana** to visualize your RAG system’s metrics in real time.

### 1. Add Prometheus as a Data Source
- Open Grafana (usually at http://localhost:3000)
- Go to **Configuration > Data Sources**
- Click **Add data source** and select **Prometheus**
- Set the URL to your Prometheus server (e.g., `http://localhost:9090`)
- Click **Save & Test**

### 2. Create a Dashboard
- Click **+ > Dashboard > Add new panel**
- Choose **Prometheus** as the data source

#### Example Panels and Queries

| Metric Name        | Prometheus Query                                                                 | Panel Type      | Description                 |
|--------------------|---------------------------------------------------------------------------------|-----------------|-----------------------------|
| Total Requests     | `sum(rag_requests_total)`                                                        | Stat/TimeSeries | Total API requests          |
| Request Latency    | `histogram_quantile(0.95, sum(rate(rag_request_latency_seconds_bucket[5m])) by (le))` | TimeSeries      | 95th percentile latency     |
| Cache Hit Rate     | `sum(rag_cache_hits_total) / (sum(rag_cache_hits_total) + sum(rag_cache_misses_total))` | Gauge           | Cache hit ratio             |
| Errors per Minute  | `rate(rag_errors_total[1m])`                                                     | TimeSeries      | Error rate                  |
| Cache Misses       | `sum(rag_cache_misses_total)`                                                    | Stat            | Total cache misses          |

---

You can set up alerts in Grafana for high error rates, latency, or low cache hit ratio.

## Load Testing with k6

You can use [k6](https://k6.io/) to load test the `/query` endpoint.

### 1. Install k6
- Download from [https://k6.io/](https://k6.io/) or install via Homebrew, Chocolatey, or Docker.

### 2. Edit the Test Script
- Open `k6_load_test.js` and set your valid API key in the `API_KEY` variable.

### 3. Run the Test

```bash
k6 run k6_load_test.js
```

- This will simulate 200 concurrent users for 10 minutes, measuring response time and error rate.
- k6 will output response time percentiles, error rates, and throughput.
- You can also parse the `cached` field in responses to estimate cache hit ratio.

---

For more advanced scenarios, see the [k6 documentation](https://k6.io/docs/). 