# Backend Data Fetchers

This directory contains modules responsible for fetching data from external, third-party APIs (e.g., EODHD, AlphaVantage, etc.).

## Structure

- Each subdirectory is dedicated to a specific data provider.
- Modules within a provider's directory correspond to specific API endpoints or data types (e.g., `eodhd_fundamentals.py`, `eodhd_news.py`).
- Fetchers are responsible for making the HTTP request and returning the raw or lightly processed data.
- Data mapping and transformation into the application's internal models should be handled by the `mappers` service, not here. 