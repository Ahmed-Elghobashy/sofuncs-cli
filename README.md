# sofuncs

Simple Python tool to list exported native functions from a Linux shared object (.so).

## Usage

```bash
python -m sofuncs /path/to/libexample.so
```

Or install and run:

```bash
sofuncs /path/to/libexample.so
```

## Notes

- Requires Linux and a shared object built for ELF.
- Uses `nm` when available, otherwise falls back to `readelf`.
