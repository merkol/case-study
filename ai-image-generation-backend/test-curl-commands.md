# AI Image Generation API - Test Commands

## Prerequisites
Make sure Firebase emulators are running:
```bash
firebase emulators:start --only functions,firestore
```

## Basic Flow Tests

### 1. Check User Credits (non-existent user)
```bash
curl -X GET "http://localhost:5001/case-study-feraset/us-central1/getUserCredits?userId=testuser1"
```

### 2. Create Generation Request (512x512 - 1 credit)
```bash
curl -X POST "http://localhost:5001/case-study-feraset/us-central1/createGenerationRequest" \
  -H "Content-Type: application/json" \
  -d '{
    "userId": "testuser1",
    "model": "Model A",
    "style": "realistic",
    "color": "vibrant",
    "size": "512x512",
    "prompt": "A beautiful sunset over mountains"
  }'
```

### 3. Check User Credits After Generation
```bash
curl -X GET "http://localhost:5001/case-study-feraset/us-central1/getUserCredits?userId=testuser1"
```

## More Generation Tests

### 4. High-Cost Generation (1024x1024 - 4 credits)
```bash
curl -X POST "http://localhost:5001/case-study-feraset/us-central1/createGenerationRequest" \
  -H "Content-Type: application/json" \
  -d '{
    "userId": "testuser1",
    "model": "Model B",
    "style": "artistic",
    "color": "monochrome",
    "size": "1024x1024",
    "prompt": "A mystical forest with ancient trees"
  }'
```

### 5. Low-Cost Generation (256x256 - 1 credit)
```bash
curl -X POST "http://localhost:5001/case-study-feraset/us-central1/createGenerationRequest" \
  -H "Content-Type: application/json" \
  -d '{
    "userId": "testuser1",
    "model": "Model C",
    "style": "cartoon",
    "color": "colorful",
    "size": "256x256",
    "prompt": "A cute robot playing in a garden"
  }'
```

## Error Testing

### 6. Insufficient Credits Test
```bash
curl -X POST "http://localhost:5001/case-study-feraset/us-central1/createGenerationRequest" \
  -H "Content-Type: application/json" \
  -d '{
    "userId": "testuser1",
    "model": "Model A",
    "style": "realistic",
    "color": "vibrant",
    "size": "1024x1024",
    "prompt": "This should fail due to insufficient credits"
  }'
```

### 7. Invalid Model Test
```bash
curl -X POST "http://localhost:5001/case-study-feraset/us-central1/createGenerationRequest" \
  -H "Content-Type: application/json" \
  -d '{
    "userId": "testuser1",
    "model": "Invalid Model",
    "style": "realistic",
    "color": "vibrant",
    "size": "512x512",
    "prompt": "This should fail due to invalid model"
  }'
```

### 8. Invalid Size Test
```bash
curl -X POST "http://localhost:5001/case-study-feraset/us-central1/createGenerationRequest" \
  -H "Content-Type: application/json" \
  -d '{
    "userId": "testuser1",
    "model": "Model A",
    "style": "realistic",
    "color": "vibrant",
    "size": "999x999",
    "prompt": "This should fail due to invalid size"
  }'
```

### 9. Missing Fields Test
```bash
curl -X POST "http://localhost:5001/case-study-feraset/us-central1/createGenerationRequest" \
  -H "Content-Type: application/json" \
  -d '{
    "userId": "testuser1",
    "model": "Model A",
    "style": "realistic",
    "color": "vibrant"
  }'
```

## Multi-User Tests

### 10. Test Different User
```bash
curl -X POST "http://localhost:5001/case-study-feraset/us-central1/createGenerationRequest" \
  -H "Content-Type: application/json" \
  -d '{
    "userId": "testuser2",
    "model": "Model A",
    "style": "realistic",
    "color": "vibrant",
    "size": "512x512",
    "prompt": "A different users generation request"
  }'
```

### 11. Check Second User Credits
```bash
curl -X GET "http://localhost:5001/case-study-feraset/us-central1/getUserCredits?userId=testuser2"
```

## Edge Case Tests

### 12. Missing userId Parameter
```bash
curl -X GET "http://localhost:5001/case-study-feraset/us-central1/getUserCredits"
```

### 13. Wrong HTTP Method
```bash
curl -X PUT "http://localhost:5001/case-study-feraset/us-central1/createGenerationRequest" \
  -H "Content-Type: application/json" \
  -d '{"test": "data"}'
```

## Quick Test Sequence

For a quick validation, run these commands in order:
1. Command #1 (check non-existent user)
2. Command #2 (create generation)
3. Command #3 (check credits after generation)

## Expected Responses

**Successful Generation:**
```json
{
  "generationRequestId": "abc123",
  "deductedCredits": 1,
  "imageUrl": "https://placeholder-model-a.com/image_abc123_timestamp.jpg"
}
```

**User Credits:**
```json
{
  "currentCredits": 49,
  "transactions": [
    {
      "id": "trans123",
      "type": "deduction",
      "credits": 1,
      "generationRequestId": "abc123",
      "timestamp": "2025-07-25T12:53:11.135Z"
    }
  ]
}
```

**Insufficient Credits:**
```json
{
  "error": "Insufficient credits",
  "required": 4,
  "available": 1
}
```

## Valid Values

**Models:** `Model A`, `Model B`, `Model C`
**Styles:** `realistic`, `artistic`, `cartoon`
**Colors:** `vibrant`, `monochrome`, `colorful`
**Sizes:** `256x256` (1 credit), `512x512` (1 credit), `1024x1024` (4 credits)

## Monitoring

Check logs in real-time:
```bash
tail -f firebase-debug.log
``` 