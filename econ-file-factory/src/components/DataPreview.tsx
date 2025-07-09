import React, { useEffect, useState } from 'react';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from '@/components/ui/table';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select';
import { Button } from '@/components/ui/button';
import { ArrowLeft, ArrowRight } from 'lucide-react';
import * as XLSX from 'xlsx';
import Papa from 'papaparse';
import { toast } from "@/hooks/use-toast";

interface DataPreviewProps {
  files: File[];
  onContinue: () => void;
  onBackToUpload: () => void;
  onGoToMapping: () => void;
  onWrangledDataReady: (data: any[], headers: string[]) => void;
}

interface ParsedFile {
  fileName: string;
  sheetNames: string[];
  activeSheet: string;
  headers: string[];
  rows: any[];
}

const DataPreview: React.FC<DataPreviewProps> = ({ files, onContinue, onBackToUpload, onGoToMapping, onWrangledDataReady }) => {
  const [parsedFiles, setParsedFiles] = useState<ParsedFile[]>([]);
  const [selectedFileIndex, setSelectedFileIndex] = useState(0);
  const [selectedSheet, setSelectedSheet] = useState<string | null>(null);

  useEffect(() => {
    const parseFiles = async () => {
      const fileObjs = await Promise.all(
        files.map(async (file) => {
          if (file.name.endsWith('.xlsx')) {
            const data = await file.arrayBuffer();
            const workbook = XLSX.read(data, { type: 'array' });
            const sheetNames = workbook.SheetNames;
            const activeSheet = sheetNames[0];
            const rows = XLSX.utils.sheet_to_json(workbook.Sheets[activeSheet]);
            return {
              fileName: file.name,
              sheetNames,
              activeSheet,
              headers: Object.keys(rows[0] || {}),
              rows: rows.slice(0, 10),
            };
          } else if (file.name.endsWith('.csv')) {
            const text = await file.text();
            const result = Papa.parse(text, { header: true });
            return {
              fileName: file.name,
              sheetNames: ['Sheet1'],
              activeSheet: 'Sheet1',
              headers: result.meta.fields || [],
              rows: (result.data as any[]).slice(0, 10),
            };
          }
          return null;
        })
      );
      setParsedFiles(fileObjs.filter(Boolean) as ParsedFile[]);
      setSelectedFileIndex(0);
      setSelectedSheet(fileObjs[0]?.sheetNames[0] || null);
    };
    if (files.length > 0) {
      parseFiles();
    }
  }, [files]);

  const currentFile = parsedFiles[selectedFileIndex];
  const currentSheet = selectedSheet || currentFile?.activeSheet;
  const sheetRows = React.useMemo(() => {
    if (!currentFile) return [];
    if (currentFile.sheetNames.length > 1 && currentSheet) {
      // re-parse the selected sheet for xlsx
      if (currentFile.fileName.endsWith('.xlsx')) {
        // Find the file in files
        const file = files[selectedFileIndex];
        return (async () => {
          const data = await file.arrayBuffer();
          const workbook = XLSX.read(data, { type: 'array' });
          const rows = XLSX.utils.sheet_to_json(workbook.Sheets[currentSheet]);
          return rows.slice(0, 10);
        })();
      }
    }
    return currentFile.rows;
  }, [currentFile, currentSheet, files, selectedFileIndex]);

  // Function to send files to backend and trigger download
  const handleSendFiles = async () => {
    if (!files || files.length === 0) return;
    const formData = new FormData();
    files.forEach((file) => {
      formData.append('files', file);
    });
    try {
      const response = await fetch('http://localhost:5000/upload', {
        method: 'POST',
        body: formData,
      });
      if (!response.ok) {
        toast({ title: 'Upload failed', description: 'Server error or invalid file(s).', variant: 'destructive' });
        return;
      }
      const text = await response.text();
      // Only use the first CSV part before any # Duplicate Records section
      const mainCsv = text.split('# Duplicate Records')[0].trim();
      // Parse CSV using PapaParse
      const result = Papa.parse(mainCsv, { header: true });
      const wrangledData = result.data as any[];
      const wrangledHeaders = result.meta.fields || [];
      onWrangledDataReady(wrangledData, wrangledHeaders);
      onGoToMapping();
    } catch (error) {
      toast({ title: 'Upload failed', description: 'Network error.', variant: 'destructive' });
    }
  };

  if (!currentFile) return null;

  return (
    <Card className="w-full mt-8">
      <CardHeader>
        <CardTitle>Data Preview</CardTitle>
        <CardDescription>
          Preview of the first 10 rows from your data files.
          {parsedFiles.length > 1 && ' Select a file to preview its data.'}
          {currentFile.sheetNames.length > 1 && ' Select a sheet to view its data.'}
        </CardDescription>
        <div className="flex gap-4 mt-2">
          {parsedFiles.length > 1 && (
            <div>
              <label className="text-sm font-medium mb-1 block">File:</label>
              <Select
                value={selectedFileIndex.toString()}
                onValueChange={value => {
                  const idx = parseInt(value);
                  setSelectedFileIndex(idx);
                  setSelectedSheet(parsedFiles[idx].activeSheet);
                }}
              >
                <SelectTrigger className="w-[200px]">
                  <SelectValue placeholder="Select file" />
                </SelectTrigger>
                <SelectContent>
                  {parsedFiles.map((file, index) => (
                    <SelectItem key={index} value={index.toString()}>
                      {file.fileName}
                    </SelectItem>
                  ))}
                </SelectContent>
              </Select>
            </div>
          )}
          {currentFile.sheetNames.length > 1 && (
            <div>
              <label className="text-sm font-medium mb-1 block">Sheet:</label>
              <Select
                value={currentSheet}
                onValueChange={value => setSelectedSheet(value)}
              >
                <SelectTrigger className="w-[180px]">
                  <SelectValue placeholder="Select sheet" />
                </SelectTrigger>
                <SelectContent>
                  {currentFile.sheetNames.map(sheet => (
                    <SelectItem key={sheet} value={sheet}>
                      {sheet}
                    </SelectItem>
                  ))}
                </SelectContent>
              </Select>
            </div>
          )}
        </div>
      </CardHeader>
      <CardContent>
        <div className="table-container rounded border">
          <Table>
            <TableHeader>
              <TableRow>
                {currentFile.headers.map(header => (
                  <TableHead key={header} className="font-medium">
                    {header}
                  </TableHead>
                ))}
              </TableRow>
            </TableHeader>
            <TableBody>
              {Array.isArray(sheetRows) && sheetRows.map((row, rowIndex) => (
                <TableRow key={rowIndex}>
                  {currentFile.headers.map(header => (
                    <TableCell key={`${rowIndex}-${header}`}>
                      {row[header] !== undefined ? String(row[header]) : ''}
                    </TableCell>
                  ))}
                </TableRow>
              ))}
            </TableBody>
          </Table>
        </div>
        <div className="flex justify-between mt-4">
          <Button onClick={onBackToUpload}>
            <ArrowLeft className="w-4 h-4 mr-2" />
            Back to Upload
          </Button>
          <Button onClick={handleSendFiles}>
            Mapping
            <ArrowRight className="w-4 h-4 ml-2" />
          </Button>
        </div>
       
      </CardContent>
    </Card>
  );
};

export default DataPreview;
