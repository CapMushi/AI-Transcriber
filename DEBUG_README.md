# Debug Scripts for Content Comparison

This directory contains comprehensive debugging scripts to help identify why certain chunks are being missed in the content comparison process.

## Scripts Overview

### 1. `debug_comparison.py` - Main Debug Script
**Purpose**: Replicates the complete original workflow with detailed logging to identify missed chunks.

**Features**:
- ✅ **Complete workflow replication** - Uses all original methods and components
- ✅ **Comprehensive logging** - Logs every step to `comparison_debug.log`
- ✅ **File validation** - Validates both primary and secondary files
- ✅ **Audio preparation** - Uses original audio processing pipeline
- ✅ **Transcription** - Uses original Whisper transcriber
- ✅ **Vector storage** - Uses original Pinecone storage with embeddings
- ✅ **Content comparison** - Uses original search algorithms
- ✅ **Gap analysis** - Identifies and analyzes missing regions
- ✅ **Detailed reporting** - Provides complete session summary

### 2. `analyze_chunks.py` - Advanced Analysis Script
**Purpose**: Provides deeper insights into chunking and matching processes.

**Features**:
- 📊 **Chunking analysis** - Detailed statistics on segments and chunks
- 🔍 **Embedding similarity** - Tests different similarity thresholds
- 📈 **Missing content analysis** - Identifies why specific regions are missed
- 📋 **Segment statistics** - Length, duration, and confidence analysis
- 🎯 **Threshold testing** - Tests multiple similarity thresholds (0.5 to 0.95)

## Usage

### Running the Main Debug Script

```bash
# Basic usage
python debug_comparison.py primary_file.mp4 secondary_file.mp4

# Example with your files
python debug_comparison.py "testing files/primary.mp4" "testing files/secondary.mp4"
```

**Output**: 
- Console output with progress updates
- Detailed log file: `comparison_debug.log`

### Running the Advanced Analysis Script

```bash
# Basic usage
python analyze_chunks.py primary_file.mp4 secondary_file.mp4

# Example with your files
python analyze_chunks.py "testing files/primary.mp4" "testing files/secondary.mp4"
```

**Output**: 
- Console output with detailed analysis
- No separate log file (all output to console)

## What the Scripts Will Help You Identify

### 1. **Chunking Issues**
- How segments are being split into chunks
- Whether chunks are too large or too small
- If chunking is missing certain segments
- Chunk overlap and boundary issues

### 2. **Embedding Issues**
- Whether embeddings are being generated correctly
- Similarity threshold problems
- Vector search performance issues
- Pinecone indexing problems

### 3. **Missing Content Analysis**
- **Gap identification**: Exact timestamps of missing regions
- **Content analysis**: What text is in the missing regions
- **Segment analysis**: Length, confidence, and quality of missing segments
- **Pattern identification**: Common characteristics of missed content

### 4. **Workflow Issues**
- File validation problems
- Audio preparation failures
- Transcription errors
- Storage/retrieval issues

## Expected Output Analysis

### From `debug_comparison.py`:

```
==========================================================
COMPARISON DEBUG SESSION STARTED
==========================================================
Timestamp: 2024-01-15 10:30:00
Config: {'segment_based': True, 'max_segment_length': 500, ...}

==========================================================
FILE INFO: PRIMARY
==========================================================
File path: primary.mp4
File exists: True
File size: 12345678 bytes
File extension: .mp4
File validation: PASS
File info: {"duration": 600.5, "format": "mp4", ...}

==========================================================
AUDIO PREPARATION: PRIMARY
==========================================================
Preparing audio for: primary.mp4
Audio prepared successfully: /tmp/audio_123.wav
Prepared audio size: 9876543 bytes

==========================================================
TRANSCRIPTION: PRIMARY
==========================================================
Model: base
Language: auto
Audio path: /tmp/audio_123.wav
Transcription completed in 45.23 seconds
Success: True
Language detected: en
Confidence: 0.856
Text length: 15432 characters
Number of segments: 89

First 5 segments:
  Segment 1: 0.00s - 2.45s
    Text: 'Hello, this is the beginning of the video.'
  Segment 2: 2.45s - 5.12s
    Text: 'We will be discussing important topics today.'
  ...

==========================================================
STORING PRIMARY CONTENT
==========================================================
Clearing existing embeddings...
Clear embeddings result: True
Generated file ID: debug_1705312200
Storing transcription chunks...
Store chunks result: True
Chunks exist in database: True

==========================================================
CHUNKING SECONDARY TEXT
==========================================================
Chunking config: {"segment_based": true, "max_segment_length": 500, ...}
Generated 15 chunks

Chunk 1:
  Text: 'Hello, this is the beginning of the video.'
  Start time: 0.00s
  End time: 2.45s
  Segment index: 0
  Chunk type: segment
  Text length: 42 characters

...

==========================================================
SEARCHING FOR CONTENT MATCHES
==========================================================
Threshold: 0.7
Secondary text: 'Hello, this is the beginning of the video. We will be discussing...'
Search result: {"success": true, "matches": [...], "confidence": 0.823}

==========================================================
ANALYZING MISSING REGIONS
==========================================================
Found 3 gaps in matches

Gap 1: 501.20s - 502.50s (duration: 1.30s)
  Segments in gap: 2
  Total text in gap: 156 characters
  Gap text: 'This is some content that was missed during the comparison process.'
  Average segment length: 78.0 characters
  Short segments (<50 chars): 0
  Low confidence segments (<50%): 0

...

==========================================================
DEBUG SESSION SUMMARY
==========================================================
Primary file processed: primary.mp4
Secondary file processed: secondary.mp4
Primary text length: 15432 characters
Secondary text length: 8234 characters
Primary segments: 89
Secondary chunks: 15
Search threshold: 0.7
Matches found: 8
Search success: True
```

