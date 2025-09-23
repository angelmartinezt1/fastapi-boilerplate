# Deployment Scripts

This directory contains deployment-related scripts for production setup.

## Database Setup

### Create MongoDB Indexes

Before deploying to production, you **must** create the required MongoDB indexes:

```bash
# Run the index creation script
python deployment/create_indexes.py
```

This script will create all necessary indexes for optimal performance:

- **seller_email_unique**: Compound unique index on `seller_id` + `email`
- **seller_id_idx**: Index for basic seller queries
- **email_idx**: Index for email lookups
- **seller_active_created_idx**: Compound index for listing/filtering
- **search_text_idx**: Full-text search index

### Environment Variables Required

Make sure these environment variables are set:

```bash
MONGODB_URL=mongodb+srv://user:password@cluster.mongodb.net/database
```

### Deployment Checklist

1. ✅ Set environment variables
2. ✅ Run `python deployment/create_indexes.py`
3. ✅ Deploy application code
4. ✅ Test endpoints

### Performance Benefits

By pre-creating indexes:
- **Lambda cold start**: ~135ms faster (no index creation overhead)
- **Query performance**: 10-100x faster depending on collection size
- **Resource usage**: Lower CPU and memory consumption

### Re-running the Script

The script is idempotent - you can run it multiple times safely:
- Existing indexes will be skipped
- Only missing indexes will be created
- No data loss or downtime