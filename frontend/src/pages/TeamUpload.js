import React, { useState } from 'react';
import { useDropzone } from 'react-dropzone';
import { Upload, Users, FileText, AlertCircle, CheckCircle } from 'lucide-react';
import toast from 'react-hot-toast';

const TeamUpload = () => {
  const [uploadedFile, setUploadedFile] = useState(null);
  const [uploadStatus, setUploadStatus] = useState('idle');
  const [teamData, setTeamData] = useState([]);
  const [fileType, setFileType] = useState('csv');

  const onDrop = (acceptedFiles) => {
    const file = acceptedFiles[0];
    if (file) {
      setUploadedFile(file);
      setUploadStatus('uploaded');
      toast.success(`File "${file.name}" uploaded successfully`);
    }
  };

  const { getRootProps, getInputProps, isDragActive } = useDropzone({
    onDrop,
    accept: {
      'text/csv': ['.csv'],
      'application/json': ['.json']
    },
    multiple: false
  });

  const handleUpload = async () => {
    if (!uploadedFile) {
      toast.error('Please select a file first');
      return;
    }

    setUploadStatus('uploading');
    
    try {
      const formData = new FormData();
      formData.append('file', uploadedFile);
      formData.append('file_type', fileType);

      const response = await fetch('/api/v1/ingest/team/file', {
        method: 'POST',
        body: formData,
      });

      if (response.ok) {
        const result = await response.json();
        setUploadStatus('success');
        setTeamData(result);
        toast.success(`Team data uploaded successfully! ${result.team_size} members processed.`);
      } else {
        const error = await response.json();
        setUploadStatus('error');
        toast.error(error.detail || 'Upload failed');
      }
    } catch (error) {
      setUploadStatus('error');
      toast.error('Upload failed: ' + error.message);
    }
  };

  const getStatusIcon = () => {
    switch (uploadStatus) {
      case 'success':
        return <CheckCircle className="w-6 h-6 text-green-500" />;
      case 'error':
        return <AlertCircle className="w-6 h-6 text-red-500" />;
      case 'uploading':
        return <div className="spinner"></div>;
      default:
        return <Upload className="w-6 h-6 text-gray-400" />;
    }
  };

  const getStatusText = () => {
    switch (uploadStatus) {
      case 'success':
        return 'Upload successful';
      case 'error':
        return 'Upload failed';
      case 'uploading':
        return 'Uploading...';
      case 'uploaded':
        return 'File ready to upload';
      default:
        return 'No file selected';
    }
  };

  return (
    <div className="max-w-4xl mx-auto space-y-8">
      {/* Header */}
      <div className="text-center">
        <h1 className="text-3xl font-bold text-gray-900 mb-4">
          Team Data Upload
        </h1>
        <p className="text-lg text-gray-600">
          Upload your team member data to get personalized skill recommendations
        </p>
      </div>

      {/* File Upload Section */}
      <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-8">
        <h2 className="text-xl font-semibold text-gray-900 mb-6">
          Upload Team Data
        </h2>

        {/* File Type Selection */}
        <div className="mb-6">
          <label className="block text-sm font-medium text-gray-700 mb-2">
            File Type
          </label>
          <div className="flex space-x-4">
            <label className="flex items-center">
              <input
                type="radio"
                name="fileType"
                value="csv"
                checked={fileType === 'csv'}
                onChange={(e) => setFileType(e.target.value)}
                className="mr-2"
              />
              <span className="text-sm text-gray-700">CSV</span>
            </label>
            <label className="flex items-center">
              <input
                type="radio"
                name="fileType"
                value="json"
                checked={fileType === 'json'}
                onChange={(e) => setFileType(e.target.value)}
                className="mr-2"
              />
              <span className="text-sm text-gray-700">JSON</span>
            </label>
          </div>
        </div>

        {/* Dropzone */}
        <div
          {...getRootProps()}
          className={`border-2 border-dashed rounded-lg p-8 text-center cursor-pointer transition-colors ${
            isDragActive
              ? 'border-blue-400 bg-blue-50'
              : 'border-gray-300 hover:border-gray-400'
          }`}
        >
          <input {...getInputProps()} />
          <Upload className="w-12 h-12 text-gray-400 mx-auto mb-4" />
          {isDragActive ? (
            <p className="text-lg text-blue-600">Drop the file here...</p>
          ) : (
            <div>
              <p className="text-lg text-gray-600 mb-2">
                Drag & drop a file here, or click to select
              </p>
              <p className="text-sm text-gray-500">
                Supports CSV and JSON files
              </p>
            </div>
          )}
        </div>

        {/* File Info */}
        {uploadedFile && (
          <div className="mt-4 p-4 bg-gray-50 rounded-lg">
            <div className="flex items-center justify-between">
              <div className="flex items-center space-x-3">
                <FileText className="w-5 h-5 text-gray-500" />
                <div>
                  <p className="text-sm font-medium text-gray-900">
                    {uploadedFile.name}
                  </p>
                  <p className="text-sm text-gray-500">
                    {(uploadedFile.size / 1024).toFixed(1)} KB
                  </p>
                </div>
              </div>
              <div className="flex items-center space-x-2">
                {getStatusIcon()}
                <span className="text-sm text-gray-600">
                  {getStatusText()}
                </span>
              </div>
            </div>
          </div>
        )}

        {/* Upload Button */}
        <div className="mt-6">
          <button
            onClick={handleUpload}
            disabled={!uploadedFile || uploadStatus === 'uploading'}
            className={`w-full py-3 px-4 rounded-lg font-medium transition-colors ${
              uploadedFile && uploadStatus !== 'uploading'
                ? 'bg-blue-600 text-white hover:bg-blue-700'
                : 'bg-gray-300 text-gray-500 cursor-not-allowed'
            }`}
          >
            {uploadStatus === 'uploading' ? 'Uploading...' : 'Upload Team Data'}
          </button>
        </div>
      </div>

      {/* File Format Guide */}
      <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
        <h3 className="text-lg font-semibold text-gray-900 mb-4">
          File Format Requirements
        </h3>
        
        <div className="grid md:grid-cols-2 gap-6">
          {/* CSV Format */}
          <div>
            <h4 className="font-medium text-gray-900 mb-2">CSV Format</h4>
            <div className="bg-gray-50 p-3 rounded text-sm font-mono">
              name,role,level,skills,years_experience<br/>
              John Doe,Data Engineer,Senior,"Python,SQL,Airflow",5<br/>
              Jane Smith,Software Engineer,Mid,"JavaScript,React,Node.js",3
            </div>
          </div>

          {/* JSON Format */}
          <div>
            <h4 className="font-medium text-gray-900 mb-2">JSON Format</h4>
            <div className="bg-gray-50 p-3 rounded text-sm font-mono">
              [<br/>
              &nbsp;&nbsp;{'{'}<br/>
              &nbsp;&nbsp;&nbsp;&nbsp;"name": "John Doe",<br/>
              &nbsp;&nbsp;&nbsp;&nbsp;"role": "Data Engineer",<br/>
              &nbsp;&nbsp;&nbsp;&nbsp;"level": "Senior",<br/>
              &nbsp;&nbsp;&nbsp;&nbsp;"skills": ["Python", "SQL", "Airflow"],<br/>
              &nbsp;&nbsp;&nbsp;&nbsp;"years_experience": 5<br/>
              &nbsp;&nbsp;{'}'}<br/>
              ]
            </div>
          </div>
        </div>

        <div className="mt-4 p-4 bg-blue-50 rounded-lg">
          <h4 className="font-medium text-blue-900 mb-2">Required Fields</h4>
          <ul className="text-sm text-blue-800 space-y-1">
            <li>• <strong>name</strong>: Team member's full name</li>
            <li>• <strong>role</strong>: Current job role/title</li>
            <li>• <strong>level</strong>: Experience level (Junior, Mid, Senior, Lead)</li>
            <li>• <strong>skills</strong>: List of current skills (comma-separated for CSV, array for JSON)</li>
            <li>• <strong>years_experience</strong>: Years of experience (optional)</li>
          </ul>
        </div>
      </div>

      {/* Upload Results */}
      {teamData && teamData.team_size > 0 && (
        <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
          <h3 className="text-lg font-semibold text-gray-900 mb-4">
            Upload Results
          </h3>
          
          <div className="grid md:grid-cols-3 gap-4">
            <div className="text-center p-4 bg-green-50 rounded-lg">
              <Users className="w-8 h-8 text-green-600 mx-auto mb-2" />
              <p className="text-2xl font-bold text-green-900">
                {teamData.team_size}
              </p>
              <p className="text-sm text-green-700">Team Members</p>
            </div>
            
            <div className="text-center p-4 bg-blue-50 rounded-lg">
              <FileText className="w-8 h-8 text-blue-600 mx-auto mb-2" />
              <p className="text-2xl font-bold text-blue-900">
                {teamData.roles_found?.length || 0}
              </p>
              <p className="text-sm text-blue-700">Unique Roles</p>
            </div>
            
            <div className="text-center p-4 bg-purple-50 rounded-lg">
              <CheckCircle className="w-8 h-8 text-purple-600 mx-auto mb-2" />
              <p className="text-2xl font-bold text-purple-900">
                Success
              </p>
              <p className="text-sm text-purple-700">Upload Complete</p>
            </div>
          </div>

          {teamData.roles_found && teamData.roles_found.length > 0 && (
            <div className="mt-4">
              <h4 className="font-medium text-gray-900 mb-2">Roles Found:</h4>
              <div className="flex flex-wrap gap-2">
                {teamData.roles_found.map((role, index) => (
                  <span
                    key={index}
                    className="inline-flex items-center px-3 py-1 rounded-full text-sm font-medium bg-gray-100 text-gray-800"
                  >
                    {role}
                  </span>
                ))}
              </div>
            </div>
          )}
        </div>
      )}
    </div>
  );
};

export default TeamUpload; 