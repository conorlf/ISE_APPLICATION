import React, { useState, useCallback } from 'react';
import { FileSpreadsheet, Upload } from 'lucide-react';
import { Button } from '@/components/ui/button';

interface FileUploaderProps {
  onFilesSelected: (files: File[]) => void;
}

const FileUploader = ({ onFilesSelected }: FileUploaderProps) => {
  const [dragActive, setDragActive] = useState(false);
  const [selectedFiles, setSelectedFiles] = useState<File[]>([]);

  const handleFiles = (files: FileList | File[]) => {
    const fileArr = Array.from(files);
    setSelectedFiles(fileArr);
    onFilesSelected(fileArr);
  };

  const handleDrag = useCallback((e: React.DragEvent) => {
    e.preventDefault();
    e.stopPropagation();
    if (e.type === 'dragenter' || e.type === 'dragover') {
      setDragActive(true);
    } else if (e.type === 'dragleave') {
      setDragActive(false);
    }
  }, []);

  const handleDrop = useCallback((e: React.DragEvent) => {
    e.preventDefault();
    e.stopPropagation();
    setDragActive(false);
    if (e.dataTransfer.files && e.dataTransfer.files.length > 0) {
      handleFiles(e.dataTransfer.files);
    }
  }, [handleFiles]);

  const handleChange = useCallback((e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files && e.target.files.length > 0) {
      handleFiles(e.target.files);
    }
  }, [handleFiles]);

  console.log("Selected files:", selectedFiles);

  return (
    <div className="space-y-6">
      <div className="flex flex-col items-center">
        <h2 className="text-2xl font-bold mb-4">Upload Your Data File</h2>
        <p className="text-gray-500 mb-6 text-center">
          Upload Excel files (.xlsx) or CSV files(.csv) containing your economic data for analysis
        </p>
      </div>
      <div
        className={`border-2 border-dashed rounded-lg p-10 text-center transition-all cursor-pointer ${
          dragActive ? 'border-primary bg-primary/5' : 'border-gray-300'
        }`}
        onDragEnter={handleDrag}
        onDragLeave={handleDrag}
        onDragOver={handleDrag}
        onDrop={handleDrop}
        onClick={() => document.getElementById('file-upload')?.click()}
      >
        <input
          id="file-upload"
          type="file"
          className="hidden"
          onChange={handleChange}
          accept=".xlsx,.csv"
          multiple
        />
        <div className="flex flex-col items-center justify-center space-y-4">
          {selectedFiles.length > 0 ? (
            <>
              <FileSpreadsheet className="h-12 w-12 text-primary" />
              <div>
                <p className="font-medium text-lg text-foreground">
                  {selectedFiles.map(file => file.name).join(', ')}
                </p>
                <p className="text-sm text-muted-foreground">
                  {(selectedFiles.reduce((total, file) => total + file.size, 0) / 1024 / 1024).toFixed(2)} MB
                </p>
              </div>
              <Button
                variant="outline"
                onClick={e => {
                  e.stopPropagation();
                  document.getElementById('file-upload')?.click();
                }}
              >
                Change File(s)
              </Button>
            </>
          ) : (
            <>
              <div className="rounded-full bg-primary/10 p-4">
                <Upload className="h-8 w-8 text-primary" />
              </div>
              <div className="space-y-2">
                <p className="text-lg font-medium">
                  Drag and drop your Excel or CSV file(s) here
                </p>
                <p className="text-sm text-gray-500">or</p>
                <label
                  htmlFor="file-upload"
                  className="cursor-pointer text-sm text-primary hover:text-primary/90 transition-colors"
                >
                  Browse files
                </label>
              </div>
              <p className="text-xs text-gray-500 max-w-xs">
                Supports .xlsx or .csv Excel files
              </p>
            </>
          )}
        </div>
      </div>
    </div>
  );
};

export default FileUploader;