### From `analyze_chunks.py`:

```
============================================================
CHUNKING ANALYSIS: PRIMARY
============================================================
Total segments: 89

Segment 1: 0.00s - 2.45s (2.45s)
  Text: 'Hello, this is the beginning of the video.'
  Length: 42 chars

...

Text length statistics:
  Average: 173.4 chars
  Min: 12 chars
  Max: 456 chars

Duration statistics:
  Average: 6.78s
  Min: 0.85s
  Max: 15.23s

Chunking with config: {"segment_based": true, "max_segment_length": 500, ...}
Generated 23 chunks

Chunk 1: 0.00s - 2.45s (2.45s)
  Text: 'Hello, this is the beginning of the video.'
  Length: 42 chars
  Type: segment

...

============================================================
EMBEDDING SIMILARITY ANALYSIS
============================================================
Primary chunks: 23
Secondary chunks: 15

Testing threshold: 0.5
  Chunk 1: 3 matches
    Match: 0.823 confidence
      Time: 0.00s - 2.45s
      Text: 'Hello, this is the beginning of the video.'
  Chunk 2: 1 match
    Match: 0.756 confidence
      Time: 2.45s - 5.12s
      Text: 'We will be discussing important topics today.'
  ...
  Total matches at threshold 0.5: 12

Testing threshold: 0.7
  Chunk 1: 2 matches
  Chunk 2: 1 match
  ...
  Total matches at threshold 0.7: 8

...

============================================================
MISSING CONTENT ANALYSIS
============================================================
Found 3 gaps in matches

Gap 1: 501.20s - 502.50s (duration: 1.30s)
  Segments in gap: 2
  Total text in gap: 156 characters
  Gap text: 'This is some content that was missed during the comparison process.'
  Average segment length: 78.0 characters
  Short segments (<50 chars): 0
  Low confidence segments (<50%): 0

...
```

## Key Areas to Investigate

### 1. **Gap Analysis**
Look for patterns in the missing regions:
- **Short segments**: Segments with <50 characters might be missed
- **Low confidence**: Segments with <50% confidence might be filtered out
- **Boundary issues**: Segments at chunk boundaries might be split incorrectly
- **Silence gaps**: Very short segments might represent silence or noise

### 2. **Threshold Analysis**
The `analyze_chunks.py` script tests multiple thresholds:
- **0.5**: Very permissive - should catch most matches
- **0.7**: Current default - balanced approach
- **0.9**: Very strict - only high-confidence matches
- **0.95**: Extremely strict - only near-perfect matches

### 3. **Chunking Analysis**
Check if the chunking process is:
- **Splitting segments correctly**: Long segments should be split
- **Preserving boundaries**: Segment boundaries should be maintained
- **Handling overlaps**: Overlapping chunks should be merged properly

### 4. **Embedding Issues**
Verify that:
- **Embeddings are generated**: All chunks should have embeddings
- **Similarity is calculated**: Vector similarity should work correctly
- **Pinecone is accessible**: Database operations should succeed

## Troubleshooting Common Issues

### Issue: No matches found
**Check**:
1. Are embeddings being generated? (Look for "Failed to generate batch embeddings")
2. Is Pinecone accessible? (Check API key and connection)
3. Is the threshold too high? (Try lower thresholds in analyze_chunks.py)

### Issue: Missing specific regions
**Check**:
1. Are the missing segments very short? (Look for "Short segments" in analysis)
2. Do they have low confidence? (Look for "Low confidence segments")
3. Are they at chunk boundaries? (Check chunk splitting logic)

### Issue: Inconsistent results
**Check**:
1. Are embeddings being cleared properly? (Look for "Clear embeddings result")
2. Is the same model being used? (Check model configuration)
3. Are file paths correct? (Verify file validation)

## Next Steps

After running these scripts:

1. **Review the log files** for any error messages or warnings
2. **Analyze the gaps** identified in the missing content analysis
3. **Test different thresholds** using the analyze_chunks.py script
4. **Check chunking configuration** if segments are being split incorrectly
5. **Verify Pinecone setup** if embeddings are not being stored/retrieved

The scripts will provide comprehensive information to help identify exactly why certain chunks are being missed in your comparison process. 