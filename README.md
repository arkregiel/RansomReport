# Ransomware group reporting tool

Simple Python tool to create reports about ransomware groups. It fetches the data from ransomware.live and MalwareBazaar API.

## API Keys

Obtain ransomware.live [API PRO key](https://www.ransomware.live/api) and MalwareBazaar [auth key](https://bazaar.abuse.ch/api/).

Create `.env` file in repo's root directory looking like this:

```
ABUSECH_AUTH_KEY=<MalwareBazaar auth key>
RANSOMWARELIVE_API_TOKEN=<ransomware.live API PRO key>
```

## Usage example

```
uv sync
uv run ransomreport -g qilin > Qilin.md
```
