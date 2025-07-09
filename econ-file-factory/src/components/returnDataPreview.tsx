import React from 'react';
import { Table, TableHeader, TableRow, TableHead, TableBody, TableCell } from "@/components/ui/table";

interface DataPreviewProps {
  headers: string[];
  data: any[];
}

const ReturnDataPreview = ({ headers, data }: DataPreviewProps) => {
  if (!headers.length || !data.length) {
    return null;
  }

  return (
    <div className="space-y-4 mb-8">
      <div>
        <h2 className="text-2xl font-bold mb-2">Data Preview</h2>
        <p className="text-gray-500 mb-4">
          Preview of the first 5 rows of your Cleaned Data
        </p>
      </div>
      
      <div className="border rounded-lg overflow-x-auto">
        <Table>
          <TableHeader>
            <TableRow>
              {headers.map((header, index) => (
                <TableHead key={index} className="whitespace-nowrap">
                  {header}
                </TableHead>
              ))}
            </TableRow>
          </TableHeader>
          <TableBody>
            {data.slice(0, 5).map((row, rowIndex) => (
              <TableRow key={rowIndex}>
                {headers.map((header, colIndex) => (
                  <TableCell key={colIndex} className="whitespace-nowrap">
                    {row[header] !== undefined ? String(row[header]) : "-"}
                  </TableCell>
                ))}
              </TableRow>
            ))}
          </TableBody>
        </Table>
      </div>
    </div>
  );
};

export default ReturnDataPreview;