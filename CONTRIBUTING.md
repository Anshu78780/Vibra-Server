# Contributing to Music Backend API

First off, thank you for considering contributing to Music Backend API! It's people like you that make this project great.

## Code of Conduct

This project and everyone participating in it is governed by our Code of Conduct. By participating, you are expected to uphold this code.

## How Can I Contribute?

### Reporting Bugs

Before creating bug reports, please check the issue list as you might find out that you don't need to create one. When you are creating a bug report, please include as many details as possible:

- **Use a clear and descriptive title**
- **Describe the exact steps to reproduce the problem**
- **Provide specific examples to demonstrate the steps**
- **Describe the behavior you observed after following the steps**
- **Explain which behavior you expected to see instead and why**
- **Include details about your configuration and environment**

### Suggesting Enhancements

Enhancement suggestions are tracked as GitHub issues. When creating an enhancement suggestion, please include:

- **Use a clear and descriptive title**
- **Provide a step-by-step description of the suggested enhancement**
- **Provide specific examples to demonstrate the steps**
- **Describe the current behavior and explain which behavior you expected to see instead**
- **Explain why this enhancement would be useful**

### Pull Requests

1. Fork the repo and create your branch from `main`
2. If you've added code that should be tested, add tests
3. If you've changed APIs, update the documentation
4. Ensure the test suite passes
5. Make sure your code follows the existing style
6. Issue that pull request!

## Development Setup

### Prerequisites
- Python 3.8+
- pip
- Git

### Setup Steps

1. **Fork and clone the repository**
   ```bash
   git clone https://github.com/yourusername/Vibra-Server.git
   cd Vibra-Server
   ```

2. **Create a virtual environment**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Create environment file**
   ```bash
   cp .env.example .env  # Edit with your settings
   ```

5. **Run the application**
   ```bash
   python app.py
   ```

## Development Guidelines

### Code Style

- Follow PEP 8 Python style guidelines
- Use meaningful variable and function names
- Add docstrings to all functions and classes
- Keep functions small and focused
- Use type hints where appropriate

### Example:
```python
def search_songs(self, query: str, max_results: int = 10) -> List[Dict]:
    """
    Search for songs using the specified query.
    
    Args:
        query: Search term for songs
        max_results: Maximum number of results to return
        
    Returns:
        List of song dictionaries with metadata
        
    Raises:
        ValueError: If query is empty or invalid
    """
    if not query.strip():
        raise ValueError("Query cannot be empty")
    
    # Implementation here...
```

### Error Handling

- Always include proper error handling
- Log errors with appropriate levels
- Return meaningful error messages to users
- Use try-except blocks appropriately

### Testing

- Write tests for new features
- Ensure existing tests pass
- Test edge cases and error conditions
- Use meaningful test names

### Documentation

- Update README.md if you change functionality
- Add docstrings to new functions
- Update API documentation for new endpoints
- Include examples in documentation

## Project Structure

```
Vibra-Server/
├── app.py                 # Main Flask application
├── config.py             # Configuration settings  
├── music_extractor.py    # Core music extraction logic
├── requirements.txt      # Python dependencies
├── tests/                # Test files
│   ├── test_charts.py
│   └── test_trending.py
├── docs/                 # Additional documentation
└── README.md            # Main documentation
```

## API Design Guidelines

### Endpoint Naming
- Use nouns, not verbs
- Use plural nouns for collections
- Be consistent with naming conventions
- Use kebab-case for multi-word endpoints

### Response Format
All API responses should follow this format:

```json
{
  "success": true,
  "data": {...},
  "message": "Optional message",
  "error": null
}
```

For errors:
```json
{
  "success": false,
  "data": null,
  "message": "Error description",
  "error": "ERROR_CODE"
}
```

### HTTP Status Codes
- 200: Success
- 201: Created
- 400: Bad Request
- 404: Not Found
- 429: Rate Limited
- 500: Internal Server Error

## Commit Message Guidelines

Use the conventional commits format:

```
<type>(<scope>): <subject>

<body>

<footer>
```

### Types:
- **feat**: A new feature
- **fix**: A bug fix
- **docs**: Documentation only changes
- **style**: Changes that do not affect the meaning of the code
- **refactor**: A code change that neither fixes a bug nor adds a feature
- **perf**: A code change that improves performance
- **test**: Adding missing tests or correcting existing tests
- **chore**: Changes to the build process or auxiliary tools

### Examples:
```
feat(api): add playlist creation endpoint

Add new POST /playlist endpoint that allows users to create
custom playlists with song collections.

Closes #123
```

```
fix(extractor): handle YouTube rate limiting

Implement exponential backoff retry logic when YouTube
returns 429 status codes.

Fixes #456
```

## Testing

### Running Tests
```bash
# Run all tests
python -m pytest

# Run specific test file
python -m pytest tests/test_charts.py

# Run with coverage
python -m pytest --cov=. --cov-report=html
```

### Writing Tests
- Use descriptive test names
- Test both success and failure cases
- Mock external API calls
- Test edge cases

```python
def test_search_songs_with_valid_query():
    """Test that search returns results for valid query."""
    extractor = MusicExtractor()
    results = extractor.search_songs("imagine dragons", 5)
    
    assert len(results) > 0
    assert all('id' in song for song in results)
    assert all('title' in song for song in results)

def test_search_songs_with_empty_query():
    """Test that search raises error for empty query."""
    extractor = MusicExtractor()
    
    with pytest.raises(ValueError):
        extractor.search_songs("", 5)
```

## Performance Guidelines

- Cache frequently requested data
- Use appropriate data structures
- Minimize API calls to external services
- Implement proper pagination
- Add request timeouts

## Security Guidelines

- Validate all input data
- Sanitize user-provided content
- Use HTTPS in production
- Implement rate limiting
- Log security-related events

## Release Process

1. Update version in `app.py`
2. Update CHANGELOG.md
3. Create release branch
4. Test thoroughly
5. Merge to main
6. Tag the release
7. Deploy to production

## Questions?

Don't hesitate to ask questions! You can:

- Create an issue for bugs or feature requests
- Start a discussion for questions
- Reach out to maintainers directly

## Recognition

Contributors will be recognized in:
- README.md contributors section
- Release notes
- Project documentation

Thank you for your contributions! 🎉
