# Troubleshooting Guide

## Current Issue: Transcribe Button Not Accessible After File Upload

### 🔍 **Debug Steps**

#### 1. **Check API Server Status**
```bash
# Start the API server
python api_server.py

# Test API connection
python test_frontend_connection.py
```

#### 2. **Check Browser Console**
Open browser developer tools (F12) and look for:
- 🚀 File upload logs
- 📤 API request logs
- ❌ Error messages
- 🔍 State changes

#### 3. **Debug Panel**
A debug panel is now added to the bottom-left corner showing:
- 📁 Current file state
- 📤 Upload progress
- 🎯 Transcription status
- ❌ Error messages
- 📋 API configuration status

### 🔧 **Common Issues & Solutions**

#### **Issue 1: API Server Not Running**
**Symptoms:**
- Network errors in console
- "Cannot connect" messages
- Upload fails immediately

**Solution:**
```bash
# Start API server
python api_server.py

# Verify it's running
curl http://localhost:8000/health
```

#### **Issue 2: CORS Errors**
**Symptoms:**
- CORS errors in console
- "Access-Control-Allow-Origin" errors

**Solution:**
- Check CORS configuration in `api/middleware/cors.py`
- Ensure frontend is running on `http://localhost:3000`

#### **Issue 3: File Upload Fails**
**Symptoms:**
- Upload progress doesn't complete
- No file information displayed
- Transcribe button remains disabled

**Debug Steps:**
1. Check console for upload logs
2. Verify file format is supported
3. Check file size limits
4. Look for validation errors

#### **Issue 4: Transcribe Button Disabled**
**Symptoms:**
- Button shows as disabled
- No error messages visible

**Debug Steps:**
1. Check debug panel for file state
2. Look for console logs about file upload
3. Verify `uploadedFile` state is set
4. Check for API errors

### 📊 **Expected Console Logs**

#### **Successful File Upload:**
```
📂 File upload handler called with files: 1 files
📁 Selected file: {name: "audio.mp3", size: 1234567, type: "audio/mpeg"}
🔄 Calling uploadFile function...
🚀 Starting file upload: audio.mp3 1234567 bytes
📤 Uploading file to API...
🌐 API: Starting file upload to: http://localhost:8000/api/upload
📁 API: File details: {name: "audio.mp3", size: 1234567, type: "audio/mpeg"}
📤 API: Sending POST request to: http://localhost:8000/api/upload
📥 API: Response status: 200 OK
✅ API: Upload successful: {success: true, file_info: {...}}
📥 Upload response: {success: true, file_info: {...}}
✅ Upload successful, file info: {...}
📤 Upload result: true
🔍 ActionButtons - Current state: {uploadedFile: "File uploaded", ...}
```

#### **Successful Transcription:**
```
🎯 Transcribe button clicked
📁 Uploaded file state: {file_path: "...", original_name: "audio.mp3", ...}
⚙️ Selected model: base
🔄 Starting transcription...
🎯 Starting transcription with model: base language: auto
📁 Uploaded file: {file_path: "...", original_name: "audio.mp3", ...}
🔄 Calling transcription API...
📝 Transcription response: {success: true, text: "...", ...}
✅ Transcription successful: {success: true, text: "...", ...}
📝 Transcription result: true
```

### 🛠️ **Manual Testing Steps**

1. **Start Backend:**
   ```bash
   python api_server.py
   ```

2. **Start Frontend:**
   ```bash
   cd frontend
   npm run dev
   ```

3. **Test File Upload:**
   - Open browser to `http://localhost:3000`
   - Upload an audio file (MP3, WAV, etc.)
   - Check console logs
   - Verify debug panel shows file uploaded

4. **Test Transcription:**
   - Click "Transcribe" button
   - Check console logs
   - Verify progress indicator appears
   - Check transcription results

### 🔍 **Debug Panel Information**

The debug panel shows:
- **📁 File**: Current uploaded file name or "None"
- **📤 Uploading**: Upload progress percentage or "No"
- **🎯 Transcribing**: Transcription progress percentage or "No"
- **📝 Has Transcription**: "Yes" or "No"
- **❌ Error**: Current error message or "None"
- **📋 Formats**: "Loaded" or "Not loaded"
- **⚙️ Models**: "Loaded" or "Not loaded"

### 🚨 **Critical Checks**

1. **API Server Running**: `http://localhost:8000/health` should return `{"status": "healthy"}`

2. **CORS Working**: No CORS errors in browser console

3. **File Upload Success**: Console shows "✅ Upload successful"

4. **State Management**: Debug panel shows file uploaded

5. **Button State**: Transcribe button should be enabled when file is uploaded

### 📞 **If Issues Persist**

1. Check browser console for detailed error messages
2. Verify API server is running and accessible
3. Test with a simple audio file (MP3, WAV)
4. Check file size (should be under 500MB)
5. Look for network errors in browser Network tab

### 🎯 **Expected Behavior**

1. **File Upload**: Progress bar → Success message → File info displayed
2. **Transcribe Button**: Disabled → Enabled (after file upload)
3. **Transcription**: Progress bar → Results displayed
4. **Download**: Multiple format buttons appear after transcription